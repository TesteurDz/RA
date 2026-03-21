"""
ra/backend/app/services/comment_intent.py

v6.0 — Enhanced comment classification with DM/intent detection.
5 categories: achat_direct, interet, dm_request, neutre, spam
Algerian darija + FR + EN + Arabic script support.

Each category has a ROI weight used in conversion scoring.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class IntentCategory(str, Enum):
    ACHAT_DIRECT = "achat_direct"   # "prix?", "chhal?", "commander", "livraison"
    INTERET = "interet"              # "dispo?", "kayen?", "combien?"
    DM_REQUEST = "dm_request"        # "whatsapp", "dm", "inbox", "واتساب"
    NEUTRE = "neutre"                # normal comment, no purchase signal
    SPAM = "spam"                    # bots, f4f, promo


# ROI weights — higher = stronger purchase signal
INTENT_WEIGHTS = {
    IntentCategory.ACHAT_DIRECT: 2.5,
    IntentCategory.INTERET: 1.5,
    IntentCategory.DM_REQUEST: 3.0,
    IntentCategory.NEUTRE: 1.0,
    IntentCategory.SPAM: 0.3,
}


@dataclass
class CommentIntent:
    text: str
    category: IntentCategory
    weight: float
    matched_pattern: str = ""


# ═══════════════════════════════════════════
# Keyword patterns by category (FR + Darija + EN + Arabic)
# ═══════════════════════════════════════════

# --- achat_direct (weight 2.5): direct purchase signals ---
ACHAT_DIRECT_PATTERNS = [
    # FR
    r"(je\s*(veux|voudrais|souhaite)\s*(acheter|commander|prendre|r[eé]server))",
    r"(comment\s*(commander|acheter|payer|r[eé]server))",
    r"(livr(aison|ez|e)\s*(où|comment|disponible)?)",
    r"(envoy(ez|e)\s*(moi|en)\s*(dm|priv[eé]|inbox|message))",
    r"(je\s*(prends?|commande))",
    r"(c.est\s*combien)",
    r"(lien\s*(d.achat|pour\s*acheter|svp))",
    r"\b(prix|tarif)\s*(\?|svp|stp|please)?",
    r"\b(combien)\b",
    r"\b(commander)\b",
    r"\b(livraison)\b",
    r"\b(numero|num[eé]ro)\b",
    r"\b(tel|t[eé]l[eé]phone)\b",
    # AR darija
    r"(bch[hh]al|beshhal|chhal|9addash|gaddach|kidayr\s*el\s*prix)",
    r"(bghit\s*(nchri|nachri|nakhod|ncommandi))",
    r"(ki(fash|faش)\s*(nchri|nachri|ncommandi|ndirha))",
    r"(rani\s*(hab|baghi|bghit)\s*(nachri|nchri|nakhod))",
    r"(3tini|aatini|envoyili)\s*(prix|tarif|lien)",
    # EN
    r"(how\s*(much|to\s*(buy|order|get)))",
    r"(where\s*(can\s*i|to)\s*(buy|order|get))",
    r"(i\s*(want|need)\s*to\s*(buy|order|get))",
    r"(price|cost)\s*\??",
    r"(send\s*(me\s*)?(dm|link|price))",
    r"(is\s*(this|it)\s*(available|in\s*stock))",
    r"(can\s*i\s*(order|buy|get))",
    r"(i.ll\s*take\s*(it|one|this))",
    r"(shut\s*up\s*and\s*take\s*my\s*money)",
]

# --- interet (weight 1.5): interest/curiosity signals ---
INTERET_PATTERNS = [
    # FR
    r"(j.adore|j.aime\s*(trop|beaucoup|bien))",
    r"(trop\s*(beau|belle|bien|styl[eé]|cool|canon))",
    r"(il\s*(me\s*)?(le\s*)?faut)",
    r"(je\s*(kiffe|r[eê]ve|craque))",
    r"(où\s*(trouver|acheter|c.est))",
    r"(ça\s*(donne|a\s*l.air)\s*(trop\s*)?envie)",
    r"(quelle\s*(marque|r[eé]f[eé]rence|taille|couleur))",
    r"(c.est\s*(quoi|quelle)\s*(la\s*)?(marque|r[eé]f))",
    r"\b(dispo|disponible)\b",
    r"\b(kayen)\b",
    r"(wach\s*kayen)",
    r"(wach\s*(3andkom|3endkom|andkom)\s*(khra|autre|taille|couleur))",
    # AR darija
    r"(3jbatni|3ajbatni|ajbatni|waaw|yaaah)",
    r"(fin\s*(nlga|nlgaha|nla9aha|nchriha))",
    r"(hadi\s*(top|hbitha|zwin|zwina))",
    r"(lazimni|khassni|baghi)\s*(had|hadi|hedhi)",
    # EN
    r"(i\s*(love|need|want)\s*(this|it))",
    r"(where\s*(is|did\s*you)\s*(this|get))",
    r"(what\s*(brand|size|color|ref))",
    r"(looks?\s*(amazing|great|fire|sick).*(\bi\s*need))",
    r"(omg\s*(i\s*)?(need|want))",
    r"(take\s*my\s*money)",
    r"(adding\s*to\s*(my\s*)?(cart|wishlist))",
]

# --- dm_request (weight 3.0): strongest purchase signal ---
DM_REQUEST_PATTERNS = [
    # FR + EN
    r"\b(whatsapp)\b",
    r"\b(dm)\b",
    r"\b(inbox)\b",
    r"\b(message\s*priv[eé]?)\b",
    r"\b(num)\b",
    r"(envoi(e|ez)?\s*(moi\s*)?(ton|votre|le)?\s*(num|whatsapp|numero))",
    r"(donne\s*(moi\s*)?(ton|votre|le)?\s*(num|whatsapp|numero))",
    # Arabic script
    r"(واتساب|واتس|وتساب)",
    r"(رقم)",
    r"(خاص|الخاص)",
    r"(ارسل|ابعث)\s*(لي|رقم)",
]

# --- spam (weight 0.3): bot/promo noise ---
SPAM_PATTERNS = [
    r"(follow\s*(me|back|4follow))",
    r"(f4f|l4l|s4s)",
    r"(check\s*(my|out)\s*(page|profile|bio|link))",
    r"(dm\s*(me|for)\s*(collab|promo|business))",
    r"(free\s*followers)",
    r"(grow\s*your\s*(page|account|followers))",
    r"(visit\s*(my|link|bio))",
    r"(click\s*(link|bio))",
    r"(i\s*can\s*help\s*you\s*(grow|get))",
    r"(promo\s*(code|offer|deal))",
    r"(earn\s*money|make\s*\$)",
    r"(subscribe\s*(to\s*)?my)",
    # Generic 1-word bot comments
    r"^(nice|cool|great|wow|fire|love|beautiful|amazing|gorgeous)[\s!.]*$",
    # Emoji-only (1-5 emojis)
    r"^[\U0001f600-\U0001f64f\U0001f300-\U0001f5ff\U0001f680-\U0001f6ff\U0001f1e0-\U0001f1ff\u2600-\u26ff\u2700-\u27bf]{1,5}$",
]


def _compile_patterns(patterns: list[str]):
    return [re.compile(p, re.IGNORECASE | re.UNICODE) for p in patterns]


_ACHAT_RE = _compile_patterns(ACHAT_DIRECT_PATTERNS)
_INTERET_RE = _compile_patterns(INTERET_PATTERNS)
_DM_RE = _compile_patterns(DM_REQUEST_PATTERNS)
_SPAM_RE = _compile_patterns(SPAM_PATTERNS)


def classify_comment(text: str) -> CommentIntent:
    """
    Classify a single comment by purchase intent.
    Priority: dm_request > achat_direct > interet > spam > neutre
    """
    clean = text.strip()
    if not clean:
        return CommentIntent(text=text, category=IntentCategory.SPAM, weight=INTENT_WEIGHTS[IntentCategory.SPAM])

    lower = clean.lower()

    # DM requests are the strongest signal — check first
    for pattern in _DM_RE:
        m = pattern.search(lower)
        if m:
            return CommentIntent(
                text=text, category=IntentCategory.DM_REQUEST,
                weight=INTENT_WEIGHTS[IntentCategory.DM_REQUEST],
                matched_pattern=m.group(0),
            )

    # Direct purchase intent
    for pattern in _ACHAT_RE:
        m = pattern.search(lower)
        if m:
            return CommentIntent(
                text=text, category=IntentCategory.ACHAT_DIRECT,
                weight=INTENT_WEIGHTS[IntentCategory.ACHAT_DIRECT],
                matched_pattern=m.group(0),
            )

    # Interest / curiosity
    for pattern in _INTERET_RE:
        m = pattern.search(lower)
        if m:
            return CommentIntent(
                text=text, category=IntentCategory.INTERET,
                weight=INTENT_WEIGHTS[IntentCategory.INTERET],
                matched_pattern=m.group(0),
            )

    # Spam / bot
    for pattern in _SPAM_RE:
        m = pattern.search(lower)
        if m:
            return CommentIntent(
                text=text, category=IntentCategory.SPAM,
                weight=INTENT_WEIGHTS[IntentCategory.SPAM],
                matched_pattern=m.group(0),
            )

    # Very short comments (<=3 chars) = spam
    if len(clean) <= 3:
        return CommentIntent(text=text, category=IntentCategory.SPAM, weight=INTENT_WEIGHTS[IntentCategory.SPAM])

    return CommentIntent(text=text, category=IntentCategory.NEUTRE, weight=INTENT_WEIGHTS[IntentCategory.NEUTRE])


@dataclass
class IntentReport:
    total: int = 0
    achat_direct_count: int = 0
    interet_count: int = 0
    dm_request_count: int = 0
    neutre_count: int = 0
    spam_count: int = 0
    achat_direct_pct: float = 0.0
    interet_pct: float = 0.0
    dm_request_pct: float = 0.0
    neutre_pct: float = 0.0
    spam_pct: float = 0.0
    avg_intent_weight: float = 1.0     # weighted average for engagement calc
    buyer_intent_score: float = 0.0    # 0-10 synthetic purchase intent score
    dm_intent_score: float = 0.0       # 0-10 DM/conversion intent score
    sample_achat: list = None
    sample_interet: list = None
    sample_dm: list = None


def analyze_comment_intents(comments: list[str]) -> IntentReport:
    """
    Analyze a list of comments and return a full intent report.
    Includes the new dm_intent_score for ROI scoring.
    """
    if not comments:
        return IntentReport()

    results = [classify_comment(c) for c in comments]
    total = len(results)

    counts = {cat: 0 for cat in IntentCategory}
    weights_sum = 0.0
    samples_achat = []
    samples_interet = []
    samples_dm = []

    for r in results:
        counts[r.category] += 1
        weights_sum += r.weight
        if r.category == IntentCategory.ACHAT_DIRECT and len(samples_achat) < 5:
            samples_achat.append(r.text[:100])
        elif r.category == IntentCategory.INTERET and len(samples_interet) < 5:
            samples_interet.append(r.text[:100])
        elif r.category == IntentCategory.DM_REQUEST and len(samples_dm) < 5:
            samples_dm.append(r.text[:100])

    avg_weight = weights_sum / total

    achat_pct = (counts[IntentCategory.ACHAT_DIRECT] / total) * 100
    interet_pct = (counts[IntentCategory.INTERET] / total) * 100
    dm_pct = (counts[IntentCategory.DM_REQUEST] / total) * 100

    # Buyer Intent Score (0-10): achat_direct + interet signals
    # Formula: (achat% * 3 + interet% * 1.5) capped at 10
    buyer_intent_score = min((achat_pct * 3.0 + interet_pct * 1.5) / 10.0, 10.0)

    # DM Intent Score (0-10): strongest ROI signal
    # dm_intent_score = (achat_direct + interet + dm_requests) / total_comments
    # Normalized: high % of intent comments = high score
    intent_total = counts[IntentCategory.ACHAT_DIRECT] + counts[IntentCategory.INTERET] + counts[IntentCategory.DM_REQUEST]
    dm_intent_ratio = intent_total / total  # 0-1

    # Scale with DM weight bonus: DMs count 2x in the score
    dm_weighted_ratio = (
        counts[IntentCategory.ACHAT_DIRECT] * 1.0
        + counts[IntentCategory.INTERET] * 0.8
        + counts[IntentCategory.DM_REQUEST] * 2.0
    ) / total

    # Sigmoid normalize to 0-10 (midpoint at 0.15 ratio = score 5)
    import math
    dm_intent_score = 10.0 / (1.0 + math.exp(-8.0 * (dm_weighted_ratio - 0.15)))
    dm_intent_score = round(min(dm_intent_score, 10.0), 1)

    return IntentReport(
        total=total,
        achat_direct_count=counts[IntentCategory.ACHAT_DIRECT],
        interet_count=counts[IntentCategory.INTERET],
        dm_request_count=counts[IntentCategory.DM_REQUEST],
        neutre_count=counts[IntentCategory.NEUTRE],
        spam_count=counts[IntentCategory.SPAM],
        achat_direct_pct=round(achat_pct, 1),
        interet_pct=round(interet_pct, 1),
        dm_request_pct=round(dm_pct, 1),
        neutre_pct=round((counts[IntentCategory.NEUTRE] / total) * 100, 1),
        spam_pct=round((counts[IntentCategory.SPAM] / total) * 100, 1),
        avg_intent_weight=round(avg_weight, 3),
        buyer_intent_score=round(buyer_intent_score, 1),
        dm_intent_score=dm_intent_score,
        sample_achat=samples_achat,
        sample_interet=samples_interet,
        sample_dm=samples_dm,
    )
