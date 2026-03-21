"""
ra/backend/app/services/engagement_calculator.py
<<<<<<< HEAD
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
=======

v6.0 — ROI-driven scoring overhaul.
New features:
  - View/Follower ratio score
  - Enhanced conversion score (saves + shares + intent + DM signals)
  - Giveaway penalty on ER and conversion
  - Posting frequency score
  - Local audience detection score
  - New Business Score formula (conversion 30%, dm_intent 25%, posting_freq 15%,
    velocity 20%, view_ratio 10%)
  - New Overall Score: 40% Business + 30% Social + 20% Authenticity + 10% Confidence
  - Classification: HIGH_ROI / TEST / AVOID

Backward compatible — all v5 fields preserved.
"""

from __future__ import annotations

import math
import re
import statistics
import time
from dataclasses import dataclass, field
from typing import Optional, List
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
import logging

logger = logging.getLogger(__name__)


<<<<<<< HEAD
=======
# ═══════════════════════════════════════════
# Darija keywords for local audience detection
# ═══════════════════════════════════════════

DARIJA_KEYWORDS = [
    "wah", "hna", "dzair", "rabi", "kho", "sahbi", "nchallah", "baraka",
    "inchallah", "hamdoulah", "alhamdoulilah", "khouya", "khti", "walah",
    "wlh", "rahi", "rani", "nchalah", "tbarkallah", "mabrouk", "ya3tik",
    "saha", "sahit", "bsahtek", "bezzaf", "mlih", "hbib", "frero",
    "3aych", "ga3", "hada", "hadi", "hedhi", "wach", "kifash", "ki",
    "bghit", "lazim", "khlass", "dz", "dziri", "djazairi",
]

# Giveaway keywords for penalty detection
GIVEAWAY_KEYWORDS = [
    "giveaway", "concours", "tag", "gagne", "tirage",
    "مسابقة", "سحب", "هدية",
    "participe", "participez", "tente ta chance",
]


>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
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
<<<<<<< HEAD
=======
    caption: str = ""
    # v5 — timestamps and comment texts
    timestamp: Optional[float] = None
    comment_texts: list = field(default_factory=list)
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)


@dataclass
class PostEngagement:
    er_views: Optional[float] = None
    er_reach: Optional[float] = None
    er_followers: Optional[float] = None
    er_best: float = 0.0
    er_method: str = ""
    total_interactions: int = 0
    weighted_interactions: float = 0.0
<<<<<<< HEAD
=======
    intent_weighted_interactions: float = 0.0
    velocity: Optional[float] = None
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)


@dataclass
class EngagementReport:
<<<<<<< HEAD
=======
    # --- Existing v5 fields (backward compatible) ---
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
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

<<<<<<< HEAD

class EngagementCalculator:
=======
    # --- v5 ROI fields ---
    er_median: Optional[float] = None
    er_trimmed: Optional[float] = None
    intent_weighted_er: Optional[float] = None
    avg_velocity: Optional[float] = None
    velocity_score: float = 0.0
    conversion_score: float = 0.0
    buyer_intent_score: float = 0.0
    confidence_score: float = 0.0

    # --- v6 NEW ROI fields ---
    view_ratio: Optional[float] = None           # avg_views / followers
    view_ratio_score: float = 0.0                # 0-10 scored
    dm_intent_score: float = 0.0                 # 0-10 from comment_intent
    posting_frequency: float = 0.0               # posts per week
    posting_frequency_score: float = 0.0         # 0-10
    local_audience_score: float = 0.0            # 0-1 (Algerian local %)
    giveaway_detected: bool = False              # whether giveaway posts found
    business_score: float = 0.0                  # 0-10 weighted business ROI
    social_score: float = 0.0                    # 0-10 social engagement
    authenticity_score: float = 0.0              # 0-10 real audience
    overall_score: float = 0.0                   # 0-10 final weighted
    classification: str = "AVOID"                # HIGH_ROI / TEST / AVOID


