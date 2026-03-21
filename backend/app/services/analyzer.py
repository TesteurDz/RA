from __future__ import annotations

import logging
import math
import re
import statistics
from collections import Counter
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

# All 58 Algerian wilayas
ALGERIAN_WILAYAS = [
    "Adrar", "Chlef", "Laghouat", "Oum El Bouaghi", "Batna", "Bejaia",
    "Biskra", "Bechar", "Blida", "Bouira", "Tamanrasset", "Tebessa",
    "Tlemcen", "Tiaret", "Tizi Ouzou", "Alger", "Djelfa", "Jijel",
    "Setif", "Saida", "Skikda", "Sidi Bel Abbes", "Annaba", "Guelma",
    "Constantine", "Medea", "Mostaganem", "M'Sila", "Mascara", "Ouargla",
    "Oran", "El Bayadh", "Illizi", "Bordj Bou Arreridj", "Boumerdes",
    "El Tarf", "Tindouf", "Tissemsilt", "El Oued", "Khenchela",
    "Souk Ahras", "Tipaza", "Mila", "Ain Defla", "Naama", "Ain Temouchent",
    "Ghardaia", "Relizane",
    # 10 new wilayas added in 2019
    "Timimoun", "Bordj Badji Mokhtar", "Ouled Djellal", "Beni Abbes",
    "In Salah", "In Guezzam", "Touggourt", "Djanet", "El M'Ghair", "El Meniaa",
]

# Alternative spellings and common variations
WILAYA_ALIASES = {
    "algiers": "Alger",
    "algers": "Alger",
    "dzair": "Alger",
    "el djazair": "Alger",
    "bejaia": "Bejaia",
    "bgayet": "Bejaia",
    "bougie": "Bejaia",
    "wahran": "Oran",
    "qsentina": "Constantine",
    "setif": "Setif",
    "stif": "Setif",
    "tizi": "Tizi Ouzou",
    "tizi-ouzou": "Tizi Ouzou",
    "tiziouzou": "Tizi Ouzou",
    "annaba": "Annaba",
    "bone": "Annaba",
    "blida": "Blida",
    "el boulaida": "Blida",
    "batna": "Batna",
    "biskra": "Biskra",
    "djelfa": "Djelfa",
    "ghardaia": "Ghardaia",
    "gardaia": "Ghardaia",
    "msila": "M'Sila",
    "m sila": "M'Sila",
    "boumerdes": "Boumerdes",
    "tipaza": "Tipaza",
    "chlef": "Chlef",
    "medea": "Medea",
    "skikda": "Skikda",
    "jijel": "Jijel",
    "mostaganem": "Mostaganem",
    "mascara": "Mascara",
    "tlemcen": "Tlemcen",
    "ouargla": "Ouargla",
    "bechar": "Bechar",
    "saida": "Saida",
    "guelma": "Guelma",
    "mila": "Mila",
    "souk ahras": "Souk Ahras",
}

# Simple positive/negative word lists for basic sentiment
POSITIVE_WORDS = {
    "love", "great", "amazing", "beautiful", "awesome", "best", "perfect",
    "excellent", "wonderful", "fantastic", "good", "nice", "bravo", "magnifique",
    "super", "top", "incroyable", "formidable", "genial", "bien",
    "mabrouk", "mashallah", "tbarkallah", "rani", "waaw",
}

NEGATIVE_WORDS = {
    "bad", "terrible", "worst", "ugly", "hate", "horrible", "awful",
    "fake", "scam", "fraud", "nul", "mauvais", "honte", "arnaque",
    "moche", "degueu", "narik", "hchouma",
}

# Common bot comment patterns
BOT_PATTERNS = [
    r"follow\s*(me|back|4follow)",
    r"f4f",
    r"check\s*(my|out)",
    r"dm\s*(me|for)",
    r"free\s*followers",
    r"grow\s*your",
    r"visit\s*(my|link)",
    r"click\s*(link|bio)",
    r"^(nice|cool|great|wow|amazing|fire|love)[\s!.]*$",
    r"^[\U0001f600-\U0001f64f\U0001f300-\U0001f5ff\U0001f680-\U0001f6ff\U0001f1e0-\U0001f1ff]{1,5}$",
]

# ---------- Improvement 1: Buyer Intent Keywords ----------

