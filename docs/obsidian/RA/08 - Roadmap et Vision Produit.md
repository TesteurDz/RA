# RA Pro - Roadmap et Vision Produit

> Derniere mise a jour : 20 mars 2026
> Statut : Phase 1 en cours

---

## Vision

Transformer RA d un simple outil d analyse en SaaS de prediction ROI pour le marche algerien (cash, offline). Le systeme doit predire quels influenceurs vont generer le plus de ventes reelles, pas juste de l engagement.

---

## Phase 1 - Stabilisation (cette semaine)

Objectif : App stable, testee, utilisable au quotidien

### Bugs a fixer
- [ ] Verdict incoherent (titre vs texte)
- [ ] Labels demographiques : 25-34-pct au lieu de 25-34 ans
- [ ] Pays affiche en brut au lieu de Algerie 65%
- [ ] Zone d operation : pas afficher Algerie pour profils internationaux
- [ ] Genre non affiche (clefs estimated_male_pct / estimated_female_pct)

### Tests a faire
- [ ] Tester 10 influenceurs Instagram algeriens
- [ ] Tester 5 influenceurs TikTok algeriens
- [ ] Verifier coherence des scores (mega vs micro)
- [ ] Tester capture d ecran (upload + OCR)
- [ ] Tester sur differents telephones

### Technique
- [ ] Commit propre sur GitHub
- [ ] Backup base de donnees
- [ ] Documenter les endpoints API
- [ ] Backend en systemd (redemarrage auto)

---

## Phase 2 - Campagnes et Tracking Offline (semaine prochaine)

Objectif : Mesurer le ROI reel malgre le cash

### Fonctionnalites
- [ ] Creer une campagne (nom, produit, prix, dates)
- [ ] Attribuer un influenceur avec code promo unique (ex: BARA_SARA)
- [ ] Generer lien WhatsApp pre-rempli avec code
- [ ] Formulaire commercial rapide (5 champs, 30 secondes)
- [ ] Dashboard campagne : contacts / commandes / paiements par influenceur
- [ ] Attribution automatique par code promo dans les messages
- [ ] Detection wilaya par prefixe telephonique

### Modele de donnees
- Campaign : nom, produit, prix, marge, dates, budget
- InfluencerDeal : campaign_id, influencer_id, promo_code, tarif
- OfflineContact : source, statut funnel, montant, wilaya

### Funnel a tracker
Reach - Contact (WA/DM/Tel) - Demande prix - Commande - Livraison - Paiement cash

### KPI offline
- Contact Rate : contacts / reach estime
- Ask Rate : demandes prix / contacts
- Order Rate : commandes / demandes prix
- Delivery Rate : livrees / commandees
- Payment Rate : payees / livrees
- CPA reel : tarif / paiements
- ROI reel : (revenue - tarif) / tarif x 100

---

## Phase 3 - Prediction ROI Avancee (quand 10+ campagnes)

Objectif : Predire les ventes avant de payer l influenceur

### Nouveaux KPIs
- Save Rate = saves / views (intention d achat)
- Completion Rate = watch_time / duree (TikTok)
- Buyer Intent Score = classification commentaires (achat/interet/neutre/spam)
- Content Fit Score = matching contenu influenceur vs produit/marque
- Conversion Potential Score = modele dynamique multi-facteurs

### Score final revise

SOCIAL PERFORMANCE 40%
- Engagement ajuste par taille 15%
- Authenticite 15%
- Completion Rate 10%

BUSINESS PERFORMANCE 60%
- Buyer Intent Score 18%
- Save Rate 15%
- Content Fit 12%
- Audience Match 9%
- ROI financier estime 6%

### Detection Giveaway
- Mots-cles multilingues (FR, AR darija, EN)
- Signaux comportementaux (spike comments, ratio anormal)
- Classification : exclure (score>75), ponderer (40-75), garder (<40)
- Anti faux-positifs : viral organique vs concours

### Verdicts business

| Score | Verdict | Action |
|-------|---------|--------|
| 80-100 | INVESTIR | Negocier un package |
| 60-79 | TESTER | Un post test d abord |
| 40-59 | PRUDENCE | Risque eleve |
| 0-39 | EVITER | Ne pas collaborer |

---

## Phase 4 - Machine Learning (quand 50+ campagnes)

Objectif : Le systeme apprend et s ameliore tout seul

### Apprentissage
1. Phase 1 (0-10 campagnes) : Benchmarks fixes marche algerien
2. Phase 2 (10-50 campagnes) : Calibration par regles ajustees (70% reel + 30% defaults)
3. Phase 3 (50+ campagnes) : Gradient Boosting sur les features

### Feedback loop
Prediction - Campagne - Resultats reels - Recalibration - Meilleure prediction

---

## Benchmarks Marche Algerien (Cash)

### Taux par niche

| Niche | Contact Rate | Ask to Order | Order to Paid |
|-------|-------------|-------------|--------------|
| Food | 3.5% | 35% | 75% |
| Beauty | 2.5% | 30% | 70% |
| Fashion | 2.0% | 25% | 65% |
| Tech | 1.5% | 15% | 80% |

### Grille tarifaire influenceurs DZ (DA)

| Followers | Tarif base |
|-----------|-----------|
| < 5K | 3,000 |
| 5K-10K | 8,000 |
| 10K-25K | 15,000 |
| 25K-50K | 30,000 |
| 50K-100K | 60,000 |
| 100K-250K | 120,000 |
| 250K-500K | 250,000 |
| 500K-1M | 500,000 |

### Normalisation engagement par taille

| Tier | Excellent | Bon | Faible |
|------|----------|-----|--------|
| Nano (<10K) | 5%+ | 3% | 1.5% |
| Micro (10K-100K) | 3.5% | 2% | 1% |
| Mid (100K-500K) | 2.5% | 1.5% | 0.7% |
| Macro (500K-1M) | 2% | 1% | 0.5% |
| Mega (1M-10M) | 1.5% | 0.8% | 0.3% |
| Celebrity (10M+) | 1% | 0.5% | 0.2% |

---

## Regles terrain (8 regles d or)

1. Code obligatoire : l influenceur DOIT mentionner le code (overlay + caption + story)
2. WhatsApp = ROI : lien pre-rempli en bio + story
3. Premiere question : Avez-vous un code promo ? avant de parler prix
4. Tout noter : meme les contacts non-convertis
5. Wilaya = gold : toujours noter la wilaya
6. Timing : enregistrer dans les 24h
7. Ne pas melanger : 1 campagne = 1 influenceur = 1 code unique
8. Feedback loop : a la fin de chaque campagne, entrer les totaux

---

## Stack technique

| Composant | Technologie |
|-----------|------------|
| Backend | Python FastAPI + SQLite |
| Frontend | Flutter 3.35.2 |
| Scraping Instagram | instagrapi (API privee, login bapk2026) + instaloader (fallback) |
| Scraping TikTok | TikTok-Api (Playwright) + HTTP BeautifulSoup (fallback) |
| OCR | Tesseract |
| Hebergement | VPS Hostinger 187.124.37.159 |
| Port backend | 8001 |
| APK download | http://187.124.37.159/ra-app.apk |

---

## Liens

- [[00 - Vue d ensemble]]
- [[09 - Systeme ROI et KPIs]]
- [[10 - Detection Giveaway]]
- [[11 - Module Offline et Cash]]