class EngagementCalculator:
    """
    v6 — ROI-driven engagement calculator.

    Interaction weights (base):
        like=1.0, comment=1.2, share=1.3, save=1.5

    New scoring components:
        - view_ratio_score: views/followers health
        - conversion_score: saves + shares + intent + DM signals / views
        - posting_frequency_score: post cadence
        - local_audience_score: Algerian darija detection
        - giveaway penalty: reduce ER and conversion for giveaway posts
        - business_score: weighted composite
        - overall_score: 40% business + 30% social + 20% authenticity + 10% confidence
        - classification: HIGH_ROI / TEST / AVOID
    """

>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
    WEIGHTS = {
        "like": 1.0,
        "comment": 1.2,
        "share": 1.3,
        "save": 1.5,
    }

<<<<<<< HEAD
    def calculate(self, posts: list[PostMetrics], followers: int, platform: str = "instagram") -> EngagementReport:
        if not posts or followers <= 0:
            return EngagementReport()

=======
    def calculate(
        self,
        posts: list[PostMetrics],
        followers: int,
        platform: str = "instagram",
        intent_avg_weight: float = 1.0,
        buyer_intent_score: float = 0.0,
        dm_intent_score: float = 0.0,
        posts_count: int = 0,
        account_age_weeks: float = 0.0,
        fake_pct: float = 0.0,
        all_comment_texts: Optional[List[str]] = None,
    ) -> EngagementReport:
        """
        Full engagement calculation with ROI scoring.

        Args:
            posts: list of PostMetrics
            followers: follower count
            platform: "instagram" or "tiktok"
            intent_avg_weight: avg intent weight from comment_intent
            buyer_intent_score: 0-10 buyer intent score
            dm_intent_score: 0-10 DM intent score from comment_intent
            posts_count: total posts on profile (for frequency calc)
            account_age_weeks: approximate account age in weeks
            fake_pct: estimated fake follower percentage (0-95)
            all_comment_texts: all raw comment texts for local detection
        """
        if not posts or followers <= 0:
            return EngagementReport()

        all_comment_texts = all_comment_texts or []

        # --- Detect giveaway posts ---
        giveaway_detected = False
        for post in posts:
            caption_lower = (post.caption or "").lower()
            for kw in GIVEAWAY_KEYWORDS:
                if kw.lower() in caption_lower:
                    post.is_giveaway = True
                    giveaway_detected = True
                    break

        # Clean posts = exclude giveaway for base ER calc
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
        clean_posts = [p for p in posts if not p.is_giveaway]
        if not clean_posts:
            clean_posts = posts

<<<<<<< HEAD
=======
        # --- Per-post ER calculation ---
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
        per_post_results = []
        er_views_list = []
        er_reach_list = []
        er_followers_list = []

        for post in clean_posts:
<<<<<<< HEAD
            result = self._calculate_post_er(post, followers)
=======
            result = self._calculate_post_er(post, followers, intent_avg_weight)
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
            per_post_results.append(result)
            if result.er_views is not None:
                er_views_list.append(result.er_views)
            if result.er_reach is not None:
                er_reach_list.append(result.er_reach)
            if result.er_followers is not None:
                er_followers_list.append(result.er_followers)

<<<<<<< HEAD
=======
        # --- Method selection ---
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
        er_by_views = None
        er_by_reach = None
        er_by_followers = None
        method = "followers"
<<<<<<< HEAD
        confidence = 0.4
=======
        method_confidence = 0.4
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)

        if len(er_reach_list) >= len(clean_posts) * 0.5:
            er_by_reach = sum(er_reach_list) / len(er_reach_list)
            method = "reach"
<<<<<<< HEAD
            confidence = 0.95
=======
            method_confidence = 0.95
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)

        if len(er_views_list) >= len(clean_posts) * 0.5:
            er_by_views = sum(er_views_list) / len(er_views_list)
            if method != "reach":
                method = "views"
<<<<<<< HEAD
                confidence = 0.80
=======
                method_confidence = 0.80
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)

        if er_followers_list:
            er_by_followers = sum(er_followers_list) / len(er_followers_list)

        if method == "reach":
            er_global = er_by_reach
        elif method == "views":
            er_global = er_by_views
        else:
            er_global = er_by_followers or 0.0