INTENT_KEYWORDS = {
    "achat_direct": [
        "prix", "combien", "commander", "acheter", "dispo", "livraison",
        "stock", "taille", "couleur", "payer", "wesh le prix", "chhal",
        "kayen", "nta3 sah",
    ],
    "interet": [
        "j'adore", "je veux", "trop beau", "magnifique", "waaw",
        "mashallah", "top", "ou trouver",
    ],
    "spam": [
        "follow me", "f4f", "check bio", "dm me", "check my",
        "free followers", "grow your",
    ],
}

INTENT_COEFFICIENTS = {
    "achat_direct": 2.0,
    "interet": 1.5,
    "neutre": 1.0,
    "spam": 0.3,
}

# ---------- Improvement 4: Per-tier engagement thresholds ----------

ENGAGEMENT_TIERS = {
    "nano": {"min_followers": 0, "max_followers": 10_000, "threshold": 5.0},
    "micro": {"min_followers": 10_000, "max_followers": 50_000, "threshold": 3.0},
    "mid": {"min_followers": 50_000, "max_followers": 200_000, "threshold": 2.0},
    "macro": {"min_followers": 200_000, "max_followers": 1_000_000, "threshold": 1.5},
    "mega": {"min_followers": 1_000_000, "max_followers": float("inf"), "threshold": 1.0},
}


def _get_tier(followers: int) -> dict:
    """Return the engagement tier dict for a given follower count."""
    for tier in ENGAGEMENT_TIERS.values():
        if tier["min_followers"] <= followers < tier["max_followers"]:
            return tier
    return ENGAGEMENT_TIERS["mega"]


def sigmoid_score(er: float, threshold: float) -> float:
    """Improvement 4: Sigmoid normalization instead of linear."""
    x = (er - threshold) / (threshold * 0.5)
    try:
        return round(10.0 / (1.0 + math.exp(-x)), 2)
    except OverflowError:
        return 0.0 if x < 0 else 10.0


