from __future__ import annotations

import asyncio
<<<<<<< HEAD
import logging
from app.services.engagement_calculator import EngagementCalculator, build_posts_from_tiktok, PostMetrics

try:
    from app.core.proxy import PROXY_URL
except ImportError:
    PROXY_URL = None
from typing import Any

from TikTokApi import TikTokApi

logger = logging.getLogger(__name__)


class TikTokScraper:
    """TikTok scraper using the TikTok-Api library (Playwright-based)."""

    async def scrape_profile(self, username: str) -> dict:
        """Scrape public TikTok profile data."""
        try:
            async with TikTokApi() as api:
                await api.create_sessions(
                    num_sessions=1,
                    sleep_after=3,
                    headless=True,
                    suppress_resource_load_types=["image", "font", "stylesheet"],
                )
                user = api.user(username)
                user_info = await user.info()

                user_data = user_info.get("user", user_info.get("userInfo", {}).get("user", {}))
                stats = user_info.get("stats", user_info.get("userInfo", {}).get("stats", {}))

                return {
                    "username": user_data.get("uniqueId", username),
                    "full_name": user_data.get("nickname", ""),
                    "bio": user_data.get("signature", ""),
                    "profile_pic_url": user_data.get("avatarLarger", user_data.get("avatarMedium", "")),
                    "followers_count": stats.get("followerCount", 0),
                    "following_count": stats.get("followingCount", 0),
                    "posts_count": stats.get("videoCount", 0),
                    "is_verified": user_data.get("verified", False),
                    "total_likes": stats.get("heartCount", stats.get("heart", 0)),
                    "platform": "tiktok",
                }
        except Exception as e:
            logger.warning(f"TikTok-Api failed for {username}: {e}, falling back to HTTP")
            return await self._fallback_scrape(username)

    async def _fallback_scrape(self, username: str) -> dict:
        """Fallback HTTP scraper if TikTok-Api fails."""
        import json
        import re
        import httpx
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        url = f"https://www.tiktok.com/@{username}"
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0, proxy=PROXY_URL) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
=======
import json
import logging
import random
import re
from typing import Any

try:
    from app.core.proxy import PROXY_URL
except ImportError:
    PROXY_URL = None

import httpx

from app.services.engagement_calculator import EngagementCalculator, build_posts_from_tiktok, PostMetrics

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
]


class TikTokScraper:
    """TikTok scraper — HTTP with proxy, parsing __UNIVERSAL_DATA_FOR_REHYDRATION__."""

    def _get_headers(self) -> dict:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def scrape_profile(self, username: str) -> dict:
        """Scrape TikTok profile via HTTP + __UNIVERSAL_DATA_FOR_REHYDRATION__."""
        url = f"https://www.tiktok.com/@{username}"
        headers = self._get_headers()
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)

        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            proxy=PROXY_URL,
        ) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

<<<<<<< HEAD
            for script in soup.find_all("script", id=re.compile(r"__UNIVERSAL_DATA|SIGI_STATE|__NEXT_DATA__")):
                try:
                    data = json.loads(script.string or "{}")
                    result = self._find_user_info(data, username)
                    if result:
                        return result
                except (json.JSONDecodeError, TypeError):
                    continue

            # Fallback meta tags
            description_meta = soup.find("meta", attrs={"name": "description"})
            description = description_meta.get("content", "") if description_meta else ""
            followers = self._parse_count(m.group(1)) if (m := re.search(r"([\d,.]+[KkMmBb]?)\s*Followers", description, re.IGNORECASE)) else 0
            following = self._parse_count(m.group(1)) if (m := re.search(r"([\d,.]+[KkMmBb]?)\s*Following", description, re.IGNORECASE)) else 0
            likes = self._parse_count(m.group(1)) if (m := re.search(r"([\d,.]+[KkMmBb]?)\s*Likes", description, re.IGNORECASE)) else 0

            return {
                "username": username, "full_name": "", "bio": description,
                "profile_pic_url": "", "followers_count": followers,
                "following_count": following, "posts_count": 0,
                "is_verified": False, "total_likes": likes, "platform": "tiktok",
            }
        except Exception as e:
            logger.error(f"Fallback scrape failed for {username}: {e}")
            raise ValueError(f"Cannot scrape TikTok profile '{username}': {e}")

    def _find_user_info(self, data: dict, username: str) -> dict | None:
        if isinstance(data, dict):
            for key in ("userInfo", "UserModule", "user"):
