# Backend API - RA

## Endpoints

### Influenceurs

| Methode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/influencers/analyze?username=xxx&platform=yyy` | Analyser un influenceur (scraping reel) |
| `POST` | `/api/influencers/screenshot` | Upload capture d'ecran (OCR) |
| `GET` | `/api/influencers/` | Liste tous les influenceurs analyses |
| `GET` | `/api/influencers/{id}` | Details complets d'un influenceur |
| `GET` | `/api/influencers/{id}/history` | Historique des snapshots |
| `DELETE` | `/api/influencers/{id}` | Supprimer un influenceur |
| `POST` | `/api/influencers/compare` | Comparer plusieurs influenceurs (body: ids[]) |

### Dashboard

| Methode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/dashboard/stats` | Stats globales |
| `GET` | `/api/dashboard/recent` | Analyses recentes |

## Structure backend

```
backend/
  requirements.txt
  run.py
  app/
    __init__.py
    main.py                 # FastAPI app + CORS + routers
    core/
      config.py             # Settings (DB URL, upload dir)
      database.py           # SQLAlchemy async setup
    models/
      influencer.py         # 5 tables SQLAlchemy
    services/
      instagram_scraper.py  # Instaloader scraping
      tiktok_scraper.py     # httpx + BeautifulSoup
      analyzer.py           # Calculs scores + 58 wilayas
      ocr_service.py        # Tesseract OCR
    api/
      influencers.py        # 7 endpoints
      dashboard.py          # 2 endpoints
```

## Score global (formule)

```
score = (engagement * 0.30) + (authenticite * 0.30) + (commentaires * 0.20) + (croissance * 0.20)
```

- **engagement** : taux d'engagement normalise 0-10
- **authenticite** : inverse du % faux followers, normalise 0-10
- **commentaires** : qualite des commentaires 0-10
- **croissance** : pattern de croissance 0-10

## Detection des 58 wilayas

Le service `analyzer.py` contient les 58 wilayas algeriennes avec aliases (francais/arabe/numeros) pour detecter la zone d'operation depuis la bio, localisation et hashtags.

## Lancer le backend

```bash
cd ~/RA/backend
source venv/bin/activate
python run.py
# ou
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
