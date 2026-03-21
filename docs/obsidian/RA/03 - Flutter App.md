# Flutter App - RA

## Structure

```
flutter_app/
  lib/
    main.dart                              # Entry point
    core/
      theme.dart                           # Material 3 dark theme
      api_service.dart                     # Singleton HTTP client
      constants.dart                       # Colors, spacing, text styles
    models/
      influencer.dart                      # Data model + fromJson
    screens/
      main_shell.dart                      # BottomNav + IndexedStack
      analyze_screen.dart                  # Recherche par @username + screenshot
      dashboard_screen.dart                # Stats + analyses recentes
      history_screen.dart                  # Liste influenceurs + search/filter
      compare_screen.dart                  # Comparaison cote a cote
      influencer_report_screen.dart        # Fiche technique complete
    widgets/
      score_badge.dart                     # Cercle anime score /10
      platform_badge.dart                  # Badge Instagram/TikTok
      stat_tile.dart                       # Tuile stat reutilisable
```

## Ecrans

### 1. Analyser (`analyze_screen.dart`)
- Mode username : champ @, selecteur plateforme (Instagram/TikTok)
- Mode screenshot : picker galerie, preview, upload OCR
- Bouton "Analyser" → appel API → navigation vers fiche technique
- Section analyses recentes en bas

### 2. Dashboard (`dashboard_screen.dart`)
- Grille 2x2 stats (total, score moyen, engagement, faux followers)
- Liste analyses recentes avec avatar, score, date
- Pull to refresh, shimmer loading

### 3. Historique (`history_screen.dart`)
- Liste complete des influenceurs analyses
- Barre de recherche + filtres plateforme
- Swipe pour supprimer
- Cards avec photo, nom, score, followers, engagement

### 4. Comparaison (`compare_screen.dart`)
- Selection jusqu'a 4 influenceurs
- Metriques cote a cote (score, followers, engagement, faux %)
- Meilleur choix mis en avant

### 5. Fiche Technique (`influencer_report_screen.dart`)
- Header profil (photo, nom, @username, badge verifie)
- Score gauge anime
- Grille stats (followers, following, posts, engagement)
- Card engagement avec barres
- Card faux followers avec PieChart fl_chart
- Card demographie (age, genre, villes)
- Card zone d'operation
- Verdict auto-genere avec bordure coloree
- Actions : supprimer, partager

## Dependencies

```yaml
dependencies:
  http: ^1.2.0
  image_picker: ^1.0.0
  fl_chart: ^0.69.0
  cached_network_image: ^3.3.0
  shimmer: ^3.0.0
  google_fonts: ^6.1.0
  intl: ^0.19.0
```

## Build APK

```bash
cd ~/RA/flutter_app
flutter build apk --release --split-per-abi
# Output: build/app/outputs/flutter-apk/app-arm64-v8a-release.apk (~17MB)
```