<<<<<<< HEAD
=======
        # --- Totals ---
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
        total_views = sum(p.views for p in clean_posts if p.views > 0)
        total_likes = sum(p.likes for p in clean_posts)
        total_comments = sum(p.comments for p in clean_posts)
        total_shares = sum(p.shares for p in clean_posts)
        total_saves = sum(p.saves for p in clean_posts)

<<<<<<< HEAD
        views_followers_ratio = None
=======
        # --- Secondary metrics (unchanged) ---
        views_followers_ratio = None
        avg_views = 0.0
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
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
<<<<<<< HEAD
        denominator = total_views
        if total_shares > 0 and denominator > 0:
            virality_rate = round((total_shares / denominator) * 100, 3)

        best_ers = [r.er_best for r in per_post_results if r.er_best > 0]
        consistency = self._calculate_consistency(best_ers)

=======
        if total_shares > 0 and total_views > 0:
            virality_rate = round((total_shares / total_views) * 100, 3)

        # --- Consistency ---
        best_ers = [r.er_best for r in per_post_results if r.er_best > 0]
        consistency = self._calculate_consistency(best_ers)

        # --- Sponsored vs Organic ---
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
        sponsored = [r.er_best for r, p in zip(per_post_results, clean_posts) if p.is_sponsored and r.er_best > 0]
        organic = [r.er_best for r, p in zip(per_post_results, clean_posts) if not p.is_sponsored and r.er_best > 0]
        sponsored_vs_organic = None
        if sponsored and organic:
            avg_s = sum(sponsored) / len(sponsored)
            avg_o = sum(organic) / len(organic)
            if avg_o > 0:
                sponsored_vs_organic = round(avg_s / avg_o, 2)

<<<<<<< HEAD
        has_views = total_views > 0
        has_saves = total_saves > 0
        has_shares = total_shares > 0
        completeness = sum([True, True, has_views, has_saves, has_shares, False]) / 6.0