class AnalyzerService:
    # ------------------------------------------------------------------ #
    #  EXISTING methods (kept intact for backward compatibility)           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def calculate_engagement_rate(
        avg_likes: float,
        avg_comments: float,
        avg_shares: float,
        followers: int,
    ) -> float:
        """Calculate engagement rate as a percentage."""
        if followers <= 0:
            return 0.0
        total_engagement = avg_likes + avg_comments + avg_shares
        rate = (total_engagement / followers) * 100
        return round(rate, 2)

    @staticmethod
    def estimate_fake_followers(
        followers: int,
        following: int,
        engagement_rate: float,
        avg_likes: float,
    ) -> float:
        """Estimate fake follower percentage using heuristics."""
        if followers == 0:
            return 0.0

        score = 0.0

        if followers > 10000:
            if engagement_rate < 0.5:
                score += 35.0
            elif engagement_rate < 1.0:
                score += 25.0
            elif engagement_rate < 1.5:
                score += 15.0
        elif followers > 1000:
            if engagement_rate < 1.0:
                score += 25.0
            elif engagement_rate < 2.0:
                score += 15.0

        likes_ratio = avg_likes / followers if followers > 0 else 0
        if likes_ratio < 0.005 and followers > 10000:
            score += 20.0
        elif likes_ratio < 0.01 and followers > 5000:
            score += 10.0

        if following > 0 and followers > 0:
            ratio = followers / following
            if ratio > 200 and engagement_rate < 1.0:
                score += 15.0

        follower_str = str(followers)
        if len(follower_str) >= 5 and follower_str[-3:] == "000":
            score += 5.0

        return min(round(score, 1), 95.0)

    @staticmethod
    def analyze_comments(comments: list) -> dict:
        """Analyze a list of comments for quality metrics."""
        if not comments:
            return {
                "total_analyzed": 0,
                "bot_pct": 0.0,
                "positive_pct": 0.0,
                "negative_pct": 0.0,
                "neutral_pct": 0.0,
                "top_languages": [],
                "avg_length": 0.0,
            }

        total = len(comments)
        bot_count = 0
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total_length = 0
        lang_counter = Counter()

        for comment in comments:
            comment_lower = comment.lower().strip()
            total_length += len(comment)

            is_bot = False
            for pattern in BOT_PATTERNS:
                if re.search(pattern, comment_lower):
                    bot_count += 1
                    is_bot = True
                    break

            if not is_bot:
                if len(comment_lower) <= 3:
                    bot_count += 1
                    is_bot = True

            words = set(re.findall(r"\w+", comment_lower))
            pos_hits = len(words & POSITIVE_WORDS)
            neg_hits = len(words & NEGATIVE_WORDS)

            if pos_hits > neg_hits:
                positive_count += 1
            elif neg_hits > pos_hits:
                negative_count += 1
            else:
                neutral_count += 1

            if re.search(r"[\u0600-\u06FF]", comment):
                lang_counter["Arabic"] += 1
            elif re.search(r"[\u00C0-\u017F]", comment):
                lang_counter["French"] += 1
            else:
                lang_counter["English"] += 1

        top_langs = [{"language": lang, "count": count} for lang, count in lang_counter.most_common(5)]

        return {
            "total_analyzed": total,
            "bot_pct": round((bot_count / total) * 100, 1),
            "positive_pct": round((positive_count / total) * 100, 1),
            "negative_pct": round((negative_count / total) * 100, 1),
            "neutral_pct": round((neutral_count / total) * 100, 1),
            "top_languages": top_langs,
            "avg_length": round(total_length / total, 1),
        }

    @staticmethod
    def estimate_demographics(profile_data: dict, comments_data: dict) -> dict:
        """Estimate audience demographics based on available data."""
        platform = profile_data.get("platform", "instagram")

        if platform == "tiktok":
            return {
                "estimated_male_pct": 45.0,
                "estimated_female_pct": 55.0,
                "age_13_17_pct": 25.0,
                "age_18_24_pct": 40.0,
                "age_25_34_pct": 22.0,
                "age_35_44_pct": 9.0,
                "age_45_plus_pct": 4.0,
                "top_countries": [{"country": "Algeria", "pct": 70.0}],
                "top_cities": [],
            }
        else:
            return {
                "estimated_male_pct": 50.0,
                "estimated_female_pct": 50.0,
                "age_13_17_pct": 10.0,
                "age_18_24_pct": 35.0,
                "age_25_34_pct": 32.0,
                "age_35_44_pct": 15.0,
                "age_45_plus_pct": 8.0,
                "top_countries": [{"country": "Algeria", "pct": 65.0}],
                "top_cities": [],
            }

    @staticmethod
    def calculate_overall_score(
        engagement_rate: float,
        fake_pct: float,
        comment_quality: float,
        growth_pattern: float = 5.0,
        followers_count: int = 0,
    ) -> float:
        """
        Calculate overall influencer score from 0 to 10.
        (Legacy method kept for backward compatibility.)
        """
<<<<<<< HEAD
        # Scale engagement expectation by follower tier
        if followers_count > 10_000_000:
            # Mega: 0.5-2% is excellent
            engagement_score = min(engagement_rate / 2.0 * 10.0, 10.0)
        elif followers_count > 1_000_000:
            # Macro: 1-3% is good
            engagement_score = min(engagement_rate / 3.0 * 10.0, 10.0)
        elif followers_count > 100_000:
            # Mid: 2-5% is good
            engagement_score = min(engagement_rate / 5.0 * 10.0, 10.0)
        else:
            # Micro/nano: up to 10%
            engagement_score = min(engagement_rate / 10.0 * 10.0, 10.0)

        # Invert fake percentage (lower is better)
=======
        engagement_score = min(engagement_rate / 10.0 * 10.0, 10.0)
