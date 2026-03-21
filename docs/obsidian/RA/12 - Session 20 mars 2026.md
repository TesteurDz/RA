# RA - Session 20 mars 2026

> Retour : [[00 - Vue d ensemble]]
> Tags : #RA #session #v4.2
> Date : 20 mars 2026

---

## Resume

Session majeure avec implementation des 8 ameliorations de scoring, remplacement OCR Tesseract par Mistral Vision, icone custom, et nombreux bugfix frontend/backend.

---

## 1. Scoring Avance (8 ameliorations)

### 1.1 Buyer Intent Weight
- Classification commentaires : achat_direct (x2.0), interet (x1.5), neutre (x1.0), spam (x0.3)
- Keywords darija + FR + EN (chhal, kayen, prix, combien, commander, dispo, livraison)
- Integre dans le calcul du weighted engagement

### 1.2 Engagement Velocity
- Calcul interactions/temps si timestamps disponibles
- Fallback estimation par frequence de posts
- Normalise 0-10 via log-sigmoid

### 1.3 Outliers (TikTok surtout)
- Median engagement + trimmed mean
- Suppression top 10% posts si skew >2x la moyenne
- Retourne mean, median, trimmed_mean

### 1.4 Sigmoid Normalization
- Remplace score lineaire par sigmoid : 10 / (1 + exp(-x))
- Seuils par tier : nano, micro, mid, macro, mega, celebrity

### 1.5 Social Score + Business Score separes
- Social Score (0-10) : engagement + authenticite + qualite commentaires
- Business Score (0-10) : conversion + buyer intent + content fit
- Overall = 55% social + 45% business

### 1.6 Conversion Score
- Formule : (saves x 1.5 + intent_comments x 2 + shares x 1.2) / views x 1000
- Normalise par sigmoid

### 1.7 Confidence Score (0-100)
- Base sur : taille echantillon, donnees disponibles, coherence metriques
- Faible si peu de posts analyses ou donnees manquantes

### 1.8 Structure advanced_analyze()
- 12 nouveaux champs dans API : social_score, business_score, conversion_score, buyer_intent, engagement_velocity, engagement_stats, confidence, tier, etc.
- Backward compatible avec legacy_overall_score

---

## 2. OCR - Migration Tesseract vers Mistral Vision

- Probleme : Tesseract pas installe sur telephone, erreur "tesseract not found"
- Solution : 3 niveaux de fallback
  1. Mistral Vision API (pixtral-large-latest) - meilleure precision
  2. VPS Claude proxy (base64 dans prompt)
  3. Tesseract + regex (si disponible)
- Cle Mistral : configuree dans config.py
- Backend endpoint /screenshot accepte maintenant octet-stream + detection par extension

---

## 3. App Flutter

### Icone
- Icone custom RA (fond dark #0D0D0D, texte "RA" lime #ccff00, cercles radar)
- Label app : "RA" (plus "ra_app")
- flutter_launcher_icons genere pour Android + iOS

### Bugfix chargement
- baseUrl corrige : http://187.124.37.159:8001 (etait localhost:8000)
- Permission INTERNET ajoutee dans AndroidManifest (manquait !)
- usesCleartextTraffic=true
- Timeout augmente a 120s

### Bugfix mapping cles API
- Dashboard : total_analyzed, avg_overall_score, avg_engagement_rate, avg_fake_followers_pct
- Recent : cle "recent" dans la reponse, overall_score, profile_pic_url
- History : followers_count, overall_score, profile_pic_url, updated_at
- Report : overall_score, followers_count, following_count, posts_count, zone_operation
- Analyze : overall_score dans recentCard

### Bugfix screenshot
- Content-type image/jpeg envoye explicitement (http_parser)
- Backend accepte octet-stream + extension
- Ecran ne bloque plus apres upload (reset screenshotFile, gere id=null)
- Si pas de username detecte : message info au lieu de crash

### Bugfix analyse
- Timeout 30s sur scrape_profile, 45s sur engagement
- Rate limit 429 : message erreur clair en francais
- Plus de blocage infini quand Instagram rate limit

---

## 4. Backend VPS

- Service systemd ra-backend.service restart OK
- Port 8001 ouvert firewall
- Fichiers deployes : analyzer.py, ocr_service.py, influencers.py, config.py
- Dependance mistralai installee dans venv
- Health check OK : http://187.124.37.159:8001/health

---

## Fichiers modifies

### Backend (~/RA/backend/app/)
- services/analyzer.py - 8 ameliorations scoring completes
- services/ocr_service.py - Mistral Vision + VPS proxy + Tesseract fallback
- api/influencers.py - timeouts, id dans screenshot, asyncio.wait_for
- core/config.py - MISTRAL_API_KEY, VPS_PROXY_URL, VPS_PROXY_TOKEN

### Flutter (~/RA/flutter_app/)
- core/api_service.dart - baseUrl VPS, timeout 120s, content-type image, cle "recent"/"influencers"
- screens/dashboard_screen.dart - mapping cles stats
- screens/history_screen.dart - mapping cles
- screens/analyze_screen.dart - screenshot id null, overall_score
- screens/influencer_report_screen.dart - overall_score, followers_count, zone_operation
- pubspec.yaml - http_parser, flutter_launcher_icons
- android/app/src/main/AndroidManifest.xml - INTERNET permission, cleartext, label RA

---

## Version deployee

- APK : RA v4.2e (envoye sur Telegram)
- Backend : actif sur VPS port 8001
- 12 influenceurs dans la base de donnees