=======
        # ═══════════════════════════════════════════
        # v5 — EXISTING CALCULATIONS (preserved)
        # ═══════════════════════════════════════════

        # Outliers: median + trimmed mean
        er_median = None
        er_trimmed = None
        if len(best_ers) >= 3:
            er_median = statistics.median(best_ers)
            er_trimmed = self._trimmed_mean(best_ers, trim_pct=0.10)
        elif best_ers:
            er_median = best_ers[0]
            er_trimmed = best_ers[0]

        # Intent-weighted ER
        intent_weighted_er = None
        if er_global > 0 and intent_avg_weight != 1.0:
            intent_weighted_er = round(er_global * intent_avg_weight, 3)

        # Engagement Velocity
        velocities = [r.velocity for r in per_post_results if r.velocity is not None]
        avg_velocity = None
        velocity_score = 0.0
        if velocities:
            avg_velocity = round(sum(velocities) / len(velocities), 1)
            velocity_score = self._velocity_to_score(avg_velocity, platform)

        # ═══════════════════════════════════════════
        # v6 — NEW ROI CALCULATIONS
        # ═══════════════════════════════════════════

        # --- [1] View/Follower Ratio Score ---
        view_ratio = avg_views / followers if avg_views > 0 and followers > 0 else 0.0
        view_ratio_score = self._view_ratio_to_score(view_ratio)

        # --- [2] Giveaway Penalty ---
        # Applied to ER and later to conversion_score
        if giveaway_detected:
            er_global = er_global * 0.6
            logger.info("Giveaway detected — ER penalized to %.3f", er_global)

        # --- [3] Conversion Score (enhanced formula) ---
        # conversion = (saves*1.2 + shares*1.0 + intent_comments*2.5 + dm_signals*3.0) / views
        # intent_comments estimated from buyer_intent_score
        intent_comment_ratio = buyer_intent_score / 10.0  # 0-1
        intent_comments_est = total_comments * intent_comment_ratio

        # dm_signals estimated from dm_intent_score
        dm_signal_ratio = dm_intent_score / 10.0  # 0-1
        dm_signals_est = total_comments * dm_signal_ratio

        denominator = max(total_views, followers * 0.1, 1)
        raw_conversion = (
            total_saves * 1.2
            + total_shares * 1.0
            + intent_comments_est * 2.5
            + dm_signals_est * 3.0
        ) / denominator * 100

        # Save rate bonus
        save_bonus = 0.0
        if save_rate is not None and save_rate > 0:
            save_bonus = min(save_rate * 2.0, 3.0)

        # Sigmoid normalize to 0-10 (midpoint at 2.0%)
        conversion_score = 10.0 / (1.0 + math.exp(-1.5 * (raw_conversion + save_bonus - 2.0)))
        conversion_score = min(conversion_score, 10.0)

        # Apply giveaway penalty to conversion
        if giveaway_detected:
            conversion_score = conversion_score * 0.5
            logger.info("Giveaway detected — conversion penalized to %.1f", conversion_score)

        # --- [4] Posting Frequency Score ---
        posting_frequency = 0.0
        posting_frequency_score = 0.0
        effective_weeks = account_age_weeks
        if effective_weeks <= 0 and posts_count > 0:
            # Estimate: assume average account posts ~3/week
            effective_weeks = max(posts_count / 3.0, 1.0)
        if effective_weeks > 0 and posts_count > 0:
            posting_frequency = posts_count / effective_weeks
            posting_frequency_score = self._posting_frequency_to_score(posting_frequency)

        # --- [5] Local Audience Detection ---
        local_audience_score = self._calculate_local_audience_score(all_comment_texts)

        # --- [6] Confidence Score ---
        has_views = total_views > 0
        has_saves = total_saves > 0
        has_shares = total_shares > 0
        has_reach = er_by_reach is not None
        has_timestamps = any(r.velocity is not None for r in per_post_results)
        has_intent = intent_avg_weight != 1.0

        confidence_score = self._calculate_confidence(
            posts_count=len(clean_posts),
            method_confidence=method_confidence,
            consistency=consistency,
            has_views=has_views,
            has_saves=has_saves,
            has_shares=has_shares,
            has_reach=has_reach,
            has_timestamps=has_timestamps,
            has_intent=has_intent,
        )

        # --- Data completeness ---
        completeness_flags = [
            True,             # likes
            True,             # comments
            has_views,
            has_saves,
            has_shares,
            has_reach,
            has_timestamps,
            has_intent,
        ]
        data_completeness = sum(completeness_flags) / len(completeness_flags)

        # ═══════════════════════════════════════════
        # v6 — COMPOSITE SCORES
        # ═══════════════════════════════════════════

        # --- Business Score (weighted mix) ---
        # conversion_score (30%) + dm_intent_score (25%) + posting_frequency (15%)
        # + engagement_velocity (20%) + view_ratio_score (10%)
        business_score = (
            conversion_score * 0.30
            + dm_intent_score * 0.25
            + posting_frequency_score * 0.15
            + velocity_score * 0.20
            + view_ratio_score * 0.10
        )
        business_score = round(min(max(business_score, 0.0), 10.0), 2)

        # --- Social Score ---
        # Based on ER sigmoid + comment quality + consistency
        social_score = self._calculate_social_score(er_global, consistency, followers, platform)

        # --- Authenticity Score ---
        # Inverse of fake_pct, boosted by local audience
        authenticity_score = self._calculate_authenticity_score(fake_pct, local_audience_score, view_ratio)

        # --- Overall Score (new formula) ---
        # 40% Business + 30% Social + 20% Authenticity + 10% Confidence
        overall_score = (
            business_score * 0.40
            + social_score * 0.30
            + authenticity_score * 0.20
            + (confidence_score * 10.0) * 0.10  # confidence is 0-1, scale to 0-10
        )
        overall_score = round(min(max(overall_score, 0.0), 10.0), 2)

        # --- Classification ---
        if overall_score >= 7.5:
            classification = "HIGH_ROI"
        elif overall_score >= 5.0:
            classification = "TEST"
        else:
            classification = "AVOID"
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)

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
<<<<<<< HEAD
            method_confidence=round(confidence, 2),
            data_completeness=round(completeness, 2),
            per_post=[{"er": round(r.er_best, 3), "method": r.er_method, "interactions": r.total_interactions} for r in per_post_results],
        )

    def _calculate_post_er(self, post: PostMetrics, followers: int) -> PostEngagement:
        total = post.likes + post.comments + post.shares + post.saves
