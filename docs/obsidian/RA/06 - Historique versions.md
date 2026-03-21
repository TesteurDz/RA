# Historique des versions

## v4.2 - 20 mars 2026
### Scoring Avance (8 ameliorations)
- Buyer Intent Weight (darija+FR+EN, coefficients 2.0/1.5/1.0/0.3)
- Engagement Velocity (interactions/temps, log-sigmoid)
- Outliers handling (median, trimmed mean, top 10% removal)
- Sigmoid normalization par tier (nano/micro/mid/macro/mega)
- Social Score + Business Score separes (55/45)
- Conversion Score (saves x1.5 + intent x2 + shares x1.2)
- Confidence Score 0-100
- advanced_analyze() avec 12 nouveaux champs

### OCR
- Migration Tesseract vers Mistral Vision (pixtral-large-latest)
- 3 niveaux fallback : Mistral > VPS Claude proxy > Tesseract
- Cle Mistral API configuree

### Flutter App
- Icone custom RA (dark + lime)
- Permission INTERNET ajoutee
- baseUrl corrige vers VPS 187.124.37.159:8001
- Mapping cles API corrige partout (overall_score, followers_count, etc.)
- Screenshot : content-type explicite, ecran ne bloque plus, gere id=null
- Timeout analyse 30s/45s (plus de blocage 429)

### Backend
- asyncio.wait_for sur scraping (timeout 30s/45s)
- Screenshot retourne id
- Rate limit 429 : message erreur clair
- mistralai installe dans venv

---

## v4.1 - 20 mars 2026
### Scraping
- Migration Instagram : instaloader seul vers instagrapi (API privee) + instaloader fallback
- Migration TikTok : HTTP scraper vers TikTok-Api (Playwright) + HTTP fallback
- Integration proxy IPRoyal residential (10GB, rotation IP)
- Login Instagram automatique au demarrage (bapk2026, session persistee)
- Fix heartCount TikTok (engagement etait a 0%)

### Backend
- Service systemd ra-backend.service (auto-restart)
- Port 8001 ouvert dans firewall
- Timeout scraping avec asyncio.wait_for (30s profil, 45s engagement)
- Fix route /analyze vs /{id} (pydantic v2)

### Flutter App
- Fix mapping cles backend/frontend (followers_count, overall_score, etc.)
- Fix verdict texte incoherent avec le score
- Fix content-type upload screenshot (http_parser)
- Fix getDashboardRecent (clef recent)
- Timeout augmente 60s vers 120s
- Permission Internet + cleartext traffic dans AndroidManifest
- Labels demographiques corriges (25-34 ans au lieu de 25-34-pct)
- Affichage pays corrige (Algeria au lieu de brut JSON)
- Genre affiche (estimated_male_pct / estimated_female_pct)

### Scoring
- Engagement normalise par taille de compte (6 paliers)
- Zone d operation : skip pour profils verifies 1M+ (internationaux)

---

## v4.0 - 19 mars 2026
- Version initiale Flutter
- Scraping Instagram (instaloader) + TikTok (HTTP)
- Score global /10
- OCR captures d ecran
- Dashboard, historique, comparaison
- Design Material 3 Dark
