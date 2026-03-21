from __future__ import annotations

import asyncio
import logging
import random
import time

try:
    from app.core.proxy import PROXY_URL, get_rotating_proxy
except ImportError:
    PROXY_URL = None
    def get_rotating_proxy(): return None
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import json
import os

from app.services.engagement_calculator import EngagementCalculator, build_posts_from_instagrapi, PostMetrics

logger = logging.getLogger(__name__)

SESSION_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ig_session.json")

_executor = ThreadPoolExecutor(max_workers=2)

try:
    from instagrapi import Client as InstaClient
    HAS_INSTAGRAPI = True
except ImportError:
    HAS_INSTAGRAPI = False

try:
    import instaloader
    HAS_INSTALOADER = True
except ImportError:
    HAS_INSTALOADER = False


class InstagramScraper:
    def __init__(self):
        # Instaloader (fallback)
        if HAS_INSTALOADER:
            self.loader = instaloader.Instaloader(
                download_pictures=False,
                download_videos=False,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=False,
                compress_json=False,
            )
        else:
            self.loader = None
        # Instagrapi client (primary if logged in)
        self._ig_client = None
        self._ig_logged_in = False
        self._last_request_time = 0

    _daily_count = 0
    _daily_reset = 0

    def _rate_limit_delay(self):
        """Human-like delay between requests to avoid detection."""
        import datetime
        now = time.time()
        # Reset daily counter
        today = datetime.date.today().toordinal()
        if self._daily_reset != today:
            InstagramScraper._daily_count = 0
            InstagramScraper._daily_reset = today

        elapsed = now - self._last_request_time
        # Random delay 5-10s (balanced speed/safety)
        min_delay = 5.0
        max_delay = 10.0
        if elapsed < min_delay:
            delay = random.uniform(min_delay - elapsed, max_delay - elapsed)
            logger.info(f"Rate limit delay: {delay:.1f}s")
            time.sleep(delay)
        self._last_request_time = time.time()
        InstagramScraper._daily_count += 1

    def _rotate_proxy(self):
        """Set static proxy (rotation via IPRoyal auto-rotate)."""
        if self._ig_client and PROXY_URL:
            try:
                self._ig_client.set_proxy(PROXY_URL)
            except Exception:
                pass

    def load_session(self, session_path: str = None) -> bool:
        """Load a saved instagrapi session from JSON file."""
        if not HAS_INSTAGRAPI:
            logger.warning("instagrapi not installed")
            return False
        path = session_path or SESSION_FILE
        if not os.path.exists(path):
            logger.warning(f"Session file not found: {path}")
            return False
        try:
            self._ig_client = InstaClient()
            # Don't set proxy at session load — set it per request
            logger.info("Loading session without proxy (proxy set per-request)")

            # Load settings
            with open(path, "r") as f:
                settings_data = json.load(f)
            self._ig_client.set_settings(settings_data)

            # Don't validate with get_timeline_feed — it flags accounts
            # Just trust the session and let it fail on first real request if invalid
            self._ig_logged_in = True
            logger.info("Instagram session loaded (no validation to avoid detection)")
            return True

            self._ig_logged_in = False
            return False
        except Exception as e:
            logger.error(f"Session load failed: {e}")
            self._ig_logged_in = False
            return False

    def login_instagrapi(self, username: str, password: str) -> bool:
        """Login to Instagram via instagrapi."""
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
            self._ig_client.dump_settings(SESSION_FILE)
            return True
        except Exception as e:
            logger.error(f"Instagram login failed: {e}")
            self._ig_logged_in = False
            return False

    def _scrape_with_instagrapi(self, username: str) -> dict:
        """Scrape using instagrapi PRIVATE API (v1) to avoid 429 on public endpoints."""
        self._rate_limit_delay()

        # Try with proxy first, fallback to direct if proxy fails
        try:
            self._rotate_proxy()
            user_info = self._ig_client.user_info_by_username_v1(username)
        except Exception as e:
            err = str(e).lower()
            if "proxy" in err or "407" in err or "tunnel" in err:
                logger.warning(f"Proxy failed for {username}, trying without proxy: {e}")
                self._ig_client.set_proxy(None)
                try:
                    user_info = self._ig_client.user_info_by_username_v1(username)
                except Exception as e2:
                    logger.warning(f"v1 without proxy failed: {e2}, trying default")
                    user_info = self._ig_client.user_info_by_username(username)
            else:
                logger.warning(f"v1 failed for {username}: {e}, trying default method")
                user_info = self._ig_client.user_info_by_username(username)

        # Cache user_info to avoid redundant API calls
        self._last_user_info = user_info
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
        """Get engagement using instagrapi PRIVATE API + EngagementCalculator."""
        self._rate_limit_delay()
        try:
            self._rotate_proxy()
        except Exception:
            self._ig_client.set_proxy(None)

        # Reuse cached user_info from scrape_profile
        if hasattr(self, '_last_user_info') and self._last_user_info and self._last_user_info.username == username:
            user_info = self._last_user_info
            logger.info(f"Reusing cached user_info for {username}")
        else:
            try:
                user_info = self._ig_client.user_info_by_username_v1(username)
            except Exception:
                user_info = self._ig_client.user_info_by_username(username)

        if user_info.is_private:
            return {
                "error": "Profile is private",
                "avg_likes": 0, "avg_comments": 0,
                "engagement_rate": 0.0, "posts_analyzed": 0,
            }

        self._rate_limit_delay()

        # Force v1 medias endpoint (private API)
        try:
            medias = self._ig_client.user_medias_v1(user_info.pk, amount=post_count)
        except Exception as e:
            logger.warning(f"user_medias_v1 failed: {e}, trying default")
            medias = self._ig_client.user_medias(user_info.pk, amount=post_count)

        if not medias:
            return {
                "avg_likes": 0, "avg_comments": 0,
                "engagement_rate": 0.0, "posts_analyzed": 0,
            }

        posts = build_posts_from_instagrapi(medias)
        calc = EngagementCalculator()
        report = calc.calculate(posts, user_info.follower_count or 1, "instagram")

        total_likes = sum(m.like_count for m in medias)
        total_comments = sum(m.comment_count for m in medias)
        total_views = sum((m.view_count or 0) for m in medias)
        analyzed = len(medias)

        return {
            "avg_likes": round(total_likes / analyzed, 1),
            "avg_comments": round(total_comments / analyzed, 1),
            "avg_views": round(total_views / analyzed, 1) if total_views else 0,
            "engagement_rate": report.er_global,
            "er_method": report.er_method,
            "er_by_views": report.er_by_views,
            "er_by_followers": report.er_by_followers,
            "consistency": report.consistency,
            "comment_like_ratio": report.comment_like_ratio,
            "views_followers_ratio": report.views_followers_ratio,
            "method_confidence": report.method_confidence,
            "posts_analyzed": report.posts_analyzed,
        }

    def _scrape_with_instaloader(self, username: str) -> dict:
        """Fallback: scrape using instaloader."""
        if not self.loader:
            raise RuntimeError("instaloader not available")
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
        if not self.loader:
            raise RuntimeError("instaloader not available")
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
        """Scrape Instagram profile. Uses instagrapi private API if logged in."""
        loop = asyncio.get_event_loop()
        try:
            if self._ig_logged_in:
                return await loop.run_in_executor(
                    _executor, lambda: self._scrape_with_instagrapi(username)
                )
            elif self.loader:
                return await loop.run_in_executor(
                    _executor, lambda: self._scrape_with_instaloader(username)
                )
            else:
                raise RuntimeError("No Instagram scraper available (instagrapi not logged in, instaloader not available)")
        except Exception as e:
            # If instagrapi fails, try instaloader as fallback
            if self._ig_logged_in and self.loader:
                logger.warning(f"instagrapi failed for {username}: {e}, trying instaloader")
                try:
                    return await loop.run_in_executor(
                        _executor, lambda: self._scrape_with_instaloader(username)
                    )
                except Exception as e2:
                    raise RuntimeError(f"Both scrapers failed for {username}: instagrapi={e}, instaloader={e2}")
            raise RuntimeError(f"Error scraping profile {username}: {e}")

    async def analyze_engagement(self, username: str, post_count: int = 6) -> dict:
        """Analyze engagement. Uses instagrapi private API if logged in."""
        loop = asyncio.get_event_loop()
        try:
            if self._ig_logged_in:
                return await loop.run_in_executor(
                    _executor, lambda: self._engagement_with_instagrapi(username, post_count)
                )
            elif self.loader:
                return await loop.run_in_executor(
                    _executor, lambda: self._engagement_with_instaloader(username, post_count)
                )
            else:
                return {"avg_likes": 0, "avg_comments": 0, "engagement_rate": 0.0, "posts_analyzed": 0, "error": "No scraper available"}
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
