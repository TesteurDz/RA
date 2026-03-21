# Scraping et Analyse - Configuration actuelle

> Mis a jour : 20 mars 2026

---

## Instagram

### Scraper principal : instagrapi
- Login : bapk2026 / bapk2026@
- Session sauvegardee : /home/claude/RA/backend/ig_session.json
- API privee mobile Instagram (contourne le rate-limit web)
- Proxy IPRoyal active

### Scraper fallback : instaloader
- Sans login (limite par rate-limit 429)
- Execute dans un thread pool (non-bloquant)

### Donnees recuperees
- Profil : username, full_name, bio, followers, following, posts, verified, profile_pic
- Engagement : likes, comments par post (6 derniers posts)
- Taux engagement reel calcule
- Detection faux followers (heuristiques)

---

## TikTok

### Scraper principal : TikTok-Api (Playwright)
- Bloque sur VPS (detection bot) meme avec proxy
- Fallback automatique vers HTTP

### Scraper fallback : HTTP + BeautifulSoup
- Parse le JSON embarque dans la page TikTok
- Via proxy IPRoyal (rotation IP)
- Recupere : followers, following, posts, heartCount (total likes)
- Calcul engagement : avg_likes_per_video / followers x 100

### Donnees recuperees
- Profil : username, full_name, bio, followers, following, posts, verified, total_likes
- Engagement : calcule depuis total_likes / nombre_videos / followers

---

## Proxy

### IPRoyal Residential
- Host : geo.iproyal.com
- Port : 12321
- User : Y0pwc0SVtQUJytk4
- Pass : WeFt0BkMuXJCB8HE
- Compte : eurlenergys@gmail.com
- Plan : 10 GB pay-as-you-go (pas d expiration)
- Rotation : IP aleatoire a chaque requete
- Config : /home/claude/RA/backend/app/core/proxy.py

### Consommation estimee
- 1 scrape profil = ~50-100 KB
- 10 GB = ~100,000 - 200,000 scrapes
- Duree estimee : plusieurs mois

---

## Analyse

### Score global (sur 10)
Ponderations actuelles :
- Engagement : 30% (ajuste par taille de compte)
- Authenticite (faux followers) : 30%
- Commentaires : 20%
- Croissance : 20%

### Normalisation engagement par taille
| Tier | Excellent | Bon | Faible |
|------|----------|-----|--------|
| Nano (<10K) | 5%+ | 3% | 1.5% |
| Micro (10K-100K) | 3.5% | 2% | 1% |
| Mid (100K-500K) | 2.5% | 1.5% | 0.7% |
| Macro (500K-1M) | 2% | 1% | 0.5% |
| Mega (1M-10M) | 1.5% | 0.8% | 0.3% |
| Celebrity (10M+) | 1% | 0.5% | 0.2% |

### Detection zone operation
- 58 wilayas algeriennes + aliases (darija, francais)
- Skip pour profils verifies 1M+ followers (internationaux)
- Detection par bio, hashtags, localisation

### Detection faux followers
Heuristiques :
- Engagement tres bas pour le nombre de followers
- Ratio followers/following anormal
- Peu de posts mais beaucoup de followers
- Nombre de followers trop rond (000)

---

## Fichiers cles

| Fichier | Role |
|---------|------|
| backend/app/services/instagram_scraper.py | Scraper Instagram (instagrapi + instaloader) |
| backend/app/services/tiktok_scraper.py | Scraper TikTok (TikTok-Api + HTTP) |
| backend/app/services/analyzer.py | Logique de scoring et analyse |
| backend/app/services/ocr_service.py | OCR captures d ecran (Tesseract) |
| backend/app/core/proxy.py | Configuration proxy IPRoyal |
| backend/ig_session.json | Session Instagram sauvegardee |
