from __future__ import annotations

import logging
import re
from collections import Counter
from typing import Any

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


class AnalyzerService:
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

        # Engagement-based scoring
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

        # Likes-to-followers ratio
        likes_ratio = avg_likes / followers if followers > 0 else 0
        if likes_ratio < 0.005 and followers > 10000:
            score += 20.0
        elif likes_ratio < 0.01 and followers > 5000:
            score += 10.0

        # Following/followers ratio
        if following > 0 and followers > 0:
            ratio = followers / following
            if ratio > 200 and engagement_rate < 1.0:
                score += 15.0

        # Suspiciously round numbers
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

            # Bot detection
            is_bot = False
            for pattern in BOT_PATTERNS:
                if re.search(pattern, comment_lower):
                    bot_count += 1
                    is_bot = True
                    break

            if not is_bot:
                # Very short generic comments are likely bots
                if len(comment_lower) <= 3:
                    bot_count += 1
                    is_bot = True

            # Simple sentiment analysis
            words = set(re.findall(r"\w+", comment_lower))
            pos_hits = len(words & POSITIVE_WORDS)
            neg_hits = len(words & NEGATIVE_WORDS)

            if pos_hits > neg_hits:
                positive_count += 1
            elif neg_hits > pos_hits:
                negative_count += 1
            else:
                neutral_count += 1

            # Basic language detection based on character sets
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
        # Without API access, we provide reasonable estimates
        # based on platform norms and Algerian social media patterns
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
    ) -> float:
        """
        Calculate overall influencer score from 0 to 10.

        Weights:
        - Engagement rate: 30%
        - Fake followers (inverted): 30%
        - Comment quality: 20%
        - Growth pattern: 20%
        """
        # Normalize engagement rate (0-10 scale, cap at 10% ER)
        engagement_score = min(engagement_rate / 10.0 * 10.0, 10.0)

        # Invert fake percentage (lower is better)
        authenticity_score = max(10.0 - (fake_pct / 10.0), 0.0)

        # Comment quality is already 0-10
        comment_score = min(max(comment_quality, 0.0), 10.0)

        # Growth pattern is already 0-10
        growth_score = min(max(growth_pattern, 0.0), 10.0)

        overall = (
            engagement_score * 0.30
            + authenticity_score * 0.30
            + comment_score * 0.20
            + growth_score * 0.20
        )

        return round(min(max(overall, 0.0), 10.0), 1)

    @staticmethod
    def detect_zone_operation(bio: str = "", location: str = "", hashtags: list = None) -> str:
        """Try to detect Algerian wilaya from bio, location, or hashtags."""
        hashtags = hashtags or []
        search_text = f"{bio} {location} {' '.join(hashtags)}".lower()

        # Check aliases first (more specific matches)
        for alias, wilaya in WILAYA_ALIASES.items():
            if alias in search_text:
                return wilaya

        # Check official names
        for wilaya in ALGERIAN_WILAYAS:
            if wilaya.lower() in search_text:
                return wilaya

        # Check for wilaya number patterns like "16" for Alger, "31" for Oran
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
