import logging
from typing import Any

import instaloader

logger = logging.getLogger(__name__)


class InstagramScraper:
    def __init__(self):
        self.loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
        )

    async def scrape_profile(self, username: str) -> dict:
        """Scrape public Instagram profile data."""
        try:
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
        except instaloader.exceptions.ProfileNotExistsException:
            logger.error(f"Instagram profile not found: {username}")
            raise ValueError(f"Profile '{username}' does not exist on Instagram")
        except instaloader.exceptions.ConnectionException as e:
            logger.error(f"Connection error scraping {username}: {e}")
            raise ConnectionError(f"Failed to connect to Instagram: {e}")
        except Exception as e:
            logger.error(f"Unexpected error scraping {username}: {e}")
            raise RuntimeError(f"Error scraping profile: {e}")

    async def analyze_engagement(self, username: str, post_count: int = 12) -> dict:
        """Analyze engagement metrics from recent posts."""
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)

            if profile.is_private:
                return {
                    "error": "Profile is private",
                    "avg_likes": 0,
                    "avg_comments": 0,
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
                return {
                    "avg_likes": 0,
                    "avg_comments": 0,
                    "engagement_rate": 0.0,
                    "posts_analyzed": 0,
                }

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
        except Exception as e:
            logger.error(f"Error analyzing engagement for {username}: {e}")
            return {
                "avg_likes": 0,
                "avg_comments": 0,
                "engagement_rate": 0.0,
                "posts_analyzed": 0,
                "error": str(e),
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

        # Heuristic 1: Very low engagement rate for high follower count
        if followers > 10000 and engagement_rate < 0.5:
            fake_score += 30.0
        elif followers > 5000 and engagement_rate < 1.0:
            fake_score += 20.0
        elif followers > 1000 and engagement_rate < 1.5:
            fake_score += 10.0

        # Heuristic 2: Followers/following ratio
        ratio = followers / max(following, 1)
        if ratio > 100 and engagement_rate < 1.0:
            fake_score += 20.0
        elif following > followers * 2:
            fake_score += 15.0

        # Heuristic 3: Very few posts but many followers
        if posts < 10 and followers > 10000:
            fake_score += 25.0
        elif posts < 30 and followers > 50000:
            fake_score += 15.0

        # Heuristic 4: Abnormally round follower count
        follower_str = str(followers)
        trailing_zeros = len(follower_str) - len(follower_str.rstrip("0"))
        if trailing_zeros >= 3 and followers > 10000:
            fake_score += 10.0

        return min(round(fake_score, 1), 95.0)
