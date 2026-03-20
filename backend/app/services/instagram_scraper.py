from __future__ import annotations

import asyncio
import logging

try:
    from app.core.proxy import PROXY_URL
except ImportError:
    PROXY_URL = None
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import instaloader

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=2)

# Try to use instagrapi first, fallback to instaloader
try:
    from instagrapi import Client as InstaClient
    HAS_INSTAGRAPI = True
except ImportError:
    HAS_INSTAGRAPI = False


class InstagramScraper:
    def __init__(self):
        # Instaloader (fallback)
        self.loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
        )
        # Instagrapi client (primary if logged in)
        self._ig_client = None
        self._ig_logged_in = False

    def login_instagrapi(self, username: str, password: str) -> bool:
        """Login to Instagram via instagrapi for better access."""
        if not HAS_INSTAGRAPI:
            logger.warning("instagrapi not installed")
            return False
        try:
            self._ig_client = InstaClient()
            if PROXY_URL:
                self._ig_client.set_proxy(PROXY_URL)
            self._ig_client.login(username, password)
            self._ig_logged_in = True
            logger.info(f"Logged in to Instagram as {username}")
            return True
        except Exception as e:
            logger.error(f"Instagram login failed: {e}")
            self._ig_logged_in = False
            return False

    def _scrape_with_instagrapi(self, username: str) -> dict:
        """Scrape using instagrapi (logged in, more reliable)."""
        user_info = self._ig_client.user_info_by_username(username)
        return {
            "username": user_info.username,
            "full_name": user_info.full_name,
            "bio": user_info.biography or "",
            "profile_pic_url": str(user_info.profile_pic_url) if user_info.profile_pic_url else "",
            "followers_count": user_info.follower_count,
            "following_count": user_info.following_count,
            "posts_count": user_info.media_count,
            "is_verified": user_info.is_verified,
            "is_private": user_info.is_private,
            "external_url": user_info.external_url or "",
            "platform": "instagram",
            "user_id": user_info.pk,
        }

    def _engagement_with_instagrapi(self, username: str, post_count: int = 6) -> dict:
        """Get engagement using instagrapi (individual post stats)."""
        user_info = self._ig_client.user_info_by_username(username)

        if user_info.is_private:
            return {
                "error": "Profile is private",
                "avg_likes": 0, "avg_comments": 0,
                "engagement_rate": 0.0, "posts_analyzed": 0,
            }

        medias = self._ig_client.user_medias(user_info.pk, amount=post_count)

        if not medias:
            return {
                "avg_likes": 0, "avg_comments": 0,
                "engagement_rate": 0.0, "posts_analyzed": 0,
            }

        total_likes = sum(m.like_count for m in medias)
        total_comments = sum(m.comment_count for m in medias)
        total_views = sum((m.view_count or 0) for m in medias)
        analyzed = len(medias)

        avg_likes = total_likes / analyzed
        avg_comments = total_comments / analyzed
        followers = user_info.follower_count or 1
        engagement_rate = ((avg_likes + avg_comments) / followers) * 100

        return {
            "avg_likes": round(avg_likes, 1),
            "avg_comments": round(avg_comments, 1),
            "avg_views": round(total_views / analyzed, 1) if total_views else 0,
            "engagement_rate": round(engagement_rate, 2),
            "posts_analyzed": analyzed,
        }

    def _scrape_with_instaloader(self, username: str) -> dict:
        """Fallback: scrape using instaloader."""
        profile = instaloader.Profile.from_username(self.loader.context, username)
        return {
            "username": profile.username,
            "full_name": profile.full_name,
            "bio": profile.biography,
            "profile_pic_url": profile.profile_pic_url,
            "followers_count": profile.followers,
            "following_count": profile.followees,
            "posts_count": profile.mediacount,
            "is_verified": profile.is_verified,
            "is_private": profile.is_private,
            "external_url": profile.external_url,
            "platform": "instagram",
        }

    def _engagement_with_instaloader(self, username: str, post_count: int = 6) -> dict:
        """Fallback: engagement using instaloader."""
        profile = instaloader.Profile.from_username(self.loader.context, username)

        if profile.is_private:
            return {
                "error": "Profile is private",
                "avg_likes": 0, "avg_comments": 0,
                "engagement_rate": 0.0,
            }

        total_likes = 0
        total_comments = 0
        analyzed = 0

        for post in profile.get_posts():
            if analyzed >= post_count:
                break
            total_likes += post.likes
            total_comments += post.comments
            analyzed += 1

        if analyzed == 0:
            return {"avg_likes": 0, "avg_comments": 0, "engagement_rate": 0.0, "posts_analyzed": 0}

        avg_likes = total_likes / analyzed
        avg_comments = total_comments / analyzed
        followers = profile.followers if profile.followers > 0 else 1
        engagement_rate = ((avg_likes + avg_comments) / followers) * 100

        return {
            "avg_likes": round(avg_likes, 1),
            "avg_comments": round(avg_comments, 1),
            "engagement_rate": round(engagement_rate, 2),
            "posts_analyzed": analyzed,
        }

    async def scrape_profile(self, username: str) -> dict:
        """Scrape Instagram profile. Uses instagrapi if logged in, else instaloader."""
        loop = asyncio.get_event_loop()
        try:
            if self._ig_logged_in:
                return await loop.run_in_executor(
                    _executor, lambda: self._scrape_with_instagrapi(username)
                )
            else:
                return await loop.run_in_executor(
                    _executor, lambda: self._scrape_with_instaloader(username)
                )
        except instaloader.exceptions.ProfileNotExistsException:
            raise ValueError(f"Profile '{username}' does not exist on Instagram")
        except instaloader.exceptions.ConnectionException as e:
            raise ConnectionError(f"Failed to connect to Instagram: {e}")
        except Exception as e:
            # If instagrapi fails, try instaloader
            if self._ig_logged_in:
                logger.warning(f"instagrapi failed, trying instaloader: {e}")
                try:
                    return await loop.run_in_executor(
                        _executor, lambda: self._scrape_with_instaloader(username)
                    )
                except Exception as e2:
                    raise RuntimeError(f"Both scrapers failed: {e2}")
            raise RuntimeError(f"Error scraping profile: {e}")

    async def analyze_engagement(self, username: str, post_count: int = 6) -> dict:
        """Analyze engagement. Uses instagrapi if logged in, else instaloader."""
        loop = asyncio.get_event_loop()
        try:
            if self._ig_logged_in:
                return await loop.run_in_executor(
                    _executor, lambda: self._engagement_with_instagrapi(username, post_count)
                )
            else:
                return await loop.run_in_executor(
                    _executor, lambda: self._engagement_with_instaloader(username, post_count)
                )
        except Exception as e:
            logger.error(f"Error analyzing engagement for {username}: {e}")
            return {
                "avg_likes": 0, "avg_comments": 0,
                "engagement_rate": 0.0, "posts_analyzed": 0, "error": str(e),
            }

    def detect_fake_followers(self, profile_data: dict) -> float:
        """Estimate fake follower percentage using heuristics."""
        followers = profile_data.get("followers_count", 0)
        following = profile_data.get("following_count", 0)
        engagement_rate = profile_data.get("engagement_rate", 0)
        posts = profile_data.get("posts_count", 0)

        if followers == 0:
            return 0.0

        fake_score = 0.0

        if followers > 10000 and engagement_rate < 0.5:
            fake_score += 30.0
        elif followers > 5000 and engagement_rate < 1.0:
            fake_score += 20.0
        elif followers > 1000 and engagement_rate < 1.5:
            fake_score += 10.0

        ratio = followers / max(following, 1)
        if ratio > 100 and engagement_rate < 1.0:
            fake_score += 20.0
        elif following > followers * 2:
            fake_score += 15.0

        if posts < 10 and followers > 10000:
            fake_score += 25.0
        elif posts < 30 and followers > 50000:
            fake_score += 15.0

        follower_str = str(followers)
        trailing_zeros = len(follower_str) - len(follower_str.rstrip("0"))
        if trailing_zeros >= 3 and followers > 10000:
            fake_score += 10.0

        return min(round(fake_score, 1), 95.0)
