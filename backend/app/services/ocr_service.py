import logging
import re
from typing import Any

from PIL import Image

logger = logging.getLogger(__name__)


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

    def extract_from_screenshot(self, image_path: str) -> dict:
        """Extract profile data from a screenshot using OCR."""
        try:
            import pytesseract
        except ImportError:
            logger.error("pytesseract is not installed")
            raise RuntimeError("pytesseract is required for OCR")

        try:
            image = Image.open(image_path)

            # Run OCR
            raw_text = pytesseract.image_to_string(image)
            logger.info(f"OCR raw text: {raw_text[:500]}")

            result = {
                "raw_text": raw_text,
                "followers": None,
                "following": None,
                "posts": None,
                "likes": None,
                "username": None,
                "platform": None,
            }

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
                # Try reversed order: followers first
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

            # TikTok patterns: "123 Following  456 Followers  789 Likes"
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

            # Fallback: try to find individual numbers with labels
            if result["followers"] is None:
                follower_match = re.search(
                    r"([\d,.]+[KkMmBb]?)\s*(?:followers?|abonn[eé]s?)",
                    raw_text,
                    re.IGNORECASE,
                )
                if follower_match:
                    result["followers"] = self._parse_count(follower_match.group(1))

            if result["following"] is None:
                following_match = re.search(
                    r"([\d,.]+[KkMmBb]?)\s*(?:following|abonnements?|suivi)",
                    raw_text,
                    re.IGNORECASE,
                )
                if following_match:
                    result["following"] = self._parse_count(following_match.group(1))

            if result["posts"] is None:
                posts_match = re.search(
                    r"([\d,.]+[KkMmBb]?)\s*(?:posts?|publications?|videos?)",
                    raw_text,
                    re.IGNORECASE,
                )
                if posts_match:
                    result["posts"] = self._parse_count(posts_match.group(1))

            if result["likes"] is None:
                likes_match = re.search(
                    r"([\d,.]+[KkMmBb]?)\s*(?:likes?|j'aime)",
                    raw_text,
                    re.IGNORECASE,
                )
                if likes_match:
                    result["likes"] = self._parse_count(likes_match.group(1))

            return result

        except FileNotFoundError:
            raise FileNotFoundError(f"Image not found: {image_path}")
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            raise RuntimeError(f"OCR processing failed: {e}")
