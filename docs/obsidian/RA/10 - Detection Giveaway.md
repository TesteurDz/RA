# Detection Giveaway - Specs detaillees

> Reference technique pour implementation Phase 3

---

## Architecture

3 axes ponderes:
- Analyse textuelle (caption + hashtags) : 40%
- Analyse comportementale (ratios anormaux) : 35%
- Analyse commentaires (patterns participation) : 25%

---

## Mots-cles multilingues

### Francais
Strong: concours, giveaway, tirage au sort, jeu concours, cadeau a gagner
Medium: gagne, participe, tag 3 amis, mentionne, abonne-toi, like + commente

### Arabe (darija)
Strong: مسابقة كونكور جيفاواي سحب هدية للربح
Medium: شارك تاغي صحابك ابوني لايك+كومنت النتيجة غدا

### Anglais
Strong: giveaway, contest, raffle, sweepstakes, win this
Medium: tag a friend, follow + like, must follow, winner announced

---

## Signaux comportementaux

| Signal | Seuil | Points |
|--------|-------|--------|
| Comments > 5x moyenne | Strong | +35 |
| Comments > 3x moyenne | Medium | +20 |
| Ratio comments/likes > 0.5 | Strong | +30 |
| Ratio comments/likes > 0.2 | Medium | +15 |
| Saves tres bas vs likes | Medium | +15 |
| Likes > 4x moyenne | Medium | +15 |
| Multi-conditions (3+ actions) | Strong | +25 |

---

## Classification

| Score | Action | Weight |
|-------|--------|--------|
| 75+ | EXCLURE | 0.0 |
| 40-74 | PONDERER | 0.05-0.20 |
| < 40 | GARDER | 1.0 |

---

## Anti faux-positifs

Un post est viral organique (pas concours) si 4+ sur 5:
1. Commentaires longs (avg > 30 chars)
2. 80%+ commentaires uniques
3. Save rate eleve (> 0.05)
4. Share rate eleve (> 0.10)
5. Pas de mot-cle concours STRONG dans la caption
