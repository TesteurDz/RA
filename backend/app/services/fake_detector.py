"""
ra/backend/app/services/fake_detector.py

Detection de faux followers amelioree.
Combine 8 signaux ponderes pour estimer le % de faux.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import logging
import math

logger = logging.getLogger(__name__)


@dataclass
class FakeSignal:
    name: str
    score: float        # 0-100 contribution
    weight: float       # poids dans le total
    detail: str


@dataclass
class FakeFollowersReport:
    fake_pct: float                     # 0-95%
    confidence: float                   # 0-1
    risk_level: str                     # low, medium, high, critical
    signals: list[FakeSignal] = field(default_factory=list)
    breakdown: dict = field(default_factory=dict)


class FakeFollowerDetector:
    """
    8 signaux ponderes pour detecter les faux followers.
    
    1. Engagement vs taille        (25%) — le signal principal
    2. Followers/Following ratio   (10%) — mass follow ou achete
    3. Posts vs followers           (10%) — peu de contenu, beaucoup de followers
    4. Consistency d'engagement     (15%) — engagement irregulier = suspect
    5. Comment/Like ratio          (10%) — trop peu de comments = bots
    6. Nombre rond de followers    (5%)  — 50000 pile = achat
    7. Croissance vs contenu       (10%) — beaucoup de followers, peu d'activite
    8. Engagement par vue vs follower (15%) — ecart = faux followers
    """
    
    # Benchmarks d'engagement par taille (tier)
    # Format: (max_followers, expected_min_er, suspicious_er, dead_er)
    ER_BENCHMARKS = [
        (1_000,       3.0,  1.5,  0.5),   # Nano
        (5_000,       2.5,  1.2,  0.4),
        (10_000,      2.0,  1.0,  0.3),   # Micro
        (25_000,      1.8,  0.8,  0.25),
        (50_000,      1.5,  0.7,  0.2),
        (100_000,     1.2,  0.5,  0.15),  # Mid
        (250_000,     1.0,  0.4,  0.1),
        (500_000,     0.8,  0.3,  0.08),  # Macro
        (1_000_000,   0.6,  0.25, 0.06),
        (5_000_000,   0.4,  0.15, 0.04),  # Mega
        (10_000_000,  0.3,  0.1,  0.03),
        (float('inf'), 0.2, 0.08, 0.02),  # Celebrity
    ]
    
    def detect(
        self,
        followers: int,
        following: int,
        posts_count: int,
        engagement_rate: float,
        platform: str = "instagram",
        # Donnees optionnelles du nouveau EngagementCalculator
        consistency: float = None,
        comment_like_ratio: float = None,
        er_by_views: float = None,
        er_by_followers: float = None,
        views_followers_ratio: float = None,
        is_verified: bool = False,
    ) -> FakeFollowersReport:
        
        if followers == 0:
            return FakeFollowersReport(fake_pct=0, confidence=0, risk_level="low")
        
        signals = []
        
        # ═══════════════════════════════════════
        # Signal 1: Engagement vs taille (25%)
        # ═══════════════════════════════════════
        s1 = self._signal_engagement_vs_size(
            followers, engagement_rate, platform, is_verified
        )
        signals.append(s1)
        
        # ═══════════════════════════════════════
        # Signal 2: Followers/Following ratio (10%)
        # ═══════════════════════════════════════
        s2 = self._signal_ff_ratio(followers, following, engagement_rate)
        signals.append(s2)
        
        # ═══════════════════════════════════════
        # Signal 3: Posts vs followers (10%)
        # ═══════════════════════════════════════
        s3 = self._signal_posts_vs_followers(followers, posts_count)
        signals.append(s3)
        
        # ═══════════════════════════════════════
        # Signal 4: Consistency (15%)
        # ═══════════════════════════════════════
        s4 = self._signal_consistency(consistency)
        signals.append(s4)
        
        # ═══════════════════════════════════════
        # Signal 5: Comment/Like ratio (10%)
        # ═══════════════════════════════════════
        s5 = self._signal_comment_ratio(comment_like_ratio, platform)
        signals.append(s5)
        
        # ═══════════════════════════════════════
        # Signal 6: Nombre rond (5%)
        # ═══════════════════════════════════════
        s6 = self._signal_round_number(followers)
        signals.append(s6)
        
        # ═══════════════════════════════════════
        # Signal 7: Croissance vs contenu (10%)
        # ═══════════════════════════════════════
        s7 = self._signal_growth_vs_content(followers, posts_count, engagement_rate)
        signals.append(s7)
        
        # ═══════════════════════════════════════
        # Signal 8: ER views vs ER followers (15%)
        # ═══════════════════════════════════════
        s8 = self._signal_views_vs_followers(
            er_by_views, er_by_followers, views_followers_ratio
        )
        signals.append(s8)
        
        # ═══════════════════════════════════════
        # Score final pondere
        # ═══════════════════════════════════════
        
        total_weight = 0
        weighted_sum = 0
        available_signals = 0
        
        for s in signals:
            if s.score >= 0:  # -1 = pas de data
                weighted_sum += s.score * s.weight
                total_weight += s.weight
                available_signals += 1
        
        if total_weight > 0:
            # Normaliser pour que les poids disponibles = 100%
            fake_pct = (weighted_sum / total_weight)
        else:
            fake_pct = 0
        
        fake_pct = min(round(fake_pct, 1), 95.0)
        
        # Confidence basee sur le nombre de signaux disponibles
        confidence = round(available_signals / len(signals), 2)
        
        # Risk level
        if fake_pct >= 60:
            risk = "critical"
        elif fake_pct >= 35:
            risk = "high"
        elif fake_pct >= 15:
            risk = "medium"
        else:
            risk = "low"
        
        return FakeFollowersReport(
            fake_pct=fake_pct,
            confidence=confidence,
            risk_level=risk,
            signals=signals,
            breakdown={s.name: round(s.score, 1) for s in signals if s.score >= 0},
        )
    
    def _get_er_benchmark(self, followers: int):
        for max_f, expected, suspicious, dead in self.ER_BENCHMARKS:
            if followers < max_f:
                return expected, suspicious, dead
        return 0.2, 0.08, 0.02
    
    def _signal_engagement_vs_size(self, followers, er, platform, is_verified) -> FakeSignal:
        """
        Le signal le plus important.
        Compare l'ER reel aux benchmarks pour cette taille de compte.
        """
        expected, suspicious, dead = self._get_er_benchmark(followers)
        
        # TikTok a des taux plus eleves naturellement
        if platform == "tiktok":
            expected *= 2
            suspicious *= 2
            dead *= 2
        
        # Les comptes verifies ont naturellement un ER plus bas
        if is_verified:
            expected *= 0.7
            suspicious *= 0.7
            dead *= 0.7
        
        if er >= expected:
            score = 0
            detail = f"ER {er:.2f}% normal pour {followers} followers"
        elif er >= suspicious:
            score = 25 + (1 - (er - suspicious) / (expected - suspicious)) * 25
            detail = f"ER {er:.2f}% un peu bas (attendu > {expected:.1f}%)"
        elif er >= dead:
            score = 50 + (1 - (er - dead) / (suspicious - dead)) * 25
            detail = f"ER {er:.2f}% suspect (attendu > {suspicious:.1f}%)"
        else:
            score = 75 + min((1 - er / max(dead, 0.01)) * 20, 20)
            detail = f"ER {er:.2f}% critique (minimum attendu {dead:.2f}%)"
        
        return FakeSignal(name="engagement_vs_size", score=min(score, 95), weight=0.25, detail=detail)
    
    def _signal_ff_ratio(self, followers, following, er) -> FakeSignal:
        """
        Ratio followers/following.
        Normal: 1-50
        Mass-follow (follow/unfollow): following >> followers
        Achete: followers >> following ET engagement bas
        """
        if following == 0:
            following = 1
        ratio = followers / following
        
        score = 0
        if ratio > 500 and er < 1.0:
            score = 60
            detail = f"Ratio {ratio:.0f}:1 avec ER {er:.2f}% = probable achat"
        elif ratio > 200 and er < 1.5:
            score = 40
            detail = f"Ratio {ratio:.0f}:1 eleve avec engagement faible"
        elif following > followers * 2:
            score = 30
            detail = f"Suit {following} comptes pour {followers} followers (mass-follow)"
        elif following > followers * 1.5:
            score = 15
            detail = f"Following/followers desequilibre ({following}/{followers})"
        else:
            detail = f"Ratio {ratio:.1f}:1 normal"
        
        return FakeSignal(name="ff_ratio", score=score, weight=0.10, detail=detail)
    
    def _signal_posts_vs_followers(self, followers, posts) -> FakeSignal:
        """
        Peu de posts mais beaucoup de followers = suspect.
        Ratio normal: ~100-500 followers par post pour les petits comptes.
        """
        if posts == 0:
            if followers > 1000:
                return FakeSignal(
                    name="posts_vs_followers", score=80, weight=0.10,
                    detail=f"{followers} followers mais 0 posts"
                )
            return FakeSignal(name="posts_vs_followers", score=0, weight=0.10, detail="Nouveau compte")
        
        ratio = followers / posts  # followers par post
        
        if ratio > 5000 and posts < 20:
            score = 70
            detail = f"{followers} followers avec seulement {posts} posts ({ratio:.0f} followers/post)"
        elif ratio > 2000 and posts < 50:
            score = 45
            detail = f"Ratio {ratio:.0f} followers/post eleve"
        elif ratio > 1000 and posts < 30:
            score = 25
            detail = f"Ratio {ratio:.0f} followers/post un peu haut"
        else:
            score = 0
            detail = f"Ratio {ratio:.0f} followers/post normal"
        
        return FakeSignal(name="posts_vs_followers", score=score, weight=0.10, detail=detail)
    
    def _signal_consistency(self, consistency) -> FakeSignal:
        """
        Engagement irregulier = audience pas organique.
        Un vrai public donne un engagement stable (consistency > 0.5).
        Bots ou achat = tres variable (consistency < 0.2).
        """
        if consistency is None:
            return FakeSignal(name="consistency", score=-1, weight=0.15, detail="Pas de donnees")
        
        if consistency >= 0.6:
            score = 0
            detail = f"Engagement stable ({consistency:.2f})"
        elif consistency >= 0.4:
            score = 15
            detail = f"Engagement moderement variable ({consistency:.2f})"
        elif consistency >= 0.2:
            score = 35
            detail = f"Engagement irregulier ({consistency:.2f}) — possible achat partiel"
        else:
            score = 60
            detail = f"Engagement tres irregulier ({consistency:.2f}) — audience suspecte"
        
        return FakeSignal(name="consistency", score=score, weight=0.15, detail=detail)
    
    def _signal_comment_ratio(self, comment_like_ratio, platform) -> FakeSignal:
        """
        Ratio comments/likes.
        Trop peu de comments = followers bots (ils likent mais ne commentent pas).
        Normal Instagram: 1-5%
        Normal TikTok: 0.5-3%
        """
        if comment_like_ratio is None:
            return FakeSignal(name="comment_ratio", score=-1, weight=0.10, detail="Pas de donnees")
        
        if platform == "tiktok":
            thresholds = (2.0, 0.8, 0.3)
        else:
            thresholds = (3.0, 1.0, 0.3)
        
        good, low, dead = thresholds
        
        if comment_like_ratio >= good:
            score = 0
            detail = f"Ratio comments/likes {comment_like_ratio:.1f}% sain"
        elif comment_like_ratio >= low:
            score = 15
            detail = f"Ratio comments/likes {comment_like_ratio:.1f}% un peu bas"
        elif comment_like_ratio >= dead:
            score = 40
            detail = f"Ratio comments/likes {comment_like_ratio:.1f}% faible — peu d'interaction reelle"
        else:
            score = 65
            detail = f"Ratio comments/likes {comment_like_ratio:.1f}% critique — audience passive/bots"
        
        return FakeSignal(name="comment_ratio", score=score, weight=0.10, detail=detail)
    
    def _signal_round_number(self, followers) -> FakeSignal:
        """
        Nombre de followers tres rond = possible achat.
        50000, 100000, 200000 pile = suspect.
        """
        if followers < 5000:
            return FakeSignal(name="round_number", score=0, weight=0.05, detail="Petit compte, non applicable")
        
        follower_str = str(followers)
        trailing_zeros = len(follower_str) - len(follower_str.rstrip("0"))
        
        # Verifier aussi les multiples de 1000/5000/10000
        is_exact_thousand = followers % 1000 == 0
        is_exact_5k = followers % 5000 == 0
        is_exact_10k = followers % 10000 == 0
        
        if is_exact_10k and followers >= 10000:
            score = 30
            detail = f"{followers} est un multiple exact de 10K"
        elif is_exact_5k and followers >= 10000:
            score = 20
            detail = f"{followers} est un multiple exact de 5K"
        elif trailing_zeros >= 3 and followers >= 10000:
            score = 15
            detail = f"{followers} a {trailing_zeros} zeros finaux"
        else:
            score = 0
            detail = f"{followers} n'est pas un nombre suspect"
        
        return FakeSignal(name="round_number", score=score, weight=0.05, detail=detail)
    
    def _signal_growth_vs_content(self, followers, posts, er) -> FakeSignal:
        """
        Beaucoup de followers mais tres peu d'activite recente
        + engagement bas = croissance non organique.
        """
        if posts == 0 or followers < 1000:
            return FakeSignal(name="growth_vs_content", score=0, weight=0.10, detail="Non applicable")
        
        # Score composite: followers/post ratio * inverse de l'engagement
        followers_per_post = followers / posts
        
        if followers_per_post > 3000 and er < 1.0:
            score = 55
            detail = f"Croissance suspecte: {followers_per_post:.0f} followers/post avec ER {er:.2f}%"
        elif followers_per_post > 1500 and er < 1.5:
            score = 30
            detail = f"Croissance rapide vs engagement faible"
        elif followers_per_post > 500 and er < 0.5:
            score = 40
            detail = f"Engagement mort malgre un compte etabli"
        else:
            score = 0
            detail = "Croissance coherente avec le contenu"
        
        return FakeSignal(name="growth_vs_content", score=score, weight=0.10, detail=detail)
    
    def _signal_views_vs_followers(self, er_views, er_followers, vf_ratio) -> FakeSignal:
        """
        Si on a ER par views ET par followers, comparer les deux.
        Grand ecart = les followers ne regardent pas = faux.
        
        Aussi: views/followers ratio.
        TikTok normal: 0.5-3.0
        Instagram Reels normal: 0.2-1.0
        Si views/followers < 0.05 = personne ne voit le contenu = followers morts
        """
        if er_views is None or er_followers is None:
            # Fallback sur views/followers ratio
            if vf_ratio is not None:
                if vf_ratio < 0.05:
                    score = 50
                    detail = f"Views/Followers ratio {vf_ratio:.2f} — la majorite des followers ne voient rien"
                elif vf_ratio < 0.15:
                    score = 25
                    detail = f"Views/Followers ratio {vf_ratio:.2f} un peu bas"
                else:
                    score = 0
                    detail = f"Views/Followers ratio {vf_ratio:.2f} normal"
                return FakeSignal(name="views_vs_followers", score=score, weight=0.15, detail=detail)
            return FakeSignal(name="views_vs_followers", score=-1, weight=0.15, detail="Pas de donnees views")
        
        # Comparer ER views vs ER followers
        # Si ER followers est haut mais ER views est bas = les vues sont faibles = followers faux
        if er_followers > 0:
            ratio = er_views / er_followers
            # ratio > 1 = plus d'engagement par vue que par follower (normal/bon)
            # ratio < 0.5 = beaucoup de followers ne s'engagent pas
            if ratio < 0.3:
                score = 55
                detail = f"ER views ({er_views:.2f}%) vs followers ({er_followers:.2f}%) — gros ecart"
            elif ratio < 0.6:
                score = 30
                detail = f"Ecart modere entre ER views et followers"
            else:
                score = 0
                detail = f"ER views et followers coherents"
        else:
            score = 0
            detail = "ER followers nul"
        
        return FakeSignal(name="views_vs_followers", score=score, weight=0.15, detail=detail)
