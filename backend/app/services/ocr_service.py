import base64
import json
import logging
import re
from typing import Any, Optional

import httpx
from PIL import Image

from app.core.config import settings

logger = logging.getLogger(__name__)

VISION_PROMPT = """Extract all social media profile data from this screenshot.
Return ONLY valid JSON (no markdown, no code fences) with these fields:
{
  "username": "string or null",
  "platform": "instagram|tiktok|youtube|twitter|null",
  "followers": integer or null,
  "following": integer or null,
  "posts": integer or null,
  "likes": integer or null
}
Parse abbreviated numbers: 1.5K = 1500, 2M = 2000000, 3.2B = 3200000000.
If a field is not visible in the screenshot, set it to null."""

VISION_SYSTEM = "You are an OCR extraction assistant. You only output valid JSON, nothing else."


class OCRService:
    @staticmethod
    def _parse_count(text: str) -> int:
        """Parse abbreviated counts like 1.5K, 2M, 12.3k, etc."""
        text = text.strip().replace(",", "").replace(" ", "")
        multipliers = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}
        lower = text.lower()
        for suffix, mult in multipliers.items():
            if lower.endswith(suffix):
                try:
                    return int(float(lower[:-1]) * mult)
                except ValueError:
                    return 0
        try:
            return int(float(text))
        except ValueError:
            return 0

    @staticmethod
    def _image_to_base64(image_path: str) -> tuple[str, str]:
        """Read image file and return (base64_data, media_type)."""
        ext = image_path.lower().rsplit(".", 1)[-1]
        media_map = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp",
        }
        media_type = media_map.get(ext, "image/png")
        with open(image_path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")
        return data, media_type

    async def _try_mistral_vision(self, image_path: str) -> Optional[dict]:
        """Try Mistral Vision API (pixtral-large-latest) for OCR."""
        api_key = settings.MISTRAL_API_KEY
        if not api_key:
            logger.info("MISTRAL_API_KEY not configured, skipping Mistral Vision")
            return None

        try:
            b64_data, media_type = self._image_to_base64(image_path)
            data_url = f"data:{media_type};base64,{b64_data}"

            payload = {
                "model": "pixtral-large-latest",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": data_url},
                            },
                            {
                                "type": "text",
                                "text": VISION_PROMPT,
                            },
                        ],
                    }
                ],
                "max_tokens": 512,
                "temperature": 0,
            }

            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                resp.raise_for_status()
                body = resp.json()

            raw = body["choices"][0]["message"]["content"].strip()
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = re.sub(r"^```(?:json)?\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)

            parsed = json.loads(raw)
            logger.info(f"Mistral Vision result: {parsed}")
            return {
                "raw_text": f"[Mistral Vision] {raw}",
                "username": parsed.get("username"),
                "platform": parsed.get("platform"),
                "followers": parsed.get("followers"),
                "following": parsed.get("following"),
                "posts": parsed.get("posts"),
                "likes": parsed.get("likes"),
            }

        except Exception as e:
            logger.warning(f"Mistral Vision failed: {e}")
            return None

    async def _try_vps_proxy(self, image_path: str) -> Optional[dict]:
        """Try VPS Claude proxy with base64 image in prompt."""
        proxy_url = settings.VPS_PROXY_URL
        proxy_token = settings.VPS_PROXY_TOKEN
        if not proxy_url or not proxy_token:
            logger.info("VPS proxy not configured, skipping")
            return None

        try:
            b64_data, media_type = self._image_to_base64(image_path)

            # The proxy accepts prompt + system_prompt fields
            payload = {
                "prompt": (
                    f"[Image attached as base64 {media_type}]\n"
                    f"data:{media_type};base64,{b64_data}\n\n"
                    f"{VISION_PROMPT}"
                ),
                "system_prompt": VISION_SYSTEM,
            }

            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    proxy_url,
                    headers={
                        "Authorization": f"Bearer {proxy_token}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                resp.raise_for_status()
                body = resp.json()

            # Try to extract JSON from proxy response
            raw = ""
            if isinstance(body, dict):
                raw = body.get("response", body.get("content", body.get("text", str(body))))
            else:
                raw = str(body)

            raw = raw.strip()
            if raw.startswith("```"):
                raw = re.sub(r"^```(?:json)?\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)

            parsed = json.loads(raw)
            logger.info(f"VPS proxy result: {parsed}")
            return {
                "raw_text": f"[VPS Proxy] {raw}",
                "username": parsed.get("username"),
                "platform": parsed.get("platform"),
                "followers": parsed.get("followers"),
                "following": parsed.get("following"),
                "posts": parsed.get("posts"),
                "likes": parsed.get("likes"),
            }

        except Exception as e:
            logger.warning(f"VPS proxy OCR failed: {e}")
            return None

    def _regex_fallback(self, image_path: str) -> dict:
        """Fallback: use Pillow to open the image and attempt regex on any embedded text.
        This also serves as the Tesseract fallback if pytesseract is available."""
        raw_text = ""

        # Try pytesseract if available
        try:
            import pytesseract

            image = Image.open(image_path)
            raw_text = pytesseract.image_to_string(image)
            logger.info(f"Tesseract fallback raw text: {raw_text[:500]}")
        except ImportError:
            logger.info("pytesseract not available, regex fallback will have empty text")
        except Exception as e:
            logger.warning(f"Tesseract fallback failed: {e}")

        result: dict[str, Any] = {
            "raw_text": raw_text,
            "followers": None,
            "following": None,
            "posts": None,
            "likes": None,
            "username": None,
            "platform": None,
        }

        if not raw_text:
            return result

        # Detect platform
        text_lower = raw_text.lower()
        if "tiktok" in text_lower or "videos" in text_lower:
            result["platform"] = "tiktok"
        elif "instagram" in text_lower or "reels" in text_lower or "posts" in text_lower:
            result["platform"] = "instagram"

        # Extract username (@ pattern)
        username_match = re.search(r"@([\w.]+)", raw_text)
        if username_match:
            result["username"] = username_match.group(1)

        # Instagram patterns: "123 posts  456 followers  789 following"
        ig_pattern = re.search(
            r"([\d,.]+[KkMmBb]?)\s*(?:posts?|publications?)"
            r".*?([\d,.]+[KkMmBb]?)\s*(?:followers?|abonn[eé]s?)"
            r".*?([\d,.]+[KkMmBb]?)\s*(?:following|abonnements?|suivi)",
            raw_text,
            re.IGNORECASE | re.DOTALL,
        )
        if ig_pattern:
            result["posts"] = self._parse_count(ig_pattern.group(1))
            result["followers"] = self._parse_count(ig_pattern.group(2))
            result["following"] = self._parse_count(ig_pattern.group(3))
            if not result["platform"]:
                result["platform"] = "instagram"
        else:
            ig_alt = re.search(
                r"([\d,.]+[KkMmBb]?)\s*(?:followers?|abonn[eé]s?)"
                r".*?([\d,.]+[KkMmBb]?)\s*(?:following|abonnements?|suivi)"
                r".*?([\d,.]+[KkMmBb]?)\s*(?:posts?|publications?)",
                raw_text,
                re.IGNORECASE | re.DOTALL,
            )
            if ig_alt:
                result["followers"] = self._parse_count(ig_alt.group(1))
                result["following"] = self._parse_count(ig_alt.group(2))
                result["posts"] = self._parse_count(ig_alt.group(3))

        # TikTok patterns
        tt_pattern = re.search(
            r"([\d,.]+[KkMmBb]?)\s*(?:following|abonnements?)"
            r".*?([\d,.]+[KkMmBb]?)\s*(?:followers?|abonn[eé]s?)"
            r".*?([\d,.]+[KkMmBb]?)\s*(?:likes?|j'aime)",
            raw_text,
            re.IGNORECASE | re.DOTALL,
        )
        if tt_pattern:
            result["following"] = self._parse_count(tt_pattern.group(1))
            result["followers"] = self._parse_count(tt_pattern.group(2))
            result["likes"] = self._parse_count(tt_pattern.group(3))
            if not result["platform"]:
                result["platform"] = "tiktok"

        # TikTok split-line format: "418 21M 48,6 M\nSuivis Followers J'aime"
        # Numbers on one line, labels on next line
        if result["followers"] is None:
            split_tt = re.search(
                r"([\d,.\s]+[KkMmBb]?)\s+([\d,.\s]+[KkMmBb]?)\s+([\d,.\s]+[KkMmBb]?)\s*\n\s*(?:suivi|abonn|following).*?(?:followers?|abonn).*?(?:j.aime|likes?)",
                raw_text, re.IGNORECASE | re.DOTALL,
            )
            if split_tt:
                result["following"] = self._parse_count(split_tt.group(1).strip())
                result["followers"] = self._parse_count(split_tt.group(2).strip())
                result["likes"] = self._parse_count(split_tt.group(3).strip())
                if not result["platform"]:
                    result["platform"] = "tiktok"

        # Individual field fallbacks (label before or after number)
        if result["followers"] is None:
            m = re.search(r"([\d,.]+\s*[KkMmBb]?)\s*(?:followers?|abonn[eé]s?)", raw_text, re.IGNORECASE)
            if not m:
                m = re.search(r"(?:followers?|abonn[eé]s?)\s*[:\s]*([\d,.]+\s*[KkMmBb]?)", raw_text, re.IGNORECASE)
            if m:
                result["followers"] = self._parse_count(m.group(1))

        if result["following"] is None:
            m = re.search(r"([\d,.]+\s*[KkMmBb]?)\s*(?:following|abonnements?|suivi[es]?)", raw_text, re.IGNORECASE)
            if not m:
                m = re.search(r"(?:following|abonnements?|suivi[es]?)\s*[:\s]*([\d,.]+\s*[KkMmBb]?)", raw_text, re.IGNORECASE)
            if m:
                result["following"] = self._parse_count(m.group(1))

        if result["posts"] is None:
            m = re.search(r"([\d,.]+\s*[KkMmBb]?)\s*(?:posts?|publications?|vid[eé]os?)", raw_text, re.IGNORECASE)
            if m:
                result["posts"] = self._parse_count(m.group(1))

        if result["likes"] is None:
            m = re.search(r"([\d,.]+\s*[KkMmBb]?)\s*(?:likes?|j.aime)", raw_text, re.IGNORECASE)
            if m:
                result["likes"] = self._parse_count(m.group(1))

        # Detect TikTok from "Suivis/Followers/J'aime" pattern
        if not result["platform"] and "j'aime" in text_lower and "suivi" in text_lower:
            result["platform"] = "tiktok"

        return result

    async def extract_from_screenshot(self, image_path: str) -> dict:
        """Extract profile data from a screenshot.

        Strategy (in order):
        1. Mistral Vision API (pixtral-large-latest) - best accuracy
        2. VPS Claude proxy - if Mistral unavailable
        3. Tesseract + regex fallback - offline baseline
        """
        # Verify file exists
        try:
            Image.open(image_path).verify()
        except FileNotFoundError:
            raise FileNotFoundError(f"Image not found: {image_path}")
        except Exception as e:
            logger.warning(f"Image verification warning: {e}")

        # 1. Try Mistral Vision
        result = await self._try_mistral_vision(image_path)
        if result and any(result.get(k) is not None for k in ("followers", "following", "posts", "likes", "username")):
            return result

        # 2. Try VPS proxy
        result = await self._try_vps_proxy(image_path)
        if result and any(result.get(k) is not None for k in ("followers", "following", "posts", "likes", "username")):
            return result

        # 3. Regex fallback (with optional Tesseract)
        logger.info("Using regex/Tesseract fallback for OCR")
        return self._regex_fallback(image_path)
