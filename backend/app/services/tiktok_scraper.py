from __future__ import annotations

import asyncio
import logging

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

            soup = BeautifulSoup(response.text, "html.parser")

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
                if key in data:
                    sub = data[key]
                    if isinstance(sub, dict):
                        user_data = sub.get("user", sub.get(username, sub))
                        stats = sub.get("stats", data.get("stats", {}))
                        if isinstance(user_data, dict) and ("uniqueId" in user_data or "nickname" in user_data):
                            return {
                                "username": user_data.get("uniqueId", username),
                                "full_name": user_data.get("nickname", ""),
                                "bio": user_data.get("signature", ""),
                                "profile_pic_url": user_data.get("avatarLarger", ""),
                                "followers_count": stats.get("followerCount", 0),
                                "following_count": stats.get("followingCount", 0),
                                "posts_count": stats.get("videoCount", 0),
                                "is_verified": user_data.get("verified", False),
                                "total_likes": stats.get("heartCount", stats.get("heart", 0)),
                                "platform": "tiktok",
                            }
            for value in data.values():
                result = self._find_user_info(value, username)
                if result:
                    return result
        return None

    @staticmethod
    def _parse_count(text: str) -> int:
        text = text.strip().upper()
        for suffix, mult in {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}.items():
            if text.endswith(suffix):
                try:
                    return int(float(text[:-1]) * mult)
                except ValueError:
                    return 0
        try:
            return int(float(text.replace(",", "")))
        except ValueError:
            return 0

    async def analyze_engagement(self, username: str) -> dict:
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
        """Fallback engagement calculation using profile data only."""
        try:
            profile = await self._fallback_scrape(username)
            followers = profile.get("followers_count", 0)
            total_likes = profile.get("total_likes", 0)
            posts = profile.get("posts_count", 0)
            avg_likes = total_likes / max(posts, 1)
            engagement_rate = (avg_likes / max(followers, 1)) * 100 if followers > 0 else 0
            return {
                "avg_likes": round(avg_likes, 1),
                "avg_comments": 0,
                "avg_shares": 0,
                "engagement_rate": round(engagement_rate, 2),
                "total_likes": total_likes,
                "posts_analyzed": 0,
            }
        except Exception as e:
            logger.error(f"Fallback engagement failed for {username}: {e}")
            return {"avg_likes": 0, "avg_comments": 0, "avg_shares": 0, "engagement_rate": 0.0, "total_likes": 0, "posts_analyzed": 0}

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