>>>>>>> 4c4603f (RA v6e — Advanced ROI scoring, OCR Mistral, anti-detection, multi-screenshot)
        authenticity_score = max(10.0 - (fake_pct / 10.0), 0.0)
        comment_score = min(max(comment_quality, 0.0), 10.0)
        growth_score = min(max(growth_pattern, 0.0), 10.0)

        overall = (
            engagement_score * 0.30
            + authenticity_score * 0.30
            + comment_score * 0.20
            + growth_score * 0.20
        )

        return round(min(max(overall, 0.0), 10.0), 1)

    @staticmethod
    def detect_zone_operation(bio: str = "", location: str = "", hashtags: list = None, followers_count: int = 0, is_verified: bool = False) -> str:
        """Try to detect Algerian wilaya from bio, location, or hashtags."""
        # Skip zone detection for verified international profiles
        if is_verified and followers_count > 1_000_000:
            return None
        hashtags = hashtags or []
        search_text = f"{bio} {location} {' '.join(hashtags)}".lower()

        for alias, wilaya in WILAYA_ALIASES.items():
            if alias in search_text:
                return wilaya

        for wilaya in ALGERIAN_WILAYAS:
            if wilaya.lower() in search_text:
                return wilaya

        wilaya_numbers = {
            "01": "Adrar", "02": "Chlef", "03": "Laghouat", "04": "Oum El Bouaghi",
            "05": "Batna", "06": "Bejaia", "07": "Biskra", "08": "Bechar",
            "09": "Blida", "10": "Bouira", "11": "Tamanrasset", "12": "Tebessa",
            "13": "Tlemcen", "14": "Tiaret", "15": "Tizi Ouzou", "16": "Alger",
            "17": "Djelfa", "18": "Jijel", "19": "Setif", "20": "Saida",
            "21": "Skikda", "22": "Sidi Bel Abbes", "23": "Annaba", "24": "Guelma",
            "25": "Constantine", "26": "Medea", "27": "Mostaganem", "28": "M'Sila",
            "29": "Mascara", "30": "Ouargla", "31": "Oran", "32": "El Bayadh",
            "33": "Illizi", "34": "Bordj Bou Arreridj", "35": "Boumerdes",
            "36": "El Tarf", "37": "Tindouf", "38": "Tissemsilt", "39": "El Oued",
            "40": "Khenchela", "41": "Souk Ahras", "42": "Tipaza", "43": "Mila",
            "44": "Ain Defla", "45": "Naama", "46": "Ain Temouchent",
            "47": "Ghardaia", "48": "Relizane",
        }

        for num, wilaya in wilaya_numbers.items():
            if re.search(rf"\b{num}\b", search_text):
                return wilaya

        return None

    # ================================================================== #
    #  EXISTING improvement methods (kept intact)                         #
    # ================================================================== #

    @staticmethod
    def classify_comment_intent(comment: str) -> str:
        """Classify a single comment into an intent category."""
        lower = comment.lower().strip()

        for kw in INTENT_KEYWORDS["spam"]:
            if kw in lower:
                return "spam"
        for pattern in BOT_PATTERNS:
            if re.search(pattern, lower):
                return "spam"

        for kw in INTENT_KEYWORDS["achat_direct"]:
            if kw in lower:
                return "achat_direct"

        for kw in INTENT_KEYWORDS["interet"]:
            if kw in lower:
                return "interet"

        return "neutre"

    @staticmethod
    def analyze_buyer_intent(comments: list) -> dict:
        """Classify all comments by buyer intent."""
        if not comments:
            return {
                "distribution": {"achat_direct": 0, "interet": 0, "neutre": 0, "spam": 0},
                "distribution_pct": {"achat_direct": 0.0, "interet": 0.0, "neutre": 0.0, "spam": 0.0},
                "weighted_coefficient": 1.0,
                "total_analyzed": 0,
            }

        counts = {"achat_direct": 0, "interet": 0, "neutre": 0, "spam": 0}
        for comment in comments:
            intent = AnalyzerService.classify_comment_intent(comment)
            counts[intent] += 1

        total = len(comments)
        pcts = {k: round(v / total * 100, 1) for k, v in counts.items()}

        weighted_sum = sum(counts[k] * INTENT_COEFFICIENTS[k] for k in counts)
        weighted_coeff = round(weighted_sum / total, 3)

        return {
            "distribution": counts,
            "distribution_pct": pcts,
            "weighted_coefficient": weighted_coeff,
            "total_analyzed": total,
        }

    @staticmethod
    def calculate_engagement_velocity(
        post_engagements: Optional[List[dict]] = None,
        total_engagement: float = 0.0,
        posts_count: int = 0,
        account_age_days: Optional[float] = None,
    ) -> dict:
        """Calculate engagement velocity (interactions / time)."""
        velocity_score = 0.0
        velocity_per_day = 0.0
        method = "estimated"

        if post_engagements and len(post_engagements) >= 2:
            timestamped = [p for p in post_engagements if p.get("timestamp")]
            if len(timestamped) >= 2:
                sorted_posts = sorted(timestamped, key=lambda p: p["timestamp"])
                first_ts = sorted_posts[0]["timestamp"]
                last_ts = sorted_posts[-1]["timestamp"]
                time_span_days = max((last_ts - first_ts) / 86400.0, 1.0)
                total_eng = sum(p.get("engagement", 0) for p in sorted_posts)
                velocity_per_day = round(total_eng / time_span_days, 2)
                method = "timestamp"
            else:
                if posts_count > 0 and account_age_days and account_age_days > 0:
                    post_freq_per_day = posts_count / account_age_days
                    velocity_per_day = round(total_engagement * post_freq_per_day, 2)
                    method = "frequency_estimated"
        elif posts_count > 0 and total_engagement > 0:
            est_days = max(posts_count / 0.43, 7.0)
            velocity_per_day = round((total_engagement * posts_count) / est_days, 2)
            method = "rough_estimated"

        if velocity_per_day > 0:
            x = (math.log10(max(velocity_per_day, 1)) - 2.0) / 1.0
            try:
                velocity_score = round(10.0 / (1.0 + math.exp(-x)), 2)
            except OverflowError:
                velocity_score = 10.0 if x > 0 else 0.0

        return {
            "velocity_per_day": velocity_per_day,
            "velocity_score": velocity_score,
            "method": method,
        }

    @staticmethod
    def robust_engagement_stats(
        post_engagements: Optional[List[float]] = None,
        avg_engagement: float = 0.0,
    ) -> dict:
        """Calculate median engagement and handle outliers."""
        if not post_engagements or len(post_engagements) == 0:
            return {
                "mean": avg_engagement,
                "median": avg_engagement,
                "trimmed_mean": avg_engagement,
                "outliers_removed": 0,
                "sample_size": 0,
            }

        sorted_eng = sorted(post_engagements)
        n = len(sorted_eng)
        raw_mean = statistics.mean(sorted_eng)
        raw_median = statistics.median(sorted_eng)

        trimmed = sorted_eng
        outliers_removed = 0
        if n >= 5:
            cutoff_idx = max(int(n * 0.9), 1)
            bottom_90 = sorted_eng[:cutoff_idx]
            mean_90 = statistics.mean(bottom_90)
            if raw_mean > 2 * mean_90 and mean_90 > 0:
                trimmed = bottom_90
                outliers_removed = n - cutoff_idx

        trimmed_mean = statistics.mean(trimmed) if trimmed else raw_mean

        return {
            "mean": round(raw_mean, 2),
            "median": round(raw_median, 2),
            "trimmed_mean": round(trimmed_mean, 2),
            "outliers_removed": outliers_removed,
            "sample_size": n,
        }

    @staticmethod
    def calculate_social_score(
        engagement_rate: float,
        fake_pct: float,
        comment_quality: float,
        followers: int,
    ) -> float:
        """Social Score (0-10) — legacy method kept for compatibility."""
        tier = _get_tier(followers)
        engagement_component = sigmoid_score(engagement_rate, tier["threshold"])
        authenticity_component = max(10.0 - (fake_pct / 10.0), 0.0)
        quality_component = min(max(comment_quality, 0.0), 10.0)

        social = (
            engagement_component * 0.40
            + authenticity_component * 0.35
            + quality_component * 0.25
        )
        return round(min(max(social, 0.0), 10.0), 2)

    @staticmethod
    def calculate_business_score(
        conversion_score: float,
        buyer_intent_coeff: float,
        content_fit: float = 5.0,
    ) -> float:
        """Business Score (0-10) — legacy method kept for compatibility."""
        conv_component = min(max(conversion_score, 0.0), 10.0)
        intent_component = min((buyer_intent_coeff / 2.0) * 10.0, 10.0)
        fit_component = min(max(content_fit, 0.0), 10.0)

        business = (
            conv_component * 0.40
            + intent_component * 0.35
            + fit_component * 0.25
        )
        return round(min(max(business, 0.0), 10.0), 2)

    @staticmethod
    def calculate_conversion_score(
        saves: float = 0.0,
        intent_comments: float = 0.0,
        shares: float = 0.0,
        views: float = 0.0,
    ) -> float:
        """Conversion score based on high-intent actions — legacy."""
        raw = (saves * 1.5 + intent_comments * 2.0 + shares * 1.2) / max(views, 1) * 1000
        return round(sigmoid_score(raw, 5.0), 2)

    @staticmethod
    def calculate_confidence(
        posts_analyzed: int = 0,
        has_comments: bool = False,
        has_views: bool = False,
        has_saves: bool = False,
        has_shares: bool = False,
        has_timestamps: bool = False,
        metrics_coherent: bool = True,
    ) -> dict:
        """Confidence score (0-100) based on data quality."""
        score = 0.0

        if posts_analyzed >= 30:
            score += 30.0
        elif posts_analyzed >= 12:
            score += 20.0
        elif posts_analyzed >= 5:
            score += 12.0
        elif posts_analyzed >= 1:
            score += 5.0

        if has_comments:
            score += 12.0
        if has_views:
            score += 12.0
        if has_saves:
            score += 8.0
        if has_shares:
            score += 8.0
        if has_timestamps:
            score += 10.0

        if metrics_coherent:
            score += 20.0
        else:
            score += 5.0

        confidence = min(round(score, 1), 100.0)

        level = "low"
        if confidence >= 70:
            level = "high"
        elif confidence >= 40:
            level = "medium"

        return {
            "score": confidence,
            "level": level,
            "posts_analyzed": posts_analyzed,
        }

    # ================================================================== #
    #  v6 — ADVANCED ANALYZE (ROI-driven overhaul)                        #
    # ================================================================== #

    @staticmethod
    def advanced_analyze(
        profile_data: dict,
        engagement_data: dict,
        comments: Optional[list] = None,
        post_engagements: Optional[List[dict]] = None,
    ) -> dict:
        """
        v6 — Full advanced analysis with ROI-driven scoring.

        Returns all existing fields (backward compatible) plus:
        - dm_intent_score: DM/purchase intent from comments (0-10)
        - view_ratio: avg_views / followers
        - view_ratio_score: scored view ratio (0-10)
        - local_score: Algerian local audience detection (0-1)
        - conversion_score: enhanced conversion metric (0-10)
        - posting_frequency: posts per week
        - posting_frequency_score: scored frequency (0-10)
        - business_score_v6: new weighted business ROI (0-10)
        - social_score_v6: new social engagement (0-10)
        - authenticity_score: real audience score (0-10)
        - overall_score_v6: 40% business + 30% social + 20% auth + 10% conf
        - classification: HIGH_ROI / TEST / AVOID
        - giveaway_detected: bool
        """
        svc = AnalyzerService

        followers = profile_data.get("followers_count", 0)
        following = profile_data.get("following_count", 0)
        platform = profile_data.get("platform", "instagram")
        posts_count = profile_data.get("posts_count", 0)

        er = engagement_data.get("engagement_rate", 0.0)
        avg_likes = engagement_data.get("avg_likes", 0.0)
        avg_comments = engagement_data.get("avg_comments", 0.0)
        avg_shares = engagement_data.get("avg_shares", 0.0)
        avg_views = engagement_data.get("avg_views", 0.0)
        avg_saves = engagement_data.get("avg_saves", 0.0)

        comments = comments or []
        post_engagements = post_engagements or []

        # --- Existing analyses (backward compatible) ---
        fake_pct = svc.estimate_fake_followers(
            followers=followers,
            following=following,
            engagement_rate=er,
            avg_likes=avg_likes,
        )

        comment_analysis = svc.analyze_comments(comments)
        demographics = svc.estimate_demographics(profile_data, comment_analysis)

        zone = svc.detect_zone_operation(
            bio=profile_data.get("bio", ""),
            location=profile_data.get("location", ""),
            hashtags=profile_data.get("hashtags", []),
        )

        # --- 1. Buyer Intent (legacy) ---
        buyer_intent = svc.analyze_buyer_intent(comments)

        # --- 1b. Enhanced DM Intent (v6 via comment_intent module) ---
        dm_intent_score = 0.0
        dm_intent_report = None
        try:
            from app.services.comment_intent import analyze_comment_intents
            intent_report = analyze_comment_intents(comments)
            dm_intent_score = intent_report.dm_intent_score
            dm_intent_report = {
                "total": intent_report.total,
                "achat_direct_count": intent_report.achat_direct_count,
                "interet_count": intent_report.interet_count,
                "dm_request_count": intent_report.dm_request_count,
                "neutre_count": intent_report.neutre_count,
                "spam_count": intent_report.spam_count,
                "achat_direct_pct": intent_report.achat_direct_pct,
                "interet_pct": intent_report.interet_pct,
                "dm_request_pct": intent_report.dm_request_pct,
                "buyer_intent_score": intent_report.buyer_intent_score,
                "dm_intent_score": intent_report.dm_intent_score,
                "avg_intent_weight": intent_report.avg_intent_weight,
                "sample_achat": intent_report.sample_achat,
                "sample_interet": intent_report.sample_interet,
                "sample_dm": intent_report.sample_dm,
            }
        except Exception as e:
            logger.warning("comment_intent module not available: %s", e)

        # --- 2. Engagement Velocity ---
        total_eng_per_post = avg_likes + avg_comments + avg_shares
        velocity = svc.calculate_engagement_velocity(
            post_engagements=post_engagements if post_engagements else None,
            total_engagement=total_eng_per_post,
            posts_count=posts_count,
        )

        # --- 3. Outlier Handling ---
        raw_engs = [p.get("engagement", 0) for p in post_engagements] if post_engagements else []
        robust_stats = svc.robust_engagement_stats(
            post_engagements=raw_engs if raw_engs else None,
            avg_engagement=total_eng_per_post,
        )

        if robust_stats["outliers_removed"] > 0 and followers > 0:
            adjusted_er = round((robust_stats["trimmed_mean"] / followers) * 100, 2)
        else:
            adjusted_er = er

        # --- 4. Sigmoid score (per-tier) ---
        tier = _get_tier(followers)
        sigmoid_er_score = sigmoid_score(adjusted_er, tier["threshold"])

        # --- 5a. Social Score (legacy) ---
        comment_quality = 5.0
        if comment_analysis["total_analyzed"] > 0:
            comment_quality = (
                (comment_analysis["positive_pct"] / 10.0) * 0.4
                + ((100 - comment_analysis["bot_pct"]) / 10.0) * 0.3
                + min(comment_analysis["avg_length"] / 50.0, 1.0) * 10.0 * 0.3
            )
            comment_quality = round(min(max(comment_quality, 0.0), 10.0), 2)

        social_score = svc.calculate_social_score(
            engagement_rate=adjusted_er,
            fake_pct=fake_pct,
            comment_quality=comment_quality,
            followers=followers,
        )

        # --- 6. Conversion Score (legacy) ---
        intent_comment_count = buyer_intent["distribution"].get("achat_direct", 0)
        conversion_score_legacy = svc.calculate_conversion_score(
            saves=avg_saves,
            intent_comments=float(intent_comment_count),
            shares=avg_shares,
            views=avg_views,
        )

        # --- 5b. Business Score (legacy) ---
        business_score_legacy = svc.calculate_business_score(
            conversion_score=conversion_score_legacy,
            buyer_intent_coeff=buyer_intent["weighted_coefficient"],
        )

        # --- Legacy overall ---
        overall_score_legacy = round(social_score * 0.55 + business_score_legacy * 0.45, 2)

        legacy_overall = svc.calculate_overall_score(
            engagement_rate=er,
            fake_pct=fake_pct,
            comment_quality=comment_quality,
        )

        # --- 7. Confidence Score ---
        metrics_coherent = True
        if avg_likes > 0 and avg_comments > avg_likes * 5:
            metrics_coherent = False
        if er > 30:
            metrics_coherent = False

        confidence = svc.calculate_confidence(
            posts_analyzed=robust_stats["sample_size"] or posts_count,
            has_comments=len(comments) > 0,
            has_views=avg_views > 0,
            has_saves=avg_saves > 0,
            has_shares=avg_shares > 0,
            has_timestamps=any(p.get("timestamp") for p in post_engagements),
            metrics_coherent=metrics_coherent,
        )

        # ═══════════════════════════════════════════
        # v6 — NEW ROI SCORES (from EngagementCalculator v6)
        # ═══════════════════════════════════════════

        from app.services.engagement_calculator import EngagementCalculator

        calc = EngagementCalculator()

        # Build PostMetrics from post_engagements data
        from app.services.engagement_calculator import PostMetrics as PM
        calc_posts = []
        for p in post_engagements:
            calc_posts.append(PM(
                likes=int(p.get("likes", p.get("engagement", 0) * 0.7)),
                comments=int(p.get("comments_count", p.get("engagement", 0) * 0.15)),
                shares=int(p.get("shares", 0)),
                saves=int(p.get("saves", 0)),
                views=int(p.get("views", 0)),
                timestamp=p.get("timestamp"),
                caption=p.get("caption", ""),
                comment_texts=p.get("comment_texts", []),
            ))

        # If no per-post data, build a synthetic single post from averages
        if not calc_posts and followers > 0:
            calc_posts = [PM(
                likes=int(avg_likes),
                comments=int(avg_comments),
                shares=int(avg_shares),
                saves=int(avg_saves),
                views=int(avg_views),
            )]

        # Estimate account age in weeks from post timestamps
        account_age_weeks = 0.0
        timestamps = [p.get("timestamp") for p in post_engagements if p.get("timestamp")]
        if len(timestamps) >= 2:
            import time
            sorted_ts = sorted(timestamps)
            span_seconds = sorted_ts[-1] - sorted_ts[0]
            account_age_weeks = max(span_seconds / (7 * 86400), 1.0)

        # Get intent weights from comment_intent module
        intent_avg_weight = 1.0
        buyer_intent_score_v6 = 0.0
        if dm_intent_report:
            intent_avg_weight = dm_intent_report.get("avg_intent_weight", 1.0)
            buyer_intent_score_v6 = dm_intent_report.get("buyer_intent_score", 0.0)

        # Run the v6 calculator
        v6_report = calc.calculate(
            posts=calc_posts,
            followers=followers,
            platform=platform,
            intent_avg_weight=intent_avg_weight,
            buyer_intent_score=buyer_intent_score_v6,
            dm_intent_score=dm_intent_score,
            posts_count=posts_count,
            account_age_weeks=account_age_weeks,
            fake_pct=fake_pct,
            all_comment_texts=comments,
        )

        # --- Build the final response (backward compatible + v6 fields) ---
        result = {
            # Profile info
            "username": profile_data.get("username", ""),
            "platform": platform,
            "followers_count": followers,
            "following_count": following,
            "posts_count": posts_count,
            "full_name": profile_data.get("full_name"),
            "bio": profile_data.get("bio"),
            "profile_pic_url": profile_data.get("profile_pic_url"),
            "is_verified": profile_data.get("is_verified", False),
            "zone_operation": zone,

            # Core engagement (existing)
            "engagement_rate": er,
            "adjusted_engagement_rate": adjusted_er,
            "engagement_stats": robust_stats,

            # Legacy scores (backward compatible)
            "social_score": social_score,
            "business_score": business_score_legacy,
            "overall_score": overall_score_legacy,
            "legacy_overall_score": legacy_overall,
            "sigmoid_er_score": sigmoid_er_score,
            "conversion_score": conversion_score_legacy,

            # Buyer intent (legacy)
            "buyer_intent": buyer_intent,

            # Engagement velocity
            "engagement_velocity": velocity,

            # Fake followers
            "fake_followers_pct": fake_pct,

            # Comment analysis
            "comment_analysis": comment_analysis,
            "comment_quality_score": comment_quality,

            # Demographics
            "demographics": demographics,

            # Confidence
            "confidence": confidence,

            # Tier info
            "tier": {
                "name": next(
                    (name for name, t in ENGAGEMENT_TIERS.items()
                     if t["min_followers"] <= followers < t["max_followers"]),
                    "mega",
                ),
                "threshold": tier["threshold"],
            },

            # ═══════════════════════════════════════
            # v6 — NEW ROI FIELDS
            # ═══════════════════════════════════════
            "dm_intent_score": round(dm_intent_score, 1),
            "dm_intent_report": dm_intent_report,
            "view_ratio": v6_report.view_ratio,
            "view_ratio_score": v6_report.view_ratio_score,
            "local_score": v6_report.local_audience_score,
            "conversion_score_v6": v6_report.conversion_score,
            "posting_frequency": v6_report.posting_frequency,
            "posting_frequency_score": v6_report.posting_frequency_score,
            "giveaway_detected": v6_report.giveaway_detected,

            # v6 composite scores
            "business_score_v6": v6_report.business_score,
            "social_score_v6": v6_report.social_score,
            "authenticity_score": v6_report.authenticity_score,
            "overall_score_v6": v6_report.overall_score,
            "classification": v6_report.classification,
        }

        return result
