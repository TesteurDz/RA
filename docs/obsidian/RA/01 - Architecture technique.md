# Architecture technique - RA

## Stack technique

### Backend (Python)
- **Framework** : FastAPI 0.104.1
- **Base de donnees** : SQLite (async via aiosqlite + SQLAlchemy 2.0)
- **Scraping Instagram** : Instaloader 4.10.1
- **Scraping TikTok** : httpx + BeautifulSoup4
- **OCR** : Pytesseract + Pillow
- **Serveur** : Uvicorn sur port 8000

### Frontend Mobile (Flutter)
- **Flutter** : 3.35.2 (stable)
- **Dart** : 3.9.0
- **Charts** : fl_chart
- **HTTP** : http package
- **Images** : cached_network_image
- **Galerie** : image_picker
- **Fonts** : google_fonts (Inter + JetBrains Mono)
- **Loading** : shimmer

### Frontend Web (React - legacy)
- **React** 18 + Vite 5
- **TailwindCSS** v4
- **Charts** : Recharts
- **HTTP** : Axios
- **Capacitor** : wrap web -> APK (abandonne pour Flutter)

## Architecture globale

```
[Flutter App] <--HTTP--> [FastAPI Backend] <---> [SQLite DB]
     |                         |
     |                    [Instaloader]----> Instagram
     |                    [httpx/BS4]-----> TikTok
     |                    [Tesseract]-----> OCR Screenshots
     |
   [image_picker] --> Upload screenshots
```

## Ports & URLs

| Service | Port | URL |
|---------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| Swagger docs | 8000 | http://localhost:8000/docs |
| Flutter dev | - | Via emulateur ou APK |
| Reseau local | 8000 | http://192.168.0.103:8000 |

## Design System

- **Theme** : Material 3 Dark
- **Background** : `#0F0F14`
- **Surface/Cards** : `#1A1A24`
- **Primary** : `#6366F1` (indigo)
- **Success** : `#22C55E`
- **Warning** : `#EAB308`
- **Danger** : `#EF4444`
- **Text** : `#FAFAFA`
- **Text secondary** : `#A1A1AA`
- **Border** : `#2A2A36`
- **Border radius** : 16dp
- **Font body** : Inter
- **Font data** : JetBrains Mono