=======
            method_confidence=round(method_confidence, 2),
            data_completeness=round(data_completeness, 2),
            per_post=[
                {
                    "er": round(r.er_best, 3),
                    "method": r.er_method,
                    "interactions": r.total_interactions,
                    "velocity": r.velocity,
                }
                for r in per_post_results
            ],
            # v5 preserved
            er_median=round(er_median, 3) if er_median is not None else None,
            er_trimmed=round(er_trimmed, 3) if er_trimmed is not None else None,
            intent_weighted_er=intent_weighted_er,
            avg_velocity=avg_velocity,
            velocity_score=round(velocity_score, 1),
            conversion_score=round(conversion_score, 1),
            buyer_intent_score=round(buyer_intent_score, 1),
            confidence_score=round(confidence_score, 2),
            # v6 new fields
            view_ratio=round(view_ratio, 4) if view_ratio else None,
            view_ratio_score=round(view_ratio_score, 1),
            dm_intent_score=round(dm_intent_score, 1),
            posting_frequency=round(posting_frequency, 2),
            posting_frequency_score=round(posting_frequency_score, 1),
            local_audience_score=round(local_audience_score, 2),
            giveaway_detected=giveaway_detected,
            business_score=business_score,
            social_score=round(social_score, 2),
            authenticity_score=round(authenticity_score, 2),
            overall_score=overall_score,
            classification=classification,
        )

    # ═══════════════════════════════════════════
    # Per-post ER (unchanged from v5)
    # ═══════════════════════════════════════════

    def _calculate_post_er(
        self,
        post: PostMetrics,
        followers: int,
        intent_avg_weight: float = 1.0,
    ) -> PostEngagement:
        total = post.likes + post.comments + post.shares + post.saves

>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
        weighted = (
            post.likes * self.WEIGHTS["like"]
            + post.comments * self.WEIGHTS["comment"]
            + post.shares * self.WEIGHTS["share"]
            + post.saves * self.WEIGHTS["save"]
        )
<<<<<<< HEAD
        result = PostEngagement(total_interactions=total, weighted_interactions=round(weighted, 1))
=======

        intent_weighted = (
            post.likes * self.WEIGHTS["like"]
            + post.comments * self.WEIGHTS["comment"] * intent_avg_weight
            + post.shares * self.WEIGHTS["share"]
            + post.saves * self.WEIGHTS["save"]
        )

        result = PostEngagement(
            total_interactions=total,
            weighted_interactions=round(weighted, 1),
            intent_weighted_interactions=round(intent_weighted, 1),
        )
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)

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

<<<<<<< HEAD
        return result

