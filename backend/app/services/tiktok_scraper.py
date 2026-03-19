from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

TIKTOK_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


class TikTokScraper:
    async def scrape_profile(self, username: str) -> dict:
        """Scrape public TikTok profile data."""
        url = f"https://www.tiktok.com/@{username}"
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                response = await client.get(url, headers=TIKTOK_HEADERS)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Try to extract data from SIGI_STATE or __UNIVERSAL_DATA_FOR_REHYDRATION__
            profile_data = self._extract_from_script_tags(soup, username)
            if profile_data:
                return profile_data

            # Fallback: try meta tags
            return self._extract_from_meta_tags(soup, username)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"TikTok profile '{username}' not found")
            logger.error(f"HTTP error scraping TikTok {username}: {e}")
            raise ConnectionError(f"Failed to fetch TikTok profile: {e}")
        except Exception as e:
            logger.error(f"Error scraping TikTok profile {username}: {e}")
            raise RuntimeError(f"Error scraping TikTok profile: {e}")

    def _extract_from_script_tags(self, soup: BeautifulSoup, username: str) -> dict:
        """Try to extract profile data from embedded JSON in script tags."""
        for script in soup.find_all("script", id=re.compile(r"__UNIVERSAL_DATA|SIGI_STATE|__NEXT_DATA__")):
            try:
                data = json.loads(script.string or "{}")
                user_info = self._find_user_info(data, username)
                if user_info:
                    return user_info
            except (json.JSONDecodeError, TypeError):
                continue
        return None

    def _find_user_info(self, data: dict, username: str) -> dict:
        """Recursively search for user info in nested JSON."""
        if isinstance(data, dict):
            # Check common TikTok JSON structures
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
                                "profile_pic_url": user_data.get("avatarLarger", user_data.get("avatarMedium", "")),
                                "followers_count": stats.get("followerCount", 0),
                                "following_count": stats.get("followingCount", 0),
                                "posts_count": stats.get("videoCount", 0),
                                "is_verified": user_data.get("verified", False),
                                "platform": "tiktok",
                            }
            for value in data.values():
                result = self._find_user_info(value, username)
                if result:
                    return result
        return None

    def _extract_from_meta_tags(self, soup: BeautifulSoup, username: str) -> dict:
        """Fallback extraction from meta tags."""
        title_tag = soup.find("title")
        title = title_tag.string if title_tag else ""

        description_meta = soup.find("meta", attrs={"name": "description"})
        description = description_meta.get("content", "") if description_meta else ""

        # Try to parse follower counts from description
        followers = 0
        following = 0
        likes = 0
        follower_match = re.search(r"([\d.]+[KMB]?)\s*Followers", description, re.IGNORECASE)
        following_match = re.search(r"([\d.]+[KMB]?)\s*Following", description, re.IGNORECASE)
        likes_match = re.search(r"([\d.]+[KMB]?)\s*Likes", description, re.IGNORECASE)

        if follower_match:
            followers = self._parse_count(follower_match.group(1))
        if following_match:
            following = self._parse_count(following_match.group(1))
        if likes_match:
            likes = self._parse_count(likes_match.group(1))

        return {
            "username": username,
            "full_name": title.split("(")[0].strip() if "(" in title else "",
            "bio": description,
            "profile_pic_url": "",
            "followers_count": followers,
            "following_count": following,
            "posts_count": 0,
            "is_verified": False,
            "total_likes": likes,
            "platform": "tiktok",
        }

    @staticmethod
    def _parse_count(text: str) -> int:
        """Parse abbreviated counts like 1.5K, 2M, etc."""
        text = text.strip().upper()
        multipliers = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
        for suffix, mult in multipliers.items():
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
        """Analyze engagement for a TikTok profile."""
        try:
            profile = await self.scrape_profile(username)
            followers = profile.get("followers_count", 0)
            total_likes = profile.get("total_likes", 0)
            posts = profile.get("posts_count", 0)

            avg_likes = total_likes / max(posts, 1)
            engagement_rate = (avg_likes / max(followers, 1)) * 100 if followers > 0 else 0

            return {
                "avg_likes": round(avg_likes, 1),
                "avg_comments": 0,  # Not available from profile page
                "avg_shares": 0,
                "engagement_rate": round(engagement_rate, 2),
                "total_likes": total_likes,
            }
        except Exception as e:
            logger.error(f"Error analyzing TikTok engagement for {username}: {e}")
            return {
                "avg_likes": 0,
                "avg_comments": 0,
                "avg_shares": 0,
                "engagement_rate": 0.0,
                "error": str(e),
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

        # TikTok typically has higher engagement rates
        if followers > 10000 and engagement_rate < 1.0:
            fake_score += 30.0
        elif followers > 5000 and engagement_rate < 2.0:
            fake_score += 20.0

        # Following ratio
        if following > followers * 3:
            fake_score += 15.0

        # Few videos but many followers
        if posts < 5 and followers > 50000:
            fake_score += 25.0
        elif posts < 15 and followers > 100000:
            fake_score += 15.0

        return min(round(fake_score, 1), 95.0)
