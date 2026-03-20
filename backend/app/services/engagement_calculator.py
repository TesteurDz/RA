"""
ra/backend/app/services/engagement_calculator.py
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class PostMetrics:
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    views: int = 0
    reach: int = 0
    is_sponsored: bool = False
    is_giveaway: bool = False
    post_type: str = ""


@dataclass
class PostEngagement:
    er_views: Optional[float] = None
    er_reach: Optional[float] = None
    er_followers: Optional[float] = None
    er_best: float = 0.0
    er_method: str = ""
    total_interactions: int = 0
    weighted_interactions: float = 0.0


@dataclass
class EngagementReport:
    er_global: float = 0.0
    er_method: str = ""
    er_by_views: Optional[float] = None
    er_by_reach: Optional[float] = None
    er_by_followers: Optional[float] = None
    views_followers_ratio: Optional[float] = None
    save_rate: Optional[float] = None
    share_rate: Optional[float] = None
    comment_like_ratio: Optional[float] = None
    virality_rate: Optional[float] = None
    consistency: float = 0.0
    sponsored_vs_organic: Optional[float] = None
    posts_analyzed: int = 0
    method_confidence: float = 0.0
    data_completeness: float = 0.0
    per_post: list = field(default_factory=list)


class EngagementCalculator:
    WEIGHTS = {
        "like": 1.0,
        "comment": 1.2,
        "share": 1.3,
        "save": 1.5,
    }

    def calculate(self, posts: list[PostMetrics], followers: int, platform: str = "instagram") -> EngagementReport:
        if not posts or followers <= 0:
            return EngagementReport()

        clean_posts = [p for p in posts if not p.is_giveaway]
        if not clean_posts:
            clean_posts = posts

        per_post_results = []
        er_views_list = []
        er_reach_list = []
        er_followers_list = []

        for post in clean_posts:
            result = self._calculate_post_er(post, followers)
            per_post_results.append(result)
            if result.er_views is not None:
                er_views_list.append(result.er_views)
            if result.er_reach is not None:
                er_reach_list.append(result.er_reach)
            if result.er_followers is not None:
                er_followers_list.append(result.er_followers)

        er_by_views = None
        er_by_reach = None
        er_by_followers = None
        method = "followers"
        confidence = 0.4

        if len(er_reach_list) >= len(clean_posts) * 0.5:
            er_by_reach = sum(er_reach_list) / len(er_reach_list)
            method = "reach"
            confidence = 0.95

        if len(er_views_list) >= len(clean_posts) * 0.5:
            er_by_views = sum(er_views_list) / len(er_views_list)
            if method != "reach":
                method = "views"
                confidence = 0.80

        if er_followers_list:
            er_by_followers = sum(er_followers_list) / len(er_followers_list)

        if method == "reach":
            er_global = er_by_reach
        elif method == "views":
            er_global = er_by_views
        else:
            er_global = er_by_followers or 0.0

        total_views = sum(p.views for p in clean_posts if p.views > 0)
        total_likes = sum(p.likes for p in clean_posts)
        total_comments = sum(p.comments for p in clean_posts)
        total_shares = sum(p.shares for p in clean_posts)
        total_saves = sum(p.saves for p in clean_posts)

        views_followers_ratio = None
        if total_views > 0:
            avg_views = total_views / len(clean_posts)
            views_followers_ratio = round(avg_views / followers, 2)

        save_rate = None
        if total_saves > 0 and total_views > 0:
            save_rate = round((total_saves / total_views) * 100, 3)
        elif total_saves > 0:
            save_rate = round((total_saves / len(clean_posts) / followers) * 100, 3)

        share_rate = None
        if total_shares > 0 and total_views > 0:
            share_rate = round((total_shares / total_views) * 100, 3)

        comment_like_ratio = None
        if total_likes > 0 and total_comments > 0:
            comment_like_ratio = round((total_comments / total_likes) * 100, 2)

        virality_rate = None
        denominator = total_views
        if total_shares > 0 and denominator > 0:
            virality_rate = round((total_shares / denominator) * 100, 3)

        best_ers = [r.er_best for r in per_post_results if r.er_best > 0]
        consistency = self._calculate_consistency(best_ers)

        sponsored = [r.er_best for r, p in zip(per_post_results, clean_posts) if p.is_sponsored and r.er_best > 0]
        organic = [r.er_best for r, p in zip(per_post_results, clean_posts) if not p.is_sponsored and r.er_best > 0]
        sponsored_vs_organic = None
        if sponsored and organic:
            avg_s = sum(sponsored) / len(sponsored)
            avg_o = sum(organic) / len(organic)
            if avg_o > 0:
                sponsored_vs_organic = round(avg_s / avg_o, 2)

        has_views = total_views > 0
        has_saves = total_saves > 0
        has_shares = total_shares > 0
        completeness = sum([True, True, has_views, has_saves, has_shares, False]) / 6.0

        return EngagementReport(
            er_global=round(er_global, 3),
            er_method=method,
            er_by_views=round(er_by_views, 3) if er_by_views else None,
            er_by_reach=round(er_by_reach, 3) if er_by_reach else None,
            er_by_followers=round(er_by_followers, 3) if er_by_followers else None,
            views_followers_ratio=views_followers_ratio,
            save_rate=save_rate,
            share_rate=share_rate,
            comment_like_ratio=comment_like_ratio,
            virality_rate=virality_rate,
            consistency=round(consistency, 2),
            sponsored_vs_organic=sponsored_vs_organic,
            posts_analyzed=len(clean_posts),
            method_confidence=round(confidence, 2),
            data_completeness=round(completeness, 2),
            per_post=[{"er": round(r.er_best, 3), "method": r.er_method, "interactions": r.total_interactions} for r in per_post_results],
        )

    def _calculate_post_er(self, post: PostMetrics, followers: int) -> PostEngagement:
        total = post.likes + post.comments + post.shares + post.saves
        weighted = (
            post.likes * self.WEIGHTS["like"]
            + post.comments * self.WEIGHTS["comment"]
            + post.shares * self.WEIGHTS["share"]
            + post.saves * self.WEIGHTS["save"]
        )
        result = PostEngagement(total_interactions=total, weighted_interactions=round(weighted, 1))

        if post.reach > 0:
            result.er_reach = (weighted / post.reach) * 100
        if post.views > 0:
            result.er_views = (weighted / post.views) * 100
        if followers > 0:
            result.er_followers = (weighted / followers) * 100

        if result.er_reach is not None:
            result.er_best = result.er_reach
            result.er_method = "reach"
        elif result.er_views is not None:
            result.er_best = result.er_views
            result.er_method = "views"
        elif result.er_followers is not None:
            result.er_best = result.er_followers
            result.er_method = "followers"

        return result

    @staticmethod
    def _calculate_consistency(values: list[float]) -> float:
        if len(values) < 2:
            return 1.0
        mean = sum(values) / len(values)
        if mean <= 0:
            return 0.0
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = variance ** 0.5
        return max(1 - (std / mean), 0.0)


def build_posts_from_instagrapi(medias) -> list[PostMetrics]:
    posts = []
    for m in medias:
        caption = (m.caption_text or "").lower()
        is_sponsored = any(w in caption for w in ["#ad", "#pub", "#sponsored", "#partenariat", "#collaboration", "sponsoris"])
        post_type = {1: "photo", 2: "video", 8: "carousel"}.get(m.media_type, "unknown")
        posts.append(PostMetrics(
            likes=m.like_count or 0,
            comments=m.comment_count or 0,
            views=m.view_count or 0,
            is_sponsored=is_sponsored,
            post_type=post_type,
        ))
    return posts


def build_posts_from_tiktok(profile_data: dict, video_stats: list[dict] = None) -> list[PostMetrics]:
    if video_stats:
        posts = []
        for v in video_stats:
            stats = v.get("stats", v)
            posts.append(PostMetrics(
                likes=stats.get("diggCount", stats.get("likes", 0)),
                comments=stats.get("commentCount", stats.get("comments", 0)),
                shares=stats.get("shareCount", stats.get("shares", 0)),
                saves=stats.get("collectCount", stats.get("favorites", 0)),
                views=stats.get("playCount", stats.get("views", 0)),
                post_type="video",
            ))
        return posts

    total_likes = profile_data.get("total_likes", 0)
    video_count = profile_data.get("posts_count", 0)
    if video_count <= 0:
        return []
    avg_likes = total_likes / video_count
    return [PostMetrics(likes=int(avg_likes), post_type="video")]