=======
        # Velocity
        if post.timestamp is not None and post.timestamp > 0 and total > 0:
            age_hours = max((time.time() - post.timestamp) / 3600, 1.0)
            result.velocity = round(total / age_hours, 1)

        return result

    # ═══════════════════════════════════════════
    # View/Follower Ratio Score (0-10)
    # ═══════════════════════════════════════════

    @staticmethod
    def _view_ratio_to_score(view_ratio: float) -> float:
        """
        Score views/followers ratio.
        <0.05 = dead (0-2), 0.05-0.15 = moyen (3-5),
        0.20+ = bon (6-8), 0.40+ = excellent (9-10)
        """
        if view_ratio <= 0:
            return 0.0
        if view_ratio >= 0.60:
            return 10.0
        elif view_ratio >= 0.40:
            # 9-10
            return 9.0 + (view_ratio - 0.40) / 0.20
        elif view_ratio >= 0.20:
            # 6-9
            return 6.0 + (view_ratio - 0.20) / 0.20 * 3.0
        elif view_ratio >= 0.15:
            # 5-6
            return 5.0 + (view_ratio - 0.15) / 0.05
        elif view_ratio >= 0.05:
            # 2-5
            return 2.0 + (view_ratio - 0.05) / 0.10 * 3.0
        else:
            # 0-2 (dead)
            return max(view_ratio / 0.05 * 2.0, 0.0)

    # ═══════════════════════════════════════════
    # Posting Frequency Score (0-10)
    # ═══════════════════════════════════════════

    @staticmethod
    def _posting_frequency_to_score(posts_per_week: float) -> float:
        """
        Score posting frequency.
        <1 = faible (2), 1-3 = moyen (5), 3-7 = excellent (9), >7 = over-posting (6)
        """
        if posts_per_week <= 0:
            return 0.0
        elif posts_per_week < 1.0:
            # faible: 0-2
            return max(posts_per_week * 2.0, 0.0)
        elif posts_per_week <= 3.0:
            # moyen: 2-5, interpolate
            return 2.0 + (posts_per_week - 1.0) / 2.0 * 3.0
        elif posts_per_week <= 7.0:
            # excellent: 5-9, interpolate
            return 5.0 + (posts_per_week - 3.0) / 4.0 * 4.0
        else:
            # over-posting: drop back to 6
            # The more over-posting, the lower (down to 4)
            penalty = min((posts_per_week - 7.0) / 7.0, 1.0)
            return max(6.0 - penalty * 2.0, 4.0)

    # ═══════════════════════════════════════════
    # Local Audience Detection (0-1)
    # ═══════════════════════════════════════════

    @staticmethod
    def _calculate_local_audience_score(comment_texts: list[str]) -> float:
        """
        Analyze comment language to detect local Algerian audience.
        Returns 0-1 (1 = mostly local Algerian audience).

        Checks for:
        - Darija keywords
        - Arabic script presence
        - Algerian city mentions (wilayas)
        """
        if not comment_texts:
            return 0.0

        total = len(comment_texts)
        local_signals = 0

        # Build wilaya set (lowercase) — all 58 wilayas
        wilayas_lower = {
            "adrar", "chlef", "laghouat", "oum el bouaghi", "batna", "bejaia",
            "biskra", "bechar", "blida", "bouira", "tamanrasset", "tebessa",
            "tlemcen", "tiaret", "tizi ouzou", "alger", "djelfa", "jijel",
            "setif", "saida", "skikda", "sidi bel abbes", "annaba", "guelma",
            "constantine", "medea", "mostaganem", "m'sila", "mascara", "ouargla",
            "oran", "el bayadh", "illizi", "bordj bou arreridj", "boumerdes",
            "el tarf", "tindouf", "tissemsilt", "el oued", "khenchela",
            "souk ahras", "tipaza", "mila", "ain defla", "naama", "ain temouchent",
            "ghardaia", "relizane", "timimoun", "touggourt", "djanet",
            "el meniaa", "el m'ghair",
            # Common short forms
            "dzair", "wahran", "qsentina", "stif", "bgayet", "tizi",
        }

        darija_set = set(DARIJA_KEYWORDS)

        for text in comment_texts:
            lower = text.lower().strip()
            is_local = False

            # Check Arabic script presence
            if re.search(r'[\u0600-\u06FF]', text):
                is_local = True

            # Check darija keywords
            if not is_local:
                words = set(re.findall(r'\w+', lower))
                if words & darija_set:
                    is_local = True

            # Check wilaya mentions
            if not is_local:
                for w in wilayas_lower:
                    if w in lower:
                        is_local = True
                        break

            if is_local:
                local_signals += 1

        return local_signals / total if total > 0 else 0.0

    # ═══════════════════════════════════════════
    # Social Score (0-10)
    # ═══════════════════════════════════════════

    @staticmethod
    def _calculate_social_score(
        er_global: float,
        consistency: float,
        followers: int,
        platform: str,
    ) -> float:
        """
        Social engagement score based on ER, consistency, and platform norms.
        """
        # ER sigmoid score (tier-adjusted)
        if platform == "tiktok":
            thresholds = [(10.0, 10), (5.0, 8), (2.0, 5), (1.0, 3)]
        else:
            thresholds = [(5.0, 10), (3.0, 8), (1.5, 5), (0.5, 3)]

        # Adjust by follower size
        if followers > 500_000:
            scale = 0.6
        elif followers > 100_000:
            scale = 0.8
        else:
            scale = 1.0

        er_score = 0.0
        for threshold, max_score in thresholds:
            if er_global >= threshold * scale:
                er_score = float(max_score)
                break
        if er_score == 0.0 and er_global > 0:
            er_score = min(er_global / (0.5 * scale) * 3.0, 3.0)

        # Consistency bonus/penalty
        consistency_component = consistency * 10.0

        social = er_score * 0.65 + consistency_component * 0.35
        return min(max(social, 0.0), 10.0)

    # ═══════════════════════════════════════════
    # Authenticity Score (0-10)
    # ═══════════════════════════════════════════

    @staticmethod
    def _calculate_authenticity_score(
        fake_pct: float,
        local_audience_score: float,
        view_ratio: float,
    ) -> float:
        """
        Authenticity = inverse of fake followers, boosted by local audience
        and healthy view ratio.
        """
        # Base: inverse fake pct (0-95 → 10-0.5)
        base = max(10.0 - (fake_pct / 10.0), 0.0)

        # Local audience bonus (up to +1.5)
        local_bonus = local_audience_score * 1.5

        # View ratio factor: dead views = fake audience penalty
        vr_factor = 1.0
        if view_ratio < 0.05:
            vr_factor = 0.7  # heavy penalty
        elif view_ratio < 0.15:
            vr_factor = 0.85

        score = (base + local_bonus) * vr_factor
        return min(max(score, 0.0), 10.0)

    # ═══════════════════════════════════════════
    # Velocity → Score (unchanged from v5)
    # ═══════════════════════════════════════════

    @staticmethod
    def _velocity_to_score(avg_velocity: float, platform: str) -> float:
        """Convert average velocity to 0-10 score."""
        if platform == "tiktok":
            thresholds = (2000, 500, 100, 50)
        else:
            thresholds = (500, 100, 30, 10)

        excellent, good, ok, low = thresholds

        if avg_velocity >= excellent:
            return 10.0
        elif avg_velocity >= good:
            return 7.0 + (avg_velocity - good) / (excellent - good) * 3.0
        elif avg_velocity >= ok:
            return 4.0 + (avg_velocity - ok) / (good - ok) * 3.0
        elif avg_velocity >= low:
            return 1.0 + (avg_velocity - low) / (ok - low) * 3.0
        else:
            return max(avg_velocity / low, 0.0)

    # ═══════════════════════════════════════════
    # Trimmed mean (unchanged from v5)
    # ═══════════════════════════════════════════

    @staticmethod
    def _trimmed_mean(values: list[float], trim_pct: float = 0.10) -> float:
        if len(values) < 3:
            return sum(values) / len(values) if values else 0.0
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        trim_count = max(1, int(n * trim_pct))
        trimmed = sorted_vals[:n - trim_count]
        return sum(trimmed) / len(trimmed) if trimmed else 0.0

    # ═══════════════════════════════════════════
    # Confidence Score (0-1) — enhanced v6
    # ═══════════════════════════════════════════

    @staticmethod
    def _calculate_confidence(
        posts_count: int,
        method_confidence: float,
        consistency: float,
        has_views: bool,
        has_saves: bool,
        has_shares: bool,
        has_reach: bool,
        has_timestamps: bool,
        has_intent: bool,
    ) -> float:
        """Confidence Score (0-1) based on data quality and completeness."""
        method_score = method_confidence

        if posts_count >= 20:
            posts_score = 1.0
        elif posts_count >= 10:
            posts_score = 0.8
        elif posts_count >= 5:
            posts_score = 0.6
        elif posts_count >= 3:
            posts_score = 0.4
        else:
            posts_score = 0.2

        consistency_score = consistency

        richness_flags = [has_views, has_saves, has_shares, has_reach, has_timestamps, has_intent]
        richness_score = sum(richness_flags) / len(richness_flags)

        confidence = (
            method_score * 0.30
            + posts_score * 0.25
            + consistency_score * 0.20
            + richness_score * 0.25
        )

        return min(max(confidence, 0.0), 1.0)

    # ═══════════════════════════════════════════
    # Consistency (unchanged)
    # ═══════════════════════════════════════════

