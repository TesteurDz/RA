# Base de donnees - RA

## SGBD

SQLite (fichier `ra.db`) via SQLAlchemy 2.0 async + aiosqlite.

## Schema

### Table `influencers`
| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER PK | Auto-increment |
| username | VARCHAR | Nom d'utilisateur |
| platform | VARCHAR | instagram / tiktok |
| full_name | VARCHAR | Nom complet |
| bio | TEXT | Biographie |
| profile_pic_url | TEXT | URL photo de profil |
| followers_count | INTEGER | Nombre d'abonnes |
| following_count | INTEGER | Nombre d'abonnements |
| posts_count | INTEGER | Nombre de publications |
| is_verified | BOOLEAN | Compte verifie |
| zone_operation | VARCHAR | Wilaya detectee |
| country | VARCHAR | Pays (default: Algerie) |
| created_at | DATETIME | Date de creation |
| updated_at | DATETIME | Derniere mise a jour |

### Table `snapshots`
| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER PK | |
| influencer_id | INTEGER FK | Ref influencers.id |
| followers_count | INTEGER | Followers au moment du snapshot |
| following_count | INTEGER | |
| posts_count | INTEGER | |
| avg_likes | FLOAT | Moyenne likes |
| avg_comments | FLOAT | Moyenne commentaires |
| avg_shares | FLOAT | Moyenne partages |
| engagement_rate | FLOAT | Taux d'engagement |
| fake_followers_pct | FLOAT | % faux followers estime |
| overall_score | FLOAT | Score global /10 |
| captured_at | DATETIME | Date du snapshot |

### Table `comment_analyses`
| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER PK | |
| snapshot_id | INTEGER FK | |
| total_comments_analyzed | INTEGER | |
| bot_comments_pct | FLOAT | % bots |
| positive_pct | FLOAT | % positif |
| negative_pct | FLOAT | % negatif |
| neutral_pct | FLOAT | % neutre |
| top_languages | JSON | Langues detectees |
| avg_comment_length | FLOAT | Longueur moyenne |

### Table `audience_demographics`
| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER PK | |
| snapshot_id | INTEGER FK | |
| estimated_male_pct | FLOAT | |
| estimated_female_pct | FLOAT | |
| age_13_17_pct | FLOAT | |
| age_18_24_pct | FLOAT | |
| age_25_34_pct | FLOAT | |
| age_35_44_pct | FLOAT | |
| age_45_plus_pct | FLOAT | |
| top_countries | JSON | |
| top_cities | JSON | |

### Table `screenshots`
| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER PK | |
| influencer_id | INTEGER FK | |
| file_path | VARCHAR | Chemin fichier |
| ocr_data | JSON | Donnees extraites OCR |
| uploaded_at | DATETIME | |
