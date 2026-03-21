# Module Offline et Cash - Specs detaillees

> Reference technique pour implementation Phase 2

---

## Tracking offline

### Codes influenceurs
- Format: MARQUE_INFLUENCEUR (ex: BARA_SARA)
- Unique par influenceur par campagne
- Mentionne dans: video, caption, story

### Lien WhatsApp pre-rempli
- Le client clique, WhatsApp s ouvre avec message contenant le code
- En bio + story de l influenceur

### Sources trackees
WhatsApp, DM Instagram, DM TikTok, Appel, En magasin, Autre

---

## Attribution automatique

1. Code promo dans le message (confidence 95%)
2. Mention influenceur (confidence 75%)
3. Timing: 1 seul actif dans les 48h (confidence 45%)
4. Non attribue: demander au client

---

## Funnel cash Algerie

Reach > Contact (1-5%) > Demande prix (40-70%) > Commande (20-50%) > Livraison (70-90%) > Paiement (80-95%)

Pertes typiques: 30% annulations, 10-20% refus livraison, 5-10% impayes

---

## Formulaire commercial (30 secondes)

1. Source (WA / DM / Tel / Magasin)
2. Code promo (auto-detecte)
3. Wilaya (auto-detect par prefixe tel)
4. Statut (demande prix / commande / livre / paye)
5. Montant (DA)

Question obligatoire: "Avez-vous un code promo ?"

---

## Apprentissage

Phase 1 (0-10 campagnes): Benchmarks fixes
Phase 2 (10-50): Calibration benchmark_calibre = default x 0.3 + reel x 0.7
Phase 3 (50+): Gradient Boosting Regressor

---

## Score final avec offline

SANS offline: Social 40% + Business 60% (confidence ~45%)
AVEC offline: Social 20% + Business 30% + Offline 50% (confidence ~85-98%)