>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
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


<<<<<<< HEAD
def build_posts_from_instagrapi(medias) -> list[PostMetrics]:
    posts = []
    for m in medias:
        caption = (m.caption_text or "").lower()
        is_sponsored = any(w in caption for w in ["#ad", "#pub", "#sponsored", "#partenariat", "#collaboration", "sponsoris"])
        post_type = {1: "photo", 2: "video", 8: "carousel"}.get(m.media_type, "unknown")
=======
# ═══════════════════════════════════════════
# Builders (backward compatible)
# ═══════════════════════════════════════════

def build_posts_from_instagrapi(medias) -> list[PostMetrics]:
    """Convert instagrapi media objects to PostMetrics v6."""
    posts = []
    for m in medias:
        caption = (m.caption_text or "").lower()
        is_sponsored = any(w in caption for w in [
            "#ad", "#pub", "#sponsored", "#partenariat", "#collaboration", "sponsoris",
        ])
        post_type = {1: "photo", 2: "video", 8: "carousel"}.get(m.media_type, "unknown")

        timestamp = None
        if hasattr(m, "taken_at") and m.taken_at:
            try:
                timestamp = m.taken_at.timestamp()
            except Exception:
                pass

        comment_texts = []
        if hasattr(m, "comments") and m.comments:
            comment_texts = [c.text for c in m.comments if hasattr(c, "text") and c.text]

