# RA - Reputation Analyzer

## Vue d'ensemble

**RA** est un outil d'analyse de reputation d'influenceurs ciblant l'Algerie. Il permet d'evaluer la fiabilite d'un influenceur avant toute collaboration commerciale.

## Informations projet

| Champ | Valeur |
|-------|--------|
| **Nom** | RA - Reputation Analyzer |
| **Version** | 4.1 (Flutter + instagrapi + TikTok-Api) |
| **Date creation** | 20 mars 2026 |
| **Auteur** | Sebba - EURL ENERGY'S FOOD |
| **Plateformes** | Instagram, TikTok |
| **Zone cible** | Algerie (58 wilayas) |
| **Stack Frontend** | Flutter 3.35.2 (Dart) |
| **Stack Backend** | Python FastAPI + SQLite |
| **Design** | Material 3 Dark, moderne & epure |

## Fonctionnalites principales

1. **Scraping reel** Instagram (instagrapi + instaloader fallback) & TikTok (TikTok-Api + HTTP fallback)
2. **Taux d'engagement reel** - calcul sur les 12 derniers posts
3. **Detection faux followers** - heuristiques (ratio, engagement, patterns)
4. **Evolution abonnes** - historique des snapshots
5. **Analyse commentaires** - detection bots, sentiment, langues
6. **Demographie estimee** - age, genre, localisation
7. **Zone d'operation** - detection des 58 wilayas algeriennes
8. **Score global /10** - pondere : engagement 30%, authenticite 30%, commentaires 20%, croissance 20%
9. **OCR captures d'ecran** - upload depuis galerie, extraction Tesseract
10. **Comparaison** - jusqu'a 4 influenceurs cote a cote
11. **Fiche technique** - page detaillee par influenceur avec charts

## Repertoires

| Element | Chemin |
|---------|--------|
| Code complet | `~/RA/` (Mac local) |
| Backend Python | `~/RA/backend/` |
| Frontend Flutter | `~/RA/flutter_app/` |
| Frontend React (legacy) | `~/RA/frontend/` |
| Docs/Cahier des charges | `~/RA/docs/` |
| APK Flutter | Telegram @VpsNotifyDzBot |

## Infrastructure

| Element | Detail |
|---------|--------|
| VPS | Hostinger 187.124.37.159 |
| Backend port | 8001 (systemd ra-backend.service) |
| APK | http://187.124.37.159/ra-app.apk |
| Proxy | IPRoyal residential (geo.iproyal.com:12321, 10GB pay-as-you-go) |
| Instagram login | bapk2026 via instagrapi (session: ig_session.json) |
| Firewall | ports 22, 80, 443, 3333, 8001, 8500 |

## Liens rapides

- [[01 - Architecture technique]]
- [[02 - Backend API]]
- [[03 - Flutter App]]
- [[04 - Base de donnees]]
- [[05 - Scraping & Analyse]]
- [[06 - Historique versions]]
- [[07 - Cahier des charges]]


## Roadmap & Evolution

- [[08 - Roadmap et Vision Produit]]
- [[09 - Systeme ROI et KPIs]]
- [[10 - Detection Giveaway]]
- [[11 - Module Offline et Cash]]
