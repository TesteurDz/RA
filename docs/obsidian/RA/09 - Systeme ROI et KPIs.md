# Systeme ROI et KPIs - Specs detaillees

> Reference technique pour implementation Phase 3

---

## KPIs par categorie

### A. Engagement (30% du score)
- Taux d engagement ajuste par taille (voir table normalisation dans Roadmap)
- Ratio likes/comments : comments / likes x 100 (bon si > 3%)
- Taux de partage : shares / total_engagement x 100
- Constance : 1 - (ecart_type_ER / moyenne_ER) sur 20 posts

### B. Authenticite (25% du score)
- Pourcentage faux followers (heuristiques multi-criteres)
- Pourcentage commentaires bots
- Ratio followers/following (normal: 2-50)
- Qualite commentaires (longueur > 15 chars, 80%+ uniques)

### C. Pertinence Audience (20% du score)
- Match geographique : audience dans la zone cible
- Match demographique : age/genre vs cible produit
- Match linguistique : audience comprend la langue du contenu

### D. Performance Contenu (15% du score)
- Frequence : 3-7 posts/semaine = optimal
- Constance ER
- Performance sponsorisee vs organique (ratio > 0.7 = bon)

### E. Prediction ROI (10% du score)
- CPE estime : tarif / engagements
- Taux de conversion dynamique (via CPS)
- Comparaison vs Facebook Ads (benchmark CPE DZ: 15-30 DA)

---

## Conversion Potential Score (CPS)

Remplace le taux fixe de 2% par un modele dynamique.

Ponderations:
- Buyer Intent Score: 25%
- Save Rate: 20%
- Content Fit: 15%
- Authenticite: 15%
- Audience Match: 10%
- Engagement: 10%
- Completion Rate: 5%

Mapping CPS vers taux de conversion:
- CPS 90+ : 5-8%
- CPS 70-90 : 2-5%
- CPS 50-70 : 0.8-2%
- CPS 30-50 : 0.3-0.8%
- CPS < 30 : 0.05-0.3%

Multiplicateurs niche: Food x1.3, Beauty x1.2, Fashion x1.1, Tech x0.8, Fitness x0.9

---

## Buyer Intent Score

Classification des commentaires:

| Categorie | Poids | Exemples FR/AR/EN |
|-----------|-------|-------------------|
| PURCHASE | 1.0 | prix? ou acheter? lien svp / بشحال وين نشريه |
| INTEREST | 0.4 | trop beau je veux / نبغيه عجبني |
| NEUTRAL | 0.05 | nice, emoji, tag ami |
| SPAM | 0.0 | follow me, f4f, check my page |

Formule: BIS = (purchase x 1.0 + interest x 0.4 + neutral x 0.05) / non_spam x 10

---

## Confidence Score (0-100%)

| Data disponible | Points |
|----------------|--------|
| Base (profil) | +30 |
| Save rate | +12 |
| Buyer intent (comments) | +10 |
| Completion rate | +8 |
| Tarif reel fourni | +5 |
| Prix produit fourni | +5 |
| 100+ commentaires | +5 |
| 15+ posts analyses | +5 |
| Historique campagnes | +20 |

---

## Verdicts

| Score | Verdict | Action |
|-------|---------|--------|
| 80+ | INVESTIR | ROI quasi garanti, negocier package |
| 60-79 | TESTER | Un post test avant d investir |
| 40-59 | PRUDENCE | Risque eleve |
| 0-39 | EVITER | Ne pas collaborer |