>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
        posts.append(PostMetrics(
            likes=m.like_count or 0,
            comments=m.comment_count or 0,
            views=m.view_count or 0,
            is_sponsored=is_sponsored,
            post_type=post_type,
<<<<<<< HEAD
=======
            caption=m.caption_text or "",
            timestamp=timestamp,
            comment_texts=comment_texts,
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
        ))
    return posts


def build_posts_from_tiktok(profile_data: dict, video_stats: list[dict] = None) -> list[PostMetrics]:
<<<<<<< HEAD
=======
    """Convert TikTok data to PostMetrics v6."""
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
    if video_stats:
        posts = []
        for v in video_stats:
            stats = v.get("stats", v)
<<<<<<< HEAD
=======

            timestamp = None
            create_time = v.get("createTime") or v.get("create_time")
            if create_time:
                try:
                    timestamp = float(create_time)
                except (ValueError, TypeError):
                    pass

            comment_texts = []
            if "comments" in v and isinstance(v["comments"], list):
                comment_texts = [
                    c.get("text", "") for c in v["comments"]
                    if isinstance(c, dict) and c.get("text")
                ]

            caption = v.get("desc", v.get("caption", ""))

>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
            posts.append(PostMetrics(
                likes=stats.get("diggCount", stats.get("likes", 0)),
                comments=stats.get("commentCount", stats.get("comments", 0)),
                shares=stats.get("shareCount", stats.get("shares", 0)),
                saves=stats.get("collectCount", stats.get("favorites", 0)),
                views=stats.get("playCount", stats.get("views", 0)),
                post_type="video",
<<<<<<< HEAD
=======
                caption=caption,
                timestamp=timestamp,
                comment_texts=comment_texts,
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
            ))
        return posts

    total_likes = profile_data.get("total_likes", 0)
    video_count = profile_data.get("posts_count", 0)
    if video_count <= 0:
        return []
    avg_likes = total_likes / video_count
    return [PostMetrics(likes=int(avg_likes), post_type="video")]