=======
        html = response.text

        # Primary: parse __UNIVERSAL_DATA_FOR_REHYDRATION__
        m = re.search(
            r"<script\s+id=[\x22\x27]?__UNIVERSAL_DATA_FOR_REHYDRATION__[\x22\x27]?[^>]*>(.*?)</script>",
            html, re.DOTALL
        )
        if m:
            try:
                data = json.loads(m.group(1))
                default_scope = data.get("__DEFAULT_SCOPE__", {})
                user_detail = default_scope.get("webapp.user-detail", {})
                # Check if user exists (statusCode 10221 = not found)
                status_code = user_detail.get("statusCode", 0)
                if status_code != 0:
                    raise ValueError(f"TikTok user '{username}' not found (status: {status_code})")
                user_info = user_detail.get("userInfo", {})
                user = user_info.get("user", {})
                stats = user_info.get("stats", {})

                if user.get("uniqueId"):
                    followers = stats.get("followerCount", 0)
                    heart = stats.get("heartCount", stats.get("heart", 0))
                    # Fix negative heartCount (int32 overflow from TikTok)
                    if heart < 0:
                        heart = abs(heart)

                    return {
                        "username": user.get("uniqueId", username),
                        "full_name": user.get("nickname", ""),
                        "bio": user.get("signature", ""),
                        "profile_pic_url": user.get("avatarLarger", user.get("avatarMedium", "")),
                        "followers_count": followers,
                        "following_count": stats.get("followingCount", 0),
                        "posts_count": stats.get("videoCount", 0),
                        "is_verified": user.get("verified", False),
                        "total_likes": heart,
                        "platform": "tiktok",
                    }
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"UNIVERSAL_DATA parse error: {e}")

        # Fallback: try SIGI_STATE or __NEXT_DATA__
        for pattern in [
            r"<script\s+id=[\x22\x27]?SIGI_STATE[\x22\x27]?[^>]*>(.*?)</script>",
            r"<script\s+id=[\x22\x27]?__NEXT_DATA__[\x22\x27]?[^>]*>(.*?)</script>",
        ]:
            m = re.search(pattern, html, re.DOTALL)
            if m:
                try:
                    data = json.loads(m.group(1))
                    result = self._find_user_info(data, username)
                    if result:
                        return result
                except (json.JSONDecodeError, TypeError):
                    continue

        # Last fallback: regex from meta description
        description_meta = re.search(
            r"<meta[^>]*name=[\x22\x27]description[\x22\x27][^>]*content=[\x22\x27]([^\x22\x27]*)[\x22\x27]",
            html
        )
        description = description_meta.group(1) if description_meta else ""

        followers = self._parse_from_text(description, r"([\d,.]+[KkMmBb]?)\s*Followers?")
        following = self._parse_from_text(description, r"([\d,.]+[KkMmBb]?)\s*Following")
        likes = self._parse_from_text(description, r"([\d,.]+[KkMmBb]?)\s*Likes?")

        if followers > 0 or likes > 0:
            return {
                "username": username,
                "full_name": "",
                "bio": description,
                "profile_pic_url": "",
                "followers_count": followers,
                "following_count": following,
                "posts_count": 0,
                "is_verified": False,
                "total_likes": likes,
                "platform": "tiktok",
            }

        raise ValueError(f"Could not parse TikTok data for {username} (HTML length: {len(html)})")

    def _find_user_info(self, data: dict, username: str) -> dict | None:
        """Recursively find user info in nested dict."""
        if isinstance(data, dict):
            for key in ("userInfo", "UserModule", "user", "webapp.user-detail"):
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
                if key in data:
                    sub = data[key]
                    if isinstance(sub, dict):
                        user_data = sub.get("user", sub.get(username, sub))
                        stats = sub.get("stats", data.get("stats", {}))
                        if isinstance(user_data, dict) and ("uniqueId" in user_data or "nickname" in user_data):
                            heart = stats.get("heartCount", stats.get("heart", 0))
                            if heart < 0:
                                heart = abs(heart)
                            return {
                                "username": user_data.get("uniqueId", username),
                                "full_name": user_data.get("nickname", ""),
                                "bio": user_data.get("signature", ""),
                                "profile_pic_url": user_data.get("avatarLarger", ""),
                                "followers_count": stats.get("followerCount", 0),
                                "following_count": stats.get("followingCount", 0),
                                "posts_count": stats.get("videoCount", 0),
                                "is_verified": user_data.get("verified", False),
<<<<<<< HEAD
                                "total_likes": stats.get("heartCount", stats.get("heart", 0)),
=======
                                "total_likes": heart,
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
                                "platform": "tiktok",
                            }
            for value in data.values():
                if isinstance(value, dict):
                    result = self._find_user_info(value, username)
                    if result:
                        return result
        return None

    @staticmethod
    def _parse_count(text: str) -> int:
<<<<<<< HEAD
        text = text.strip().upper()
=======
        text = text.strip().upper().replace(",", "").replace(" ", "")
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
        for suffix, mult in {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}.items():
            if text.endswith(suffix):
                try:
                    return int(float(text[:-1]) * mult)
                except ValueError:
                    return 0
        try:
            return int(float(text))
        except ValueError:
            return 0

    @staticmethod
    def _parse_from_text(text: str, pattern: str) -> int:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return TikTokScraper._parse_count(m.group(1))
        return 0

    async def analyze_engagement(self, username: str) -> dict:
<<<<<<< HEAD
        """Analyze engagement by fetching recent videos."""
        try:
            async with TikTokApi() as api:
                await api.create_sessions(
                    num_sessions=1,
                    sleep_after=3,
                    headless=True,
                    suppress_resource_load_types=["image", "font", "stylesheet"],
                )
                user = api.user(username)
                user_info = await user.info()
                stats = user_info.get("stats", user_info.get("userInfo", {}).get("stats", {}))

                followers = stats.get("followerCount", 0)
                total_likes = stats.get("heartCount", stats.get("heart", 0))
                video_count = stats.get("videoCount", 0)

                # Try to get recent video stats
                total_views = 0
                total_video_likes = 0
                total_comments = 0
                total_shares = 0
                analyzed = 0

                try:
                    async for video in user.videos(count=10):
                        vdata = video.as_dict if hasattr(video, "as_dict") else (video if isinstance(video, dict) else {})
                        if isinstance(vdata, dict):
                            vs = vdata.get("stats", {})
                            total_views += vs.get("playCount", 0)
                            total_video_likes += vs.get("diggCount", vs.get("likes", 0))
                            total_comments += vs.get("commentCount", 0)
                            total_shares += vs.get("shareCount", 0)
                            analyzed += 1
                except Exception as ve:
                    logger.warning(f"Could not fetch videos for {username}: {ve}")

                if analyzed > 0:
                    avg_likes = total_video_likes / analyzed
                    avg_comments = total_comments / analyzed
                    avg_shares = total_shares / analyzed
                    engagement_rate = ((avg_likes + avg_comments) / max(followers, 1)) * 100
                else:
                    # Fallback: use total likes / video count
                    avg_likes = total_likes / max(video_count, 1)
                    avg_comments = 0
                    avg_shares = 0
                    engagement_rate = (avg_likes / max(followers, 1)) * 100

                return {
                    "avg_likes": round(avg_likes, 1),
                    "avg_comments": round(avg_comments, 1),
                    "avg_shares": round(avg_shares, 1),
                    "engagement_rate": round(engagement_rate, 2),
                    "total_likes": total_likes,
                    "posts_analyzed": analyzed,
                }
        except Exception as e:
            logger.warning(f"TikTok-Api engagement failed for {username}: {e}, using fallback")
            return await self._fallback_engagement(username)

    async def _fallback_engagement(self, username: str) -> dict:
        """Fallback engagement using profile data + EngagementCalculator."""
        try:
            profile = await self._fallback_scrape(username)
            followers = profile.get("followers_count", 0)
            total_likes = profile.get("total_likes", 0)
            posts_count = profile.get("posts_count", 0)

            posts = build_posts_from_tiktok(profile)
            calc = EngagementCalculator()
            report = calc.calculate(posts, max(followers, 1), "tiktok")

            avg_likes = total_likes / max(posts_count, 1)

            return {
                "avg_likes": round(avg_likes, 1),
                "avg_comments": 0,
                "avg_shares": 0,
                "engagement_rate": report.er_global,
                "er_method": report.er_method,
                "consistency": report.consistency,
                "method_confidence": report.method_confidence,
                "total_likes": total_likes,
                "posts_analyzed": report.posts_analyzed,
=======
        """Analyze TikTok engagement from profile data."""
        try:
            profile = await self.scrape_profile(username)
        except Exception as e:
            logger.error(f"Cannot get profile for engagement: {e}")
            return {
                "avg_likes": 0, "avg_comments": 0, "avg_shares": 0,
                "engagement_rate": 0.0, "total_likes": 0, "posts_analyzed": 0,
            }

        followers = profile.get("followers_count", 0)
        total_likes = profile.get("total_likes", 0)
        posts_count = profile.get("posts_count", 0)

        # Estimate engagement from profile-level data
        if posts_count > 0 and followers > 0:
            avg_likes = total_likes / posts_count
            # TikTok typical comment/like ratio ~1-3%
            estimated_comments = avg_likes * 0.02
            engagement_rate = ((avg_likes + estimated_comments) / max(followers, 1)) * 100

            return {
                "avg_likes": round(avg_likes, 1),
                "avg_comments": round(estimated_comments, 1),
                "avg_shares": 0,
                "engagement_rate": round(engagement_rate, 2),
                "total_likes": total_likes,
                "posts_analyzed": 0,
                "er_method": "estimated_from_profile",
            }

        # Fallback if no posts data
        if followers > 0 and total_likes > 0:
            # Rough estimate: assume ~100 posts
            estimated_posts = max(posts_count, 100)
            avg_likes = total_likes / estimated_posts
            engagement_rate = (avg_likes / max(followers, 1)) * 100
            return {
                "avg_likes": round(avg_likes, 1),
                "avg_comments": 0,
                "avg_shares": 0,
                "engagement_rate": round(engagement_rate, 2),
                "total_likes": total_likes,
                "posts_analyzed": 0,
                "er_method": "rough_estimate",
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
            }
        except Exception as e:
            logger.error(f"Fallback engagement failed for {username}: {e}")
            return {"avg_likes": 0, "avg_comments": 0, "avg_shares": 0, "engagement_rate": 0.0, "total_likes": 0, "posts_analyzed": 0}

        return {
            "avg_likes": 0, "avg_comments": 0, "avg_shares": 0,
            "engagement_rate": 0.0, "total_likes": total_likes, "posts_analyzed": 0,
        }

    def detect_fake_followers(self, profile_data: dict) -> float:
        """Estimate fake follower percentage for TikTok."""
        followers = profile_data.get("followers_count", 0)
        following = profile_data.get("following_count", 0)
        engagement_rate = profile_data.get("engagement_rate", 0)
        posts = profile_data.get("posts_count", 0)

        if followers == 0:
            return 0.0

        fake_score = 0.0

        if followers > 10000 and engagement_rate < 1.0:
            fake_score += 30.0
        elif followers > 5000 and engagement_rate < 2.0:
            fake_score += 20.0

        if following > followers * 3:
            fake_score += 15.0

        if posts < 5 and followers > 50000:
            fake_score += 25.0
        elif posts < 15 and followers > 100000:
            fake_score += 15.0

        return min(round(fake_score, 1), 95.0)
