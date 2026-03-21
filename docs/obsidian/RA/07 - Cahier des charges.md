# Cahier des Charges - RA (Reputation Analyzer)

**Version :** 1.0
**Date :** 19 mars 2026
**Auteur :** Sebba - EURL ENERGY'S FOOD
**Statut :** Draft initial

---

## Table des matières

1. [Présentation du projet](#1-présentation-du-projet)
2. [Contexte et objectifs](#2-contexte-et-objectifs)
3. [Périmètre fonctionnel](#3-périmètre-fonctionnel)
4. [Spécifications fonctionnelles détaillées](#4-spécifications-fonctionnelles-détaillées)
5. [Méthodes d'input et acquisition de données](#5-méthodes-dinput-et-acquisition-de-données)
6. [Interface utilisateur et expérience](#6-interface-utilisateur-et-expérience)
7. [Architecture technique](#7-architecture-technique)
8. [Modèle de données](#8-modèle-de-données)
9. [Contraintes techniques et non-fonctionnelles](#9-contraintes-techniques-et-non-fonctionnelles)
10. [Phases de développement](#10-phases-de-développement)
11. [Risques et mitigations](#11-risques-et-mitigations)
12. [Annexes](#12-annexes)

---

## 1. Présentation du projet

### 1.1 Identité du projet

| Champ | Valeur |
|-------|--------|
| **Nom** | RA - Reputation Analyzer |
| **Type** | Outil d'analyse de réputation d'influenceurs |
| **Plateformes analysées** | Instagram, TikTok |
| **Format de livraison** | Application Web + APK Android |
| **Zone cible** | Algérie (58 wilayas) |
| **Langues supportées** | Français, Arabe (darija algérien inclus) |
| **Budget opérationnel** | Gratuit (scraping, aucune API payante) |

### 1.2 Résumé exécutif

RA (Reputation Analyzer) est un outil d'investigation numérique destiné à analyser la crédibilité et la qualité des influenceurs opérant en Algérie sur Instagram et TikTok. L'outil fournit un score global sur 10, détecte les faux followers, analyse l'engagement réel, et offre une vue détaillée de l'audience estimée.

L'application s'adresse aux entreprises algériennes, aux agences marketing, et à toute personne souhaitant vérifier la légitimité d'un influenceur avant de s'engager dans un partenariat commercial.

### 1.3 Problématique

Le marché de l'influence en Algérie souffre de plusieurs problèmes majeurs :

- **Inflation artificielle des followers** : De nombreux comptes achètent des abonnés pour paraître plus populaires qu'ils ne le sont réellement.
- **Engagement fictif** : Utilisation de pods d'engagement, bots de commentaires, et likes automatisés.
- **Opacité des métriques** : Aucun outil gratuit et adapté au marché algérien n'existe pour vérifier la qualité d'un influenceur.
- **Pertes financières** : Les entreprises investissent dans des partenariats avec des influenceurs dont l'audience est en grande partie fictive.
- **Absence de données locales** : Les outils internationaux (HypeAuditor, Social Blade) ne ciblent pas spécifiquement l'Algérie et ses particularités.

### 1.4 Solution proposée

RA répond à cette problématique en offrant :

- Une analyse automatisée et gratuite basée sur le scraping
- Une détection algorithmique des faux followers et de l'engagement artificiel
- Un score de fiabilité composite et transparent
- Une interface de type "cyber investigation" qui rend l'analyse intuitive et engageante
- Un support OCR pour analyser des captures d'écran de profils
- Une adaptation au contexte algérien (wilayas, langue arabe/darija, patterns locaux)

---

## 2. Contexte et objectifs

### 2.1 Contexte du marché algérien

Le marketing d'influence en Algérie connaît une croissance rapide. Instagram et TikTok sont les deux plateformes dominantes avec :

- **Instagram** : Plateforme privilégiée pour les influenceurs lifestyle, mode, beauté, et food.
- **TikTok** : En forte croissance, particulièrement chez les 16-30 ans, dominé par le contenu en darija.

Les marques algériennes investissent de plus en plus dans l'influence marketing sans disposer d'outils d'audit adaptés. Le taux de faux followers en Algérie est estimé significativement élevé en raison du faible coût des services d'achat de followers dans la région MENA.

### 2.2 Objectifs principaux

| # | Objectif | Indicateur de succès |
|---|----------|---------------------|
| O1 | Fournir un score de fiabilité précis | Score corrélé à >80% avec vérification manuelle |
| O2 | Détecter les faux followers | Taux de détection >75% des comptes suspects |
| O3 | Analyser l'engagement réel | Calcul d'engagement ajusté vs taux brut |
| O4 | Estimer la démographie de l'audience | Précision estimée >60% sur la localisation |
| O5 | Couvrir Instagram et TikTok | Les deux plateformes pleinement opérationnelles |
| O6 | Rester 100% gratuit en opérationnel | Aucune dépendance à une API payante |
| O7 | Proposer un APK Android fonctionnel | Application publiable sur des stores alternatifs |

### 2.3 Public cible

| Segment | Description | Usage principal |
|---------|-------------|-----------------|
| **Entreprises algériennes** | PME et grandes entreprises cherchant des partenariats influenceurs | Vérification avant signature de contrat |
| **Agences marketing** | Agences de communication et marketing digital en Algérie | Audit systématique de leur roster d'influenceurs |
| **Influenceurs eux-mêmes** | Créateurs de contenu souhaitant prouver leur légitimité | Auto-audit et rapport de crédibilité |
| **Journalistes / Analystes** | Personnes enquêtant sur les pratiques d'influence | Outil d'investigation |
| **Grand public** | Curieux souhaitant vérifier un compte avant de le suivre | Vérification ponctuelle |

---

## 3. Périmètre fonctionnel

### 3.1 Fonctionnalités incluses (In Scope)

| Module | Fonctionnalité | Priorité |
|--------|----------------|----------|
| **F1** | Taux d'engagement réel | Critique |
| **F2** | Détection de faux followers | Critique |
| **F3** | Évolution des abonnés | Haute |
| **F4** | Analyse des commentaires (NLP) | Haute |
| **F5** | Démographie estimée de l'audience | Moyenne |
| **F6** | Zone d'opération de l'influenceur | Moyenne |
| **F7** | Score global sur 10 | Critique |
| **F8** | Input par @ / nom de page | Critique |
| **F9** | Input par capture d'écran (OCR) | Haute |
| **F10** | Analyse multi-comptes simultanés | Haute |
| **F11** | Comparaison côte-à-côte | Moyenne |
| **F12** | Dashboard interactif | Critique |
| **F13** | Export de rapport | Basse |

### 3.2 Fonctionnalités exclues (Out of Scope - v1)

- Analyse de YouTube, Facebook, Snapchat ou X (Twitter)
- Système d'authentification / comptes utilisateurs
- Monétisation / système de paiement
- Suivi en temps réel (monitoring continu automatique)
- Analyse de Stories/Reels Instagram en profondeur
- Application iOS native
- Notifications push

---

## 4. Spécifications fonctionnelles détaillées

### 4.1 F1 - Taux d'engagement réel

#### Description
Calcul du taux d'engagement réel d'un influenceur en se basant sur les interactions visibles par rapport à la taille de l'audience.

#### Formules de calcul

**Taux d'engagement brut :**
```
ER_brut = (likes_moyen + commentaires_moyen) / nombre_followers * 100
```

**Taux d'engagement ajusté (pondéré) :**
```
ER_ajuste = ((likes_moyen * 1) + (commentaires_moyen * 3) + (partages_moyen * 5)) / nombre_followers * 100
```

La pondération reflète la valeur relative de chaque interaction :
- Un like = effort minimal (poids 1)
- Un commentaire = engagement modéré (poids 3)
- Un partage = engagement fort (poids 5)

**Taux d'engagement par post :**
```
ER_post = (likes_post + commentaires_post) / nombre_followers * 100
```

#### Échelle d'interprétation (Instagram)

| Taux d'engagement | Évaluation | Couleur |
|-------------------|------------|---------|
| < 1% | Très faible / suspect | Rouge |
| 1% - 3% | Moyen | Orange |
| 3% - 6% | Bon | Vert |
| 6% - 10% | Très bon | Vert foncé |
| > 10% | Excellent ou suspect (vérifier) | Bleu / Alerte |

> **Note :** Un taux supérieur à 10% sur un compte de plus de 50K followers est souvent suspect et peut indiquer l'utilisation de pods d'engagement.

#### Données collectées par post (12 à 30 derniers posts)
- Nombre de likes
- Nombre de commentaires
- Date de publication
- Type de contenu (photo, carousel, reel)

#### Affichage
- Taux d'engagement brut et ajusté affichés
- Graphique en courbe montrant le taux d'engagement par post sur les 30 derniers posts
- Comparaison avec la moyenne du marché algérien (benchmark)
- Indicateur visuel (jauge circulaire avec code couleur)

---

### 4.2 F2 - Détection de faux followers

#### Description
Analyse algorithmique multi-critères pour estimer le pourcentage de faux followers dans l'audience d'un influenceur.

#### Critères de détection

**Critère 1 : Ratio engagement / followers**
```
Si followers > 10K ET engagement < 1% => Suspicion élevée
Si followers > 50K ET engagement < 0.5% => Suspicion très élevée
```

**Critère 2 : Analyse des pics de croissance**
- Détection de croissances anormales (ex : +5000 followers en 24h sans contenu viral)
- Pattern d'achat typique : pic soudain suivi d'une stagnation ou décroissance

**Critère 3 : Qualité des commentaires**
- Ratio commentaires génériques / commentaires spécifiques
- Commentaires typiques de bots : emojis seuls, phrases génériques ("Nice!", "Great post!", "Magnifique!")
- Commentaires en langues incohérentes avec l'audience cible

**Critère 4 : Ratio followers / following**
```
Si following > followers * 0.8 => Pattern de follow/unfollow suspect
Si followers > 100K ET following > 5000 => Suspect
```

**Critère 5 : Consistance de l'engagement**
- Écart-type des likes entre posts
- Un écart-type très élevé peut indiquer des achats de likes ponctuels

**Critère 6 : Analyse des profils des commentateurs (échantillon)**
- Comptes sans photo de profil
- Comptes avec 0 posts
- Noms de profils générés (suites de chiffres, noms aléatoires)

#### Score de faux followers

```
Score_faux = (w1 * critere1 + w2 * critere2 + ... + w6 * critere6) / somme_poids
```

Résultat affiché en pourcentage estimé : ex. "~35% de faux followers estimés"

#### Affichage
- Pourcentage estimé de faux followers (jauge)
- Détail de chaque critère avec indicateur vert/orange/rouge
- Graphique radar montrant la "santé" du profil
- Explication textuelle des signaux d'alerte détectés

---

### 4.3 F3 - Évolution des abonnés

#### Description
Suivi de la croissance du nombre d'abonnés dans le temps pour détecter les achats de followers et évaluer la croissance organique.

#### Données collectées
- Nombre de followers à chaque snapshot (analyse)
- Historique des snapshots précédents (stocké en base)
- Données publiques de Social Blade si disponibles (via scraping)

#### Détection d'anomalies

**Croissance organique typique :**
- Progression linéaire ou légèrement exponentielle
- Corrélation avec la fréquence de publication

**Signaux d'achat de followers :**
- Pics soudains de +1000 à +50000 followers en 1 à 3 jours
- Chute après un pic (unfollows massifs = bots qui se désabonnent)
- Absence de contenu viral correspondant au pic

#### Algorithme de détection de pics

```python
def detecter_pics(historique_followers):
    """
    Détecte les croissances anormales dans l'historique.
    Un pic est défini comme une croissance > 3x la croissance moyenne
    sur une période de 24-72h.
    """
    croissance_moyenne = calculer_croissance_moyenne(historique)
    seuil = croissance_moyenne * 3
    pics = []
    for i in range(1, len(historique)):
        delta = historique[i] - historique[i-1]
        if delta > seuil:
            pics.append({
                'date': historique[i].date,
                'delta': delta,
                'severite': delta / croissance_moyenne
            })
    return pics
```

#### Affichage
- Graphique en ligne de l'évolution des followers dans le temps
- Zones surlignées en rouge pour les pics suspects
- Annotations automatiques sur les points suspects
- Taux de croissance moyen quotidien / hebdomadaire / mensuel

---

### 4.4 F4 - Analyse des commentaires (NLP)

#### Description
Analyse automatisée des commentaires pour distinguer les vrais commentaires des commentaires de bots, et réaliser une analyse de sentiment.

#### Sous-fonctionnalités

**4.4.1 Détection de commentaires bots**

Classification des commentaires en catégories :

| Catégorie | Exemples | Score bot |
|-----------|----------|-----------|
| Emoji seul | "❤️", "🔥🔥🔥" | 0.7 |
| Phrase générique courte | "Nice!", "Beautiful!", "Magnifique" | 0.8 |
| Phrase générique arabe | "ماشاء الله", "يعطيك الصحة" (sans contexte) | 0.3 (courant en Algérie, pas nécessairement bot) |
| Commentaire spécifique | "J'adore la recette du couscous, je vais essayer ce weekend" | 0.1 |
| Spam | "DM for collab", "Check my page" | 0.9 |
| Commentaire darija contextuel | "wah sahbi hadik trop bien, win t'as acheté?" | 0.05 |

> **Adaptation algérienne :** Le modèle doit tenir compte des patterns de commentaires courants en Algérie, où certaines expressions en darija sont fréquentes et légitimes (ex: "rabbi yahfdek", "yatik saha").

**4.4.2 Analyse de sentiment**

Classification en trois catégories :
- **Positif** : Compliments, encouragements, réactions enthousiastes
- **Neutre** : Questions, tags d'amis, commentaires factuels
- **Négatif** : Critiques, plaintes, commentaires hostiles

**4.4.3 Diversité des commentateurs**

- Nombre de commentateurs uniques vs total de commentaires
- Détection de "cercles fermés" (toujours les mêmes personnes qui commentent)
- Ratio commentateurs uniques / total commentaires

#### Traitement linguistique

Langues à supporter :
- Français standard
- Arabe standard (MSA)
- Darija algérienne (transcrite en arabe et en lettres latines "arabizi")
- Mélange français/arabe (code-switching très courant en Algérie)

#### Affichage
- Camembert : répartition bot / réel / incertain
- Nuage de mots des commentaires fréquents
- Graphique de sentiment (positif/neutre/négatif)
- Liste des commentaires les plus suspects avec score de confiance
- Score de diversité des commentateurs

---

### 4.5 F5 - Démographie estimée de l'audience

#### Description
Estimation de la composition démographique de l'audience d'un influenceur à partir des données publiquement accessibles.

#### Méthodes d'estimation

**5.5.1 Localisation géographique**
- Analyse des commentaires en darija, français, arabe => estimation de la proportion algérienne
- Géolocalisation des posts de l'influenceur
- Analyse des hashtags locaux (#alger, #oran, #constantine, etc.)
- Heures de pic d'engagement (fuseau horaire UTC+1)

**5.5.2 Genre estimé**
- Analyse des prénoms des commentateurs (base de données de prénoms algériens/arabes/français)
- Classification par prénom : masculin / féminin / inconnu
- Pourcentage estimé homme/femme de l'audience active

**5.5.3 Tranche d'âge estimée**
- Type de contenu consommé (indicateur indirect)
- Langage utilisé dans les commentaires (darija = plus jeune, MSA = plus varié)
- Utilisation d'émojis et de slang (indicateur de jeunesse)
- Heure d'activité (commentaires nocturnes = audience plus jeune)

#### Affichage
- Graphique donut pour la répartition homme/femme
- Histogramme pour les tranches d'âge estimées
- Carte de l'Algérie avec intensité de couleur par wilaya
- Pourcentage d'audience estimée en Algérie vs reste du monde
- Indicateur de fiabilité de l'estimation (faible/moyen/élevé)

---

### 4.6 F6 - Zone d'opération de l'influenceur

#### Description
Détermination de la wilaya et ville d'opération principale de l'influenceur.

#### Sources de données
- Bio du profil (mention de ville/wilaya)
- Géolocalisation des posts
- Hashtags géographiques utilisés (#alger, #babeloued, #sidibelabbes, etc.)
- Mentions de lieux dans les légendes
- Langue/dialecte utilisé (indice de région)

#### Base de référence géographique

Les 58 wilayas d'Algérie avec les villes principales :

```
01-Adrar, 02-Chlef, 03-Laghouat, 04-OumElBouaghi, 05-Batna,
06-Béjaïa, 07-Biskra, 08-Béchar, 09-Blida, 10-Bouira,
11-Tamanrasset, 12-Tébessa, 13-Tlemcen, 14-Tiaret, 15-TiziOuzou,
16-Alger, 17-Djelfa, 18-Jijel, 19-Sétif, 20-Saïda,
21-Skikda, 22-SidiBelAbbès, 23-Annaba, 24-Guelma, 25-Constantine,
26-Médéa, 27-Mostaganem, 28-M'Sila, 29-Mascara, 30-Ouargla,
31-Oran, 32-ElBayadh, 33-Illizi, 34-BordjBouArréridj, 35-Boumerdès,
36-ElTarf, 37-Tindouf, 38-Tissemsilt, 39-ElOued, 40-Khenchela,
41-SoukAhras, 42-Tipaza, 43-Mila, 44-AïnDefla, 45-Naâma,
46-AïnTémouchent, 47-Ghardaïa, 48-Relizane, 49-ElM'Ghair,
50-ElMeniaa, 51-OuledDjellal, 52-BordjBadjiMokhtar, 53-BéniAbbès,
54-Timimoun, 55-Touggourt, 56-Djanet, 57-InSalah, 58-InGuezzam
```

#### Affichage
- Carte interactive de l'Algérie avec la wilaya principale surlignée
- Liste des lieux les plus fréquemment mentionnés
- Rayon d'action estimé (local / régional / national)

---

### 4.7 F7 - Score global sur 10

#### Description
Score composite agrégé reflétant la fiabilité et la qualité globale d'un influenceur.

#### Composition du score

| Critère | Poids | Description |
|---------|-------|-------------|
| Taux d'engagement réel | 25% | ER ajusté comparé aux benchmarks |
| Authenticité des followers | 25% | Inverse du taux de faux followers estimé |
| Qualité des commentaires | 15% | Ratio vrais commentaires / bots |
| Consistance de croissance | 15% | Absence de pics suspects |
| Diversité d'audience | 10% | Variété des commentateurs |
| Activité et régularité | 10% | Fréquence de publication, régularité |

#### Formule de calcul

```python
score_global = (
    engagement_score * 0.25 +
    authenticite_score * 0.25 +
    qualite_commentaires_score * 0.15 +
    consistance_croissance_score * 0.15 +
    diversite_audience_score * 0.10 +
    activite_score * 0.10
)
# Chaque sous-score est normalisé entre 0 et 10
# Score final arrondi à 1 décimale
```

#### Échelle d'interprétation

| Score | Label | Description | Couleur |
|-------|-------|-------------|---------|
| 0 - 2 | Frauduleux | Très forte probabilité de fraude massive | Rouge foncé |
| 2 - 4 | Suspect | Nombreux signaux d'alerte | Rouge |
| 4 - 5 | Douteux | Quelques signaux d'alerte significatifs | Orange |
| 5 - 6 | Moyen | Profil acceptable avec des réserves | Jaune |
| 6 - 7 | Correct | Profil globalement fiable | Vert clair |
| 7 - 8 | Bon | Profil de qualité, audience principalement réelle | Vert |
| 8 - 9 | Très bon | Profil excellent, forte authenticité | Vert foncé |
| 9 - 10 | Exceptionnel | Profil irréprochable | Bleu / Or |

#### Affichage
- Score affiché en grand format avec animation (compteur qui monte)
- Jauge circulaire avec code couleur
- Badge textuel (ex: "BON - 7.2/10")
- Détail des sous-scores en graphique radar
- Comparaison avec la moyenne des profils analysés

---

## 5. Méthodes d'input et acquisition de données

### 5.1 Input par @ ou nom de page

#### Flux utilisateur
1. L'utilisateur saisit le `@username` ou l'URL complète du profil
2. Le système détecte automatiquement la plateforme (Instagram ou TikTok)
3. Lancement du scraping en arrière-plan
4. Affichage d'une barre de progression avec les étapes
5. Résultats affichés une fois le scraping terminé

#### Formats acceptés
```
@username
username
https://www.instagram.com/username/
https://www.instagram.com/username
https://www.tiktok.com/@username
https://www.tiktok.com/@username?lang=fr
```

#### Validation
- Vérification que le profil existe
- Vérification que le profil est public
- Message d'erreur clair si profil privé ou inexistant

### 5.2 Input par capture d'écran (OCR)

#### Flux utilisateur
1. L'utilisateur upload une ou plusieurs captures d'écran d'un profil
2. Le système applique l'OCR pour extraire :
   - Nom du profil / @username
   - Nombre de followers
   - Nombre de following
   - Nombre de posts
   - Bio (si visible)
3. L'utilisateur vérifie et corrige les données extraites si nécessaire
4. Les données sont utilisées pour l'analyse (mode dégradé sans scraping)

#### Types de captures supportées
- Capture du profil Instagram (header avec stats)
- Capture du profil TikTok (header avec stats)
- Capture de post individuel (likes, commentaires visibles)
- Capture de l'écran "Insights" si partagé par l'influenceur

#### Technologie OCR
- **Tesseract.js** pour le traitement côté client (navigateur)
- Prétraitement de l'image : binarisation, débruitage, correction de contraste
- Régions d'intérêt (ROI) prédéfinies pour chaque type de capture
- Expressions régulières pour extraire les nombres (followers, likes, etc.)

#### Gestion des formats de nombres
```
1,234 => 1234
1.234 => 1234
12,5K => 12500
12.5K => 12500
1,2M => 1200000
1.2M => 1200000
12K => 12000
1M => 1000000
```

### 5.3 Analyse multi-comptes

#### Flux utilisateur
1. L'utilisateur ajoute plusieurs comptes (jusqu'à 10 simultanément)
2. Chaque compte est analysé en parallèle (file d'attente côté serveur)
3. Barre de progression individuelle par compte
4. Résultats affichés en grille ou en liste
5. Possibilité de comparer 2 à 4 comptes côte-à-côte

#### Limites
- Maximum 10 comptes par session d'analyse
- Délai minimum de 5 secondes entre chaque requête de scraping (anti-détection)
- File d'attente si plus de 3 analyses simultanées

---

## 6. Interface utilisateur et expérience

### 6.1 Direction artistique

#### Thème : "Enquêteur high-tech / Cyber Investigation"

**Palette de couleurs :**

| Élément | Couleur | Code hex |
|---------|---------|----------|
| Fond principal | Noir profond | `#0A0A0F` |
| Fond secondaire | Gris anthracite | `#12121A` |
| Fond cartes | Gris foncé | `#1A1A2E` |
| Accent primaire | Cyan néon | `#00F0FF` |
| Accent secondaire | Violet électrique | `#7B2FBE` |
| Succès | Vert émeraude | `#00E676` |
| Alerte | Orange néon | `#FF9100` |
| Danger | Rouge vif | `#FF1744` |
| Texte principal | Blanc cassé | `#E0E0E0` |
| Texte secondaire | Gris clair | `#9E9E9E` |

**Typographie :**
- Titres : `Space Grotesk` ou `Orbitron` (style tech/futuriste)
- Corps : `Inter` ou `Roboto` (lisibilité)
- Données/chiffres : `JetBrains Mono` ou `Fira Code` (monospace, style terminal)

**Éléments visuels :**
- Effet de grille subtile en fond (grid pattern)
- Lignes de scan animées sur les éléments en cours d'analyse
- Effet "glow" cyan sur les éléments interactifs
- Particules flottantes subtiles en arrière-plan
- Animations de "data flow" lors du chargement
- Icônes de style linéaire (outline) en cyan
- Bordures lumineuses subtiles sur les cards (`box-shadow: 0 0 15px rgba(0,240,255,0.1)`)

### 6.2 Pages et écrans

#### 6.2.1 Page d'accueil / Écran de recherche

```
┌─────────────────────────────────────────────────────────┐
│  [Logo RA]          Reputation Analyzer                 │
│                                                          │
│          ╔══════════════════════════════════╗            │
│          ║  🔍 Entrez un @ ou une URL...   ║            │
│          ╚══════════════════════════════════╝            │
│                                                          │
│     [Instagram]  [TikTok]     [📷 Upload capture]       │
│                                                          │
│  ── Ou analysez plusieurs comptes ──                    │
│  [+ Ajouter un compte]  [Lancer l'analyse groupée]     │
│                                                          │
│  ── Dernières analyses ──                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐               │
│  │ @user1   │ │ @user2   │ │ @user3   │               │
│  │ ★ 7.2   │ │ ★ 3.8   │ │ ★ 8.5   │               │
│  │ 12/03   │ │ 10/03   │ │ 08/03   │               │
│  └──────────┘ └──────────┘ └──────────┘               │
└─────────────────────────────────────────────────────────┘
```

**Description :**
- Champ de recherche central proéminent avec effet glow
- Toggle Instagram/TikTok pour sélectionner la plateforme
- Bouton upload pour les captures d'écran
- Section "Dernières analyses" avec mini-cards des profils récemment analysés
- Fond avec grille animée subtile et particules

#### 6.2.2 Écran de chargement / Analyse en cours

```
┌─────────────────────────────────────────────────────────┐
│                                                          │
│          ANALYSE EN COURS...                            │
│                                                          │
│          @influenceur_dz                                │
│                                                          │
│  [██████████░░░░░░░░░░] 45%                            │
│                                                          │
│  ✓ Profil récupéré                                      │
│  ✓ Posts collectés (24/30)                              │
│  ▸ Analyse des commentaires...                          │
│  ○ Calcul du score                                      │
│  ○ Génération du rapport                                │
│                                                          │
│  ── Données en temps réel ──                            │
│  Followers: 125,400                                     │
│  Posts analysés: 24                                     │
│  Commentaires scannés: 1,847                            │
│                                                          │
│           [ Annuler l'analyse ]                         │
└─────────────────────────────────────────────────────────┘
```

**Description :**
- Animation de "scan" style radar ou terminal
- Barre de progression avec les étapes détaillées
- Données extraites affichées en temps réel au fur et à mesure
- Effets de texte type "matrix" ou terminal pour les données qui arrivent
- Bouton d'annulation visible

#### 6.2.3 Dashboard principal - Résultats d'analyse

```
┌─────────────────────────────────────────────────────────────┐
│  [← Retour]    RA - @influenceur_dz    [⟳ Ré-analyser]   │
│                                                              │
│  ┌─────────────────────────────────┐  ┌──────────────────┐ │
│  │  PHOTO    @influenceur_dz       │  │   SCORE GLOBAL   │ │
│  │  PROFIL   Influenceuse Mode     │  │                  │ │
│  │           📍 Alger, W16         │  │    ╭──────╮      │ │
│  │           📷 Instagram          │  │    │ 7.2  │      │ │
│  │                                  │  │    │ /10  │      │ │
│  │  Followers: 125,400             │  │    ╰──────╯      │ │
│  │  Following: 890                  │  │    BON ✓         │ │
│  │  Posts: 432                      │  │                  │ │
│  │  Engagement: 4.2%               │  │  [Voir détails]  │ │
│  └─────────────────────────────────┘  └──────────────────┘ │
│                                                              │
│  ── MÉTRIQUES CLÉS ──                                       │
│  ┌────────────┐┌────────────┐┌────────────┐┌────────────┐ │
│  │ Engagement ││ Faux       ││ Croissance ││ Sentiment  │ │
│  │   4.2%     ││ Followers  ││  +2.3%/mois││  78%       │ │
│  │   ✅ Bon   ││   ~18%     ││   ✅ Stable││  Positif   │ │
│  └────────────┘└────────────┘└────────────┘└────────────┘ │
│                                                              │
│  ── GRAPHIQUES ──                                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  [Engagement] [Croissance] [Commentaires] [Audience] │  │
│  │                                                       │  │
│  │  📈 Graphique interactif affiché ici                  │  │
│  │     (Chart.js / Recharts)                             │  │
│  │                                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ── ANALYSE DÉTAILLÉE ──                                    │
│  ┌──────────────────────┐  ┌──────────────────────┐       │
│  │ Radar de santé       │  │ Commentaires         │       │
│  │ du profil            │  │ Top bots détectés    │       │
│  │ (graphique radar)    │  │ Sentiment breakdown  │       │
│  └──────────────────────┘  └──────────────────────┘       │
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐       │
│  │ Démographie          │  │ Zone d'opération     │       │
│  │ estimée              │  │ Carte Algérie        │       │
│  │ (genre, âge)         │  │                      │       │
│  └──────────────────────┘  └──────────────────────┘       │
│                                                              │
│  [📄 Exporter en PDF]  [📊 Comparer avec un autre profil] │
└─────────────────────────────────────────────────────────────┘
```

**Description :**
- Header avec photo de profil, infos de base, et score global proéminent
- Ligne de métriques clés en cards compactes
- Section graphiques avec onglets pour naviguer entre les vues
- Section analyse détaillée en grille de cards
- Boutons d'action en bas (export, comparaison)
- Toutes les cards avec bordure glow subtile et hover effect

#### 6.2.4 Écran de comparaison côte-à-côte

```
┌──────────────────────────────────────────────────────────────┐
│  COMPARAISON                          [+ Ajouter un profil] │
│                                                               │
│  ┌──────────────────────┐  VS  ┌──────────────────────────┐ │
│  │  @influenceur_A      │      │  @influenceur_B          │ │
│  │  Score: 7.2/10       │      │  Score: 4.1/10           │ │
│  │  ✅ BON              │      │  ⚠️ DOUTEUX              │ │
│  └──────────────────────┘      └──────────────────────────┘ │
│                                                               │
│  ── Comparaison détaillée ──                                 │
│  ┌───────────────────┬────────────┬──────────────┐          │
│  │ Critère           │ Profil A   │ Profil B     │          │
│  ├───────────────────┼────────────┼──────────────┤          │
│  │ Followers         │ 125,400    │ 340,200      │          │
│  │ Engagement réel   │ 4.2%      │ 0.8%         │          │
│  │ Faux followers    │ ~18%      │ ~62%         │          │
│  │ Score commentaires│ 8.1/10    │ 2.3/10       │          │
│  │ Croissance        │ Organique │ Suspecte     │          │
│  │ Sentiment         │ 78% pos.  │ 45% pos.     │          │
│  └───────────────────┴────────────┴──────────────┘          │
│                                                               │
│  ── Graphiques superposés ──                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Radar comparatif des deux profils                    │   │
│  │  (lignes superposées en cyan et violet)               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  VERDICT : @influenceur_A est significativement plus         │
│  fiable que @influenceur_B pour un partenariat commercial.   │
└──────────────────────────────────────────────────────────────┘
```

**Description :**
- Deux profils affichés côte-à-côte
- Tableau comparatif avec code couleur (vert/rouge) par ligne
- Graphique radar superposé pour comparaison visuelle
- Verdict textuel automatique en bas
- Possibilité d'ajouter jusqu'à 4 profils en comparaison

#### 6.2.5 Écran OCR - Upload de capture d'écran

```
┌─────────────────────────────────────────────────────────┐
│  ANALYSE PAR CAPTURE D'ÉCRAN                            │
│                                                          │
│  ┌──────────────────────────────────────────────┐       │
│  │                                               │       │
│  │     Glissez-déposez votre capture ici         │       │
│  │     ou cliquez pour sélectionner              │       │
│  │                                               │       │
│  │     📷  Formats: PNG, JPG, WEBP              │       │
│  │         Max: 10 MB                            │       │
│  │                                               │       │
│  └──────────────────────────────────────────────┘       │
│                                                          │
│  ── Résultat OCR ──                                     │
│  ┌──────────────────────────────────────────────┐       │
│  │  Données extraites :                          │       │
│  │                                               │       │
│  │  Username:  [@influenceur_dz    ] ✏️          │       │
│  │  Followers: [125,400            ] ✏️          │       │
│  │  Following: [890                ] ✏️          │       │
│  │  Posts:     [432                ] ✏️          │       │
│  │  Plateforme: (●) Instagram  ( ) TikTok       │       │
│  │                                               │       │
│  │  Confiance OCR: 94%                           │       │
│  │                                               │       │
│  │  [Corriger les données]  [Lancer l'analyse]  │       │
│  └──────────────────────────────────────────────┘       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Description :**
- Zone de drag-and-drop avec feedback visuel
- Aperçu de l'image uploadée
- Données extraites par OCR dans des champs éditables
- Indicateur de confiance de l'OCR
- L'utilisateur peut corriger manuellement avant de lancer l'analyse

### 6.3 Responsive Design

| Breakpoint | Largeur | Adaptation |
|------------|---------|------------|
| Desktop | > 1200px | Layout complet en grille |
| Tablette | 768px - 1200px | Grille réduite à 2 colonnes |
| Mobile | < 768px | Layout single column, cards empilées |

L'APK Android affichera la même interface web via Capacitor, optimisée pour le format mobile.

### 6.4 Animations et micro-interactions

| Élément | Animation | Durée |
|---------|-----------|-------|
| Score global | Compteur qui monte de 0 au score final | 1.5s |
| Jauges circulaires | Remplissage progressif | 1s |
| Cards | Fade-in séquentiel au scroll | 0.3s chaque |
| Graphiques | Draw animation (dessin progressif) | 1s |
| Hover sur cards | Légère élévation + intensification du glow | 0.2s |
| Boutons | Pulse lumineux au hover | 0.3s |
| Barre de progression | Gradient animé cyan/violet | continu |
| Données en cours de chargement | Skeleton loading avec pulse | continu |

---

## 7. Architecture technique

### 7.1 Vue d'ensemble de l'architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT                                │
│                                                          │
│  ┌──────────────┐    ┌──────────────────┐              │
│  │ React + Vite │    │ Capacitor.js     │              │
│  │ TailwindCSS  │    │ (APK Android)    │              │
│  │ Recharts     │    │                  │              │
│  │ Tesseract.js │    │ WebView wrapper  │              │
│  └──────┬───────┘    └────────┬─────────┘              │
│         │                      │                         │
│         └──────────┬───────────┘                         │
│                    │ HTTP/REST API                        │
└────────────────────┼────────────────────────────────────┘
                     │
┌────────────────────┼────────────────────────────────────┐
│                    │ SERVEUR                              │
│                    ▼                                      │
│  ┌──────────────────────────────────────┐               │
│  │         Python FastAPI               │               │
│  │                                       │               │
│  │  ┌───────────┐  ┌──────────────┐    │               │
│  │  │ API       │  │ Scraping     │    │               │
│  │  │ Routes    │  │ Engine       │    │               │
│  │  └───────────┘  └──────────────┘    │               │
│  │                                       │               │
│  │  ┌───────────┐  ┌──────────────┐    │               │
│  │  │ Analysis  │  │ NLP          │    │               │
│  │  │ Engine    │  │ Processor    │    │               │
│  │  └───────────┘  └──────────────┘    │               │
│  │                                       │               │
│  │  ┌───────────┐  ┌──────────────┐    │               │
│  │  │ Score     │  │ Background   │    │               │
│  │  │ Calculator│  │ Tasks        │    │               │
│  │  └───────────┘  └──────────────┘    │               │
│  └───────────────────┬──────────────────┘               │
│                      │                                    │
│  ┌───────────────────▼──────────────────┐               │
│  │           Base de données             │               │
│  │  SQLite (dev) / PostgreSQL (prod)     │               │
│  └──────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
```

### 7.2 Stack technique détaillé

#### 7.2.1 Backend

| Composant | Technologie | Version | Justification |
|-----------|------------|---------|---------------|
| Framework | Python FastAPI | 0.100+ | Haute performance, async natif, documentation auto |
| Serveur ASGI | Uvicorn | 0.27+ | Serveur async performant |
| ORM | SQLAlchemy | 2.0+ | ORM mature, support async |
| Migration DB | Alembic | 1.13+ | Migrations versionnées |
| Scraping Instagram | Instaloader | 4.10+ | Scraping Instagram sans API officielle |
| Scraping TikTok | TikTokApi (unofficial) | 6.0+ | Accès aux données TikTok |
| NLP | spaCy / TextBlob | - | Analyse de sentiment légère |
| Background tasks | Celery + Redis | - | Option future pour les tâches longues |
| Validation | Pydantic | 2.0+ | Validation des données, sérialisation |

#### 7.2.2 Frontend

| Composant | Technologie | Version | Justification |
|-----------|------------|---------|---------------|
| Framework | React | 18+ | Écosystème riche, composants réutilisables |
| Build tool | Vite | 5+ | Build rapide, HMR instantané |
| CSS | TailwindCSS | 3+ | Utility-first, prototypage rapide |
| Graphiques | Recharts | 2+ | Composants React natifs, responsive |
| Graphiques alt. | Chart.js + react-chartjs-2 | 4+ | Fallback pour graphiques complexes |
| OCR | Tesseract.js | 5+ | OCR côté client, pas de serveur nécessaire |
| HTTP Client | Axios | 1+ | Interceptors, gestion d'erreurs |
| State management | Zustand | 4+ | Léger, simple, performant |
| Animations | Framer Motion | 10+ | Animations fluides et déclaratives |
| Routing | React Router | 6+ | Navigation SPA |
| Icônes | Lucide React | - | Icônes modernes, style linéaire |

#### 7.2.3 Mobile

| Composant | Technologie | Justification |
|-----------|------------|---------------|
| Wrapper | Capacitor.js | Convertit l'app web en APK Android |
| Plugins | Camera, Filesystem | Accès caméra pour OCR, stockage local |
| Build | Android Studio / CLI | Compilation APK |

#### 7.2.4 Base de données

| Environnement | Technologie | Justification |
|---------------|------------|---------------|
| Développement | SQLite | Zéro configuration, fichier unique |
| Production | PostgreSQL 16+ | Performance, concurrence, scalabilité |

### 7.3 Structure du projet

```
RA/
├── docs/
│   └── Cahier_des_Charges_RA.md
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # Point d'entrée FastAPI
│   │   ├── config.py                # Configuration
│   │   ├── database.py              # Connexion DB
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── influencer.py        # Modèle Influencer
│   │   │   ├── snapshot.py          # Modèle Snapshot
│   │   │   ├── comment.py           # Modèle CommentAnalysis
│   │   │   ├── demographic.py       # Modèle AudienceDemographic
│   │   │   └── score.py             # Modèle Score
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── influencer.py        # Schémas Pydantic
│   │   │   ├── analysis.py
│   │   │   └── response.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── analyze.py       # POST /analyze
│   │   │   │   ├── influencer.py    # GET /influencer/{id}
│   │   │   │   ├── compare.py       # POST /compare
│   │   │   │   ├── history.py       # GET /history
│   │   │   │   └── health.py        # GET /health
│   │   │   └── dependencies.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── scraper_instagram.py # Scraping Instagram
│   │   │   ├── scraper_tiktok.py    # Scraping TikTok
│   │   │   ├── analyzer.py          # Moteur d'analyse principal
│   │   │   ├── engagement.py        # Calcul engagement
│   │   │   ├── fake_detector.py     # Détection faux followers
│   │   │   ├── growth_analyzer.py   # Analyse de croissance
│   │   │   ├── nlp_processor.py     # Analyse NLP des commentaires
│   │   │   ├── demographic_estimator.py  # Estimation démographie
│   │   │   ├── location_detector.py # Détection de localisation
│   │   │   └── score_calculator.py  # Calcul du score global
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── number_parser.py     # Parse 12.5K => 12500
│   │       ├── rate_limiter.py      # Anti-détection
│   │       └── validators.py        # Validations custom
│   ├── alembic/
│   │   └── versions/
│   ├── tests/
│   │   ├── test_analyzer.py
│   │   ├── test_scraper.py
│   │   └── test_score.py
│   ├── requirements.txt
│   ├── alembic.ini
│   └── Dockerfile
├── frontend/
│   ├── public/
│   │   ├── favicon.ico
│   │   └── logo.svg
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── index.css                # TailwindCSS imports
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── Footer.jsx
│   │   │   │   └── Sidebar.jsx
│   │   │   ├── search/
│   │   │   │   ├── SearchBar.jsx
│   │   │   │   ├── PlatformToggle.jsx
│   │   │   │   └── MultiAccountInput.jsx
│   │   │   ├── analysis/
│   │   │   │   ├── ScoreGauge.jsx
│   │   │   │   ├── EngagementChart.jsx
│   │   │   │   ├── GrowthChart.jsx
│   │   │   │   ├── FakeFollowerMeter.jsx
│   │   │   │   ├── CommentAnalysis.jsx
│   │   │   │   ├── DemographicChart.jsx
│   │   │   │   ├── LocationMap.jsx
│   │   │   │   └── RadarHealth.jsx
│   │   │   ├── comparison/
│   │   │   │   ├── CompareTable.jsx
│   │   │   │   └── CompareRadar.jsx
│   │   │   ├── ocr/
│   │   │   │   ├── ScreenshotUpload.jsx
│   │   │   │   └── OcrResultEditor.jsx
│   │   │   └── ui/
│   │   │       ├── Card.jsx
│   │   │       ├── Button.jsx
│   │   │       ├── ProgressBar.jsx
│   │   │       ├── Skeleton.jsx
│   │   │       └── Badge.jsx
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   ├── AnalysisPage.jsx
│   │   │   ├── ComparePage.jsx
│   │   │   ├── OcrPage.jsx
│   │   │   └── HistoryPage.jsx
│   │   ├── hooks/
│   │   │   ├── useAnalysis.js
│   │   │   ├── useOcr.js
│   │   │   └── useComparison.js
│   │   ├── store/
│   │   │   └── analysisStore.js     # Zustand store
│   │   ├── services/
│   │   │   └── api.js               # Axios instance + endpoints
│   │   └── utils/
│   │       ├── formatters.js        # Formatage nombres, dates
│   │       └── constants.js         # Couleurs, seuils
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── capacitor.config.ts
├── mobile/
│   ├── android/                     # Généré par Capacitor
│   └── capacitor.config.ts
├── .gitignore
├── docker-compose.yml
└── README.md
```

### 7.4 API REST - Endpoints

#### 7.4.1 Analyse

| Méthode | Endpoint | Description | Body/Params |
|---------|----------|-------------|-------------|
| `POST` | `/api/v1/analyze` | Lancer une analyse complète | `{ "username": str, "platform": "instagram"\|"tiktok" }` |
| `GET` | `/api/v1/analyze/{task_id}` | Statut d'une analyse en cours | - |
| `POST` | `/api/v1/analyze/ocr` | Analyse depuis données OCR | `{ "username": str, "followers": int, "following": int, "posts": int, "platform": str }` |
| `POST` | `/api/v1/analyze/batch` | Analyse multi-comptes | `{ "accounts": [{ "username": str, "platform": str }] }` |

#### 7.4.2 Influenceurs

| Méthode | Endpoint | Description | Body/Params |
|---------|----------|-------------|-------------|
| `GET` | `/api/v1/influencer/{id}` | Détails d'un influenceur analysé | - |
| `GET` | `/api/v1/influencer/{id}/snapshots` | Historique des snapshots | `?limit=10&offset=0` |
| `GET` | `/api/v1/influencer/{id}/score-history` | Évolution du score dans le temps | `?period=30d` |

#### 7.4.3 Comparaison

| Méthode | Endpoint | Description | Body/Params |
|---------|----------|-------------|-------------|
| `POST` | `/api/v1/compare` | Comparer plusieurs profils | `{ "influencer_ids": [int] }` |

#### 7.4.4 Historique

| Méthode | Endpoint | Description | Body/Params |
|---------|----------|-------------|-------------|
| `GET` | `/api/v1/history` | Liste des analyses récentes | `?limit=20&offset=0` |
| `DELETE` | `/api/v1/history/{id}` | Supprimer une analyse de l'historique | - |

#### 7.4.5 Système

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/v1/health` | Statut de l'API |
| `GET` | `/docs` | Documentation Swagger auto-générée |

### 7.5 Stratégie de scraping et anti-détection

#### 7.5.1 Instagram via Instaloader

**Données récupérables :**
- Profil public : username, bio, followers, following, nombre de posts, photo de profil
- Posts récents (jusqu'à 30) : likes, commentaires, date, type de média, légende
- Commentaires (échantillon des plus récents par post)
- Pas besoin de compte Instagram pour les profils publics

**Mesures anti-détection :**
- Délai aléatoire entre les requêtes (3 à 8 secondes)
- Rotation de User-Agent
- Limite de requêtes par heure (max 30 analyses/heure)
- Session persistante avec cookies
- Possibilité d'utiliser des proxies rotatifs (option future)

#### 7.5.2 TikTok via API non officielle

**Données récupérables :**
- Profil : username, bio, followers, following, likes totaux
- Vidéos récentes : vues, likes, commentaires, partages
- Commentaires (échantillon)

**Mesures anti-détection :**
- Simulation de navigation réelle (Playwright/Selenium en fallback)
- Rotation de proxies recommandée
- Délais aléatoires entre requêtes

#### 7.5.3 Gestion des erreurs de scraping

| Erreur | Action |
|--------|--------|
| Profil privé | Message clair à l'utilisateur, suggestion d'utiliser OCR |
| Rate limit atteint | File d'attente, retry après délai, notification utilisateur |
| Profil inexistant | Message d'erreur, suggestions de correction |
| Données partielles | Analyse avec données disponibles + avertissement |
| Scraping bloqué | Fallback sur mode OCR, alerte admin |

---

## 8. Modèle de données

### 8.1 Diagramme entité-relation

```
┌──────────────────┐       ┌──────────────────────┐
│   influencers    │       │     snapshots         │
├──────────────────┤       ├──────────────────────┤
│ id (PK)          │──┐    │ id (PK)              │
│ username         │  │    │ influencer_id (FK)   │──┐
│ platform         │  ├───>│ followers_count      │  │
│ display_name     │  │    │ following_count      │  │
│ bio              │  │    │ posts_count          │  │
│ profile_pic_url  │  │    │ avg_likes            │  │
│ is_verified      │  │    │ avg_comments         │  │
│ location_wilaya  │  │    │ avg_shares           │  │
│ location_city    │  │    │ engagement_rate_raw  │  │
│ first_seen_at    │  │    │ engagement_rate_adj  │  │
│ last_analyzed_at │  │    │ estimated_fake_pct   │  │
│ created_at       │  │    │ growth_rate_daily    │  │
│ updated_at       │  │    │ posts_analyzed       │  │
└──────────────────┘  │    │ data_source          │
                      │    │ created_at           │
                      │    └──────────────────────┘
                      │
                      │    ┌──────────────────────┐
                      │    │  comments_analysis    │
                      │    ├──────────────────────┤
                      ├───>│ id (PK)              │
                      │    │ snapshot_id (FK)     │
                      │    │ total_comments       │
                      │    │ bot_comments_pct     │
                      │    │ real_comments_pct    │
                      │    │ uncertain_pct        │
                      │    │ sentiment_positive   │
                      │    │ sentiment_neutral    │
                      │    │ sentiment_negative   │
                      │    │ unique_commenters    │
                      │    │ diversity_ratio      │
                      │    │ top_bot_comments     │  (JSON)
                      │    │ word_cloud_data      │  (JSON)
                      │    │ created_at           │
                      │    └──────────────────────┘
                      │
                      │    ┌──────────────────────────┐
                      │    │  audience_demographics    │
                      │    ├──────────────────────────┤
                      ├───>│ id (PK)                  │
                      │    │ snapshot_id (FK)         │
                      │    │ est_male_pct             │
                      │    │ est_female_pct           │
                      │    │ est_unknown_gender_pct   │
                      │    │ est_age_13_17_pct        │
                      │    │ est_age_18_24_pct        │
                      │    │ est_age_25_34_pct        │
                      │    │ est_age_35_44_pct        │
                      │    │ est_age_45_plus_pct      │
                      │    │ est_algeria_pct          │
                      │    │ est_other_countries_pct  │
                      │    │ top_wilayas              │  (JSON)
                      │    │ estimation_confidence    │
                      │    │ created_at               │
                      │    └──────────────────────────┘
                      │
                      │    ┌──────────────────────┐
                      │    │      scores           │
                      │    ├──────────────────────┤
                      └───>│ id (PK)              │
                           │ snapshot_id (FK)     │
                           │ influencer_id (FK)   │
                           │ score_global         │  (0-10)
                           │ score_engagement     │  (0-10)
                           │ score_authenticity   │  (0-10)
                           │ score_comments       │  (0-10)
                           │ score_growth         │  (0-10)
                           │ score_diversity      │  (0-10)
                           │ score_activity       │  (0-10)
                           │ label                │  (ex: "BON")
                           │ color_code           │
                           │ created_at           │
                           └──────────────────────┘
```

### 8.2 Description détaillée des tables

#### Table `influencers`

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTO_INCREMENT | Identifiant unique |
| `username` | VARCHAR(100) | NOT NULL, UNIQUE (avec platform) | Nom d'utilisateur sur la plateforme |
| `platform` | VARCHAR(20) | NOT NULL | "instagram" ou "tiktok" |
| `display_name` | VARCHAR(200) | NULLABLE | Nom affiché |
| `bio` | TEXT | NULLABLE | Biographie du profil |
| `profile_pic_url` | VARCHAR(500) | NULLABLE | URL de la photo de profil |
| `is_verified` | BOOLEAN | DEFAULT FALSE | Compte vérifié ou non |
| `location_wilaya` | VARCHAR(50) | NULLABLE | Wilaya estimée |
| `location_city` | VARCHAR(100) | NULLABLE | Ville estimée |
| `first_seen_at` | TIMESTAMP | NOT NULL | Date de première analyse |
| `last_analyzed_at` | TIMESTAMP | NOT NULL | Date de dernière analyse |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Date de création |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Date de mise à jour |

**Index :** `UNIQUE(username, platform)`, `INDEX(location_wilaya)`, `INDEX(last_analyzed_at)`

#### Table `snapshots`

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTO_INCREMENT | Identifiant unique |
| `influencer_id` | INTEGER | FK -> influencers.id | Référence à l'influenceur |
| `followers_count` | INTEGER | NOT NULL | Nombre de followers au moment du snapshot |
| `following_count` | INTEGER | NOT NULL | Nombre de following |
| `posts_count` | INTEGER | NOT NULL | Nombre total de posts |
| `avg_likes` | FLOAT | NULLABLE | Moyenne de likes sur les posts analysés |
| `avg_comments` | FLOAT | NULLABLE | Moyenne de commentaires |
| `avg_shares` | FLOAT | NULLABLE | Moyenne de partages (TikTok) |
| `engagement_rate_raw` | FLOAT | NULLABLE | Taux d'engagement brut |
| `engagement_rate_adj` | FLOAT | NULLABLE | Taux d'engagement ajusté |
| `estimated_fake_pct` | FLOAT | NULLABLE | Pourcentage estimé de faux followers |
| `growth_rate_daily` | FLOAT | NULLABLE | Taux de croissance quotidien |
| `posts_analyzed` | INTEGER | DEFAULT 0 | Nombre de posts analysés |
| `data_source` | VARCHAR(20) | NOT NULL | "scraping" ou "ocr" |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Date du snapshot |

**Index :** `INDEX(influencer_id, created_at)`

#### Table `comments_analysis`

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTO_INCREMENT | Identifiant unique |
| `snapshot_id` | INTEGER | FK -> snapshots.id | Référence au snapshot |
| `total_comments` | INTEGER | NOT NULL | Nombre total de commentaires analysés |
| `bot_comments_pct` | FLOAT | NOT NULL | % de commentaires détectés comme bots |
| `real_comments_pct` | FLOAT | NOT NULL | % de commentaires réels |
| `uncertain_pct` | FLOAT | NOT NULL | % de commentaires incertains |
| `sentiment_positive` | FLOAT | NOT NULL | % de sentiment positif |
| `sentiment_neutral` | FLOAT | NOT NULL | % de sentiment neutre |
| `sentiment_negative` | FLOAT | NOT NULL | % de sentiment négatif |
| `unique_commenters` | INTEGER | NOT NULL | Nombre de commentateurs uniques |
| `diversity_ratio` | FLOAT | NOT NULL | Ratio commentateurs uniques / total |
| `top_bot_comments` | JSON | NULLABLE | Liste des commentaires les plus suspects |
| `word_cloud_data` | JSON | NULLABLE | Données pour le nuage de mots |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Date de l'analyse |

#### Table `audience_demographics`

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTO_INCREMENT | Identifiant unique |
| `snapshot_id` | INTEGER | FK -> snapshots.id | Référence au snapshot |
| `est_male_pct` | FLOAT | NULLABLE | % estimé d'hommes |
| `est_female_pct` | FLOAT | NULLABLE | % estimé de femmes |
| `est_unknown_gender_pct` | FLOAT | NULLABLE | % genre non déterminé |
| `est_age_13_17_pct` | FLOAT | NULLABLE | % estimé 13-17 ans |
| `est_age_18_24_pct` | FLOAT | NULLABLE | % estimé 18-24 ans |
| `est_age_25_34_pct` | FLOAT | NULLABLE | % estimé 25-34 ans |
| `est_age_35_44_pct` | FLOAT | NULLABLE | % estimé 35-44 ans |
| `est_age_45_plus_pct` | FLOAT | NULLABLE | % estimé 45+ ans |
| `est_algeria_pct` | FLOAT | NULLABLE | % estimé audience algérienne |
| `est_other_countries_pct` | FLOAT | NULLABLE | % estimé hors Algérie |
| `top_wilayas` | JSON | NULLABLE | Top wilayas détectées `[{"wilaya": "Alger", "pct": 35}, ...]` |
| `estimation_confidence` | VARCHAR(10) | NOT NULL | "low", "medium", "high" |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Date de l'estimation |

#### Table `scores`

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTO_INCREMENT | Identifiant unique |
| `snapshot_id` | INTEGER | FK -> snapshots.id, UNIQUE | Référence au snapshot |
| `influencer_id` | INTEGER | FK -> influencers.id | Référence à l'influenceur |
| `score_global` | FLOAT | NOT NULL, CHECK(0-10) | Score global composite |
| `score_engagement` | FLOAT | NOT NULL, CHECK(0-10) | Sous-score engagement |
| `score_authenticity` | FLOAT | NOT NULL, CHECK(0-10) | Sous-score authenticité |
| `score_comments` | FLOAT | NOT NULL, CHECK(0-10) | Sous-score qualité commentaires |
| `score_growth` | FLOAT | NOT NULL, CHECK(0-10) | Sous-score croissance |
| `score_diversity` | FLOAT | NOT NULL, CHECK(0-10) | Sous-score diversité audience |
| `score_activity` | FLOAT | NOT NULL, CHECK(0-10) | Sous-score activité |
| `label` | VARCHAR(20) | NOT NULL | Label textuel (ex: "BON", "SUSPECT") |
| `color_code` | VARCHAR(7) | NOT NULL | Code couleur hex |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Date du score |

**Index :** `INDEX(influencer_id, created_at)` pour l'historique des scores

---

## 9. Contraintes techniques et non-fonctionnelles

### 9.1 Performance

| Métrique | Objectif | Mesure |
|----------|----------|--------|
| Temps d'analyse complet (scraping) | < 60 secondes | Du lancement au résultat |
| Temps d'analyse OCR | < 10 secondes | De l'upload au résultat |
| Temps de chargement page | < 3 secondes | First Contentful Paint |
| Taille du bundle frontend | < 500 KB (gzippé) | Production build |
| Taille de l'APK | < 30 MB | APK final signé |
| Requêtes API | < 200ms | Endpoints de lecture |

### 9.2 Scalabilité

- L'architecture doit supporter jusqu'à 100 analyses simultanées en production
- La base de données doit supporter jusqu'à 100 000 profils analysés
- Le passage de SQLite à PostgreSQL ne doit nécessiter qu'un changement de configuration

### 9.3 Sécurité

| Mesure | Description |
|--------|-------------|
| Rate limiting | Max 30 requêtes d'analyse par IP par heure |
| Input validation | Sanitisation de tous les inputs utilisateur (Pydantic) |
| CORS | Configuration stricte des origines autorisées |
| Headers de sécurité | HSTS, X-Frame-Options, CSP |
| Pas d'authentification | v1 sans comptes utilisateurs (accès libre) |
| Logs | Logging des requêtes sans données personnelles |

### 9.4 Fiabilité

- Gestion gracieuse des erreurs de scraping (fallback, retry, mode dégradé)
- Données en cache pour les profils récemment analysés (TTL: 1 heure)
- Sauvegarde automatique des résultats en base de données
- Mode hors-ligne partiel pour l'APK (consultation des résultats en cache)

### 9.5 Compatibilité

| Plateforme | Versions supportées |
|------------|---------------------|
| Chrome | 90+ |
| Firefox | 90+ |
| Safari | 14+ |
| Edge | 90+ |
| Android (APK) | 8.0+ (API 26) |
| Résolution minimale | 360px de large |

### 9.6 Internationalisation

- Interface en français par défaut
- Support futur possible de l'arabe (RTL layout)
- Analyse NLP en français, arabe standard, et darija algérienne
- Formats de nombres : support des séparateurs point et virgule

### 9.7 Contraintes légales et éthiques

| Point | Approche |
|-------|----------|
| Scraping | Uniquement sur des profils publics |
| RGPD / Loi algérienne | Aucune donnée personnelle stockée au-delà des infos publiques |
| Mention | Avertissement que les résultats sont des estimations |
| Responsabilité | Disclaimer : les scores sont indicatifs et non contractuels |
| Droits d'auteur | Pas de stockage de contenu (photos, vidéos) des influenceurs |

---

## 10. Phases de développement

### Phase 1 : Backend API + Database + Scraping Instagram

**Durée estimée :** 2 semaines

**Livrables :**
- Projet FastAPI initialisé avec structure complète
- Base de données SQLite avec toutes les tables (migrations Alembic)
- Scraping Instagram fonctionnel via Instaloader
  - Récupération profil public
  - Récupération des 30 derniers posts
  - Récupération échantillon de commentaires
- Service de calcul d'engagement (brut + ajusté)
- Service de détection de faux followers (critères de base)
- Service de calcul du score global
- Endpoints API : `/analyze`, `/influencer/{id}`, `/health`
- Documentation Swagger automatique
- Tests unitaires pour les services d'analyse

**Critères d'acceptation :**
- L'API peut recevoir un @username Instagram et retourner un score
- Les données sont persistées en SQLite
- Le temps d'analyse est inférieur à 60 secondes
- Les tests passent à 100%

---

### Phase 2 : Frontend Web avec dashboard investigateur

**Durée estimée :** 2 semaines

**Livrables :**
- Projet React + Vite + TailwindCSS initialisé
- Thème sombre "cyber investigation" implémenté
- Page d'accueil avec barre de recherche
- Écran de chargement avec progression en temps réel
- Dashboard de résultats avec :
  - Card profil + score global (jauge animée)
  - Graphique d'engagement par post (Recharts)
  - Jauge de faux followers
  - Graphique radar de santé du profil
  - Cards métriques clés
- Page d'historique des analyses
- Responsive design (desktop + mobile)
- Animations et micro-interactions (Framer Motion)
- Connexion à l'API backend

**Critères d'acceptation :**
- L'utilisateur peut saisir un @username et voir le dashboard complet
- L'interface est responsive sur mobile
- Les graphiques sont interactifs (hover, tooltips)
- Le thème visuel correspond à la direction artistique

---

### Phase 3 : Scraping TikTok

**Durée estimée :** 1 semaine

**Livrables :**
- Intégration de l'API TikTok non officielle
- Adaptation des services d'analyse pour TikTok :
  - Prise en compte des vues (spécifique TikTok)
  - Adaptation des seuils d'engagement (TikTok vs Instagram)
  - Prise en compte des partages dans le score
- Toggle Instagram/TikTok sur le frontend
- Adaptation des graphiques pour les métriques TikTok
- Tests unitaires pour le scraping TikTok

**Critères d'acceptation :**
- L'analyse TikTok fonctionne de bout en bout
- Les métriques TikTok sont correctement affichées
- Le score global intègre les particularités TikTok

---

### Phase 4 : OCR captures d'écran

**Durée estimée :** 1 semaine

**Livrables :**
- Intégration de Tesseract.js côté frontend
- Interface d'upload avec drag-and-drop
- Extraction OCR des données de profil
- Formulaire de correction des données extraites
- Endpoint API `/analyze/ocr` pour l'analyse en mode OCR
- Support des formats de nombres (12.5K, 1.2M, etc.)
- Analyse en mode dégradé (sans scraping, basée uniquement sur les données OCR)

**Critères d'acceptation :**
- L'OCR extrait correctement les données d'une capture Instagram dans >85% des cas
- L'OCR extrait correctement les données d'une capture TikTok dans >80% des cas
- L'utilisateur peut corriger les données avant analyse
- L'analyse OCR produit un résultat en moins de 10 secondes

---

### Phase 5 : APK via Capacitor

**Durée estimée :** 1 semaine

**Livrables :**
- Configuration Capacitor.js
- Adaptation du frontend pour le contexte mobile natif
- Plugin caméra pour capture d'écran directe
- Plugin filesystem pour stockage local
- Build APK fonctionnel
- Test sur appareils Android physiques (Samsung, Huawei, Oppo - marques courantes en Algérie)
- Optimisation des performances sur appareils d'entrée de gamme

**Critères d'acceptation :**
- L'APK s'installe et fonctionne sur Android 8+
- L'APK fait moins de 30 MB
- La navigation est fluide sur appareils d'entrée de gamme
- L'accès caméra fonctionne pour l'OCR

---

### Phase 6 : NLP commentaires avancé

**Durée estimée :** 2 semaines

**Livrables :**
- Amélioration du modèle de détection de bots
  - Classification multi-catégories (bot, spam, réel, incertain)
  - Base de données de patterns de commentaires bots
  - Prise en compte du contexte algérien (darija, expressions courantes)
- Analyse de sentiment améliorée
  - Support du français
  - Support de l'arabe (MSA)
  - Support basique du darija algérien (dictionnaire custom)
  - Support de l'arabizi (darija en lettres latines)
- Nuage de mots dans le dashboard
- Graphiques de sentiment (positif/neutre/négatif)
- Score de diversité des commentateurs affiché
- Estimation démographie basée sur les commentateurs
- Carte de l'Algérie avec zones d'opération estimées

**Critères d'acceptation :**
- La détection de bots a une précision >70%
- L'analyse de sentiment fonctionne en français et arabe
- Le nuage de mots est affiché et pertinent
- La démographie estimée est affichée avec un indice de confiance

---

### Récapitulatif du planning

```
Semaine  1  2  3  4  5  6  7  8  9
Phase 1  ████████
Phase 2           ████████
Phase 3                    ████
Phase 4                        ████
Phase 5                            ████
Phase 6                                ████████
```

**Durée totale estimée : 9 semaines**

---

## 11. Risques et mitigations

### 11.1 Risques techniques

| # | Risque | Probabilité | Impact | Mitigation |
|---|--------|-------------|--------|------------|
| R1 | Instagram bloque le scraping (rate limit, ban IP) | Élevée | Critique | Rotation de proxies, délais aléatoires, mode OCR en fallback |
| R2 | API TikTok non officielle cesse de fonctionner | Moyenne | Élevé | Fallback sur scraping Playwright, mode OCR |
| R3 | Précision OCR insuffisante | Faible | Moyen | Prétraitement image amélioré, correction manuelle |
| R4 | NLP imprécis sur le darija | Élevée | Moyen | Dictionnaire custom, amélioration continue, feedback utilisateur |
| R5 | Performance insuffisante sur mobiles d'entrée de gamme | Moyenne | Moyen | Optimisation bundle, lazy loading, réduction animations |
| R6 | Changement de structure des pages Instagram/TikTok | Moyenne | Élevé | Architecture modulaire des scrapers, mises à jour rapides |

### 11.2 Risques opérationnels

| # | Risque | Probabilité | Impact | Mitigation |
|---|--------|-------------|--------|------------|
| R7 | Coûts d'hébergement si trafic important | Faible | Moyen | Architecture légère, SQLite, hébergement sur VPS existant |
| R8 | Problèmes légaux liés au scraping | Faible | Élevé | Uniquement profils publics, pas de stockage de contenu, disclaimer |
| R9 | Demandes de suppression de données | Faible | Faible | Processus de suppression simple, données non sensibles |

### 11.3 Risques liés à la qualité

| # | Risque | Probabilité | Impact | Mitigation |
|---|--------|-------------|--------|------------|
| R10 | Score global non représentatif | Moyenne | Élevé | Calibration avec des cas réels, ajustement des poids, transparence des sous-scores |
| R11 | Faux positifs (profils légitimes marqués suspects) | Moyenne | Élevé | Seuils conservateurs, explications détaillées, possibilité de feedback |
| R12 | Faux négatifs (profils frauduleux non détectés) | Moyenne | Moyen | Amélioration continue des critères, benchmarking régulier |

---

## 12. Annexes

### Annexe A : Benchmarks d'engagement par taille de compte (Instagram Algérie)

| Taille du compte | ER moyen attendu | Seuil suspect |
|------------------|------------------|---------------|
| Nano (1K - 10K) | 5% - 10% | < 2% |
| Micro (10K - 50K) | 3% - 6% | < 1.5% |
| Mid (50K - 200K) | 2% - 4% | < 1% |
| Macro (200K - 1M) | 1.5% - 3% | < 0.5% |
| Mega (> 1M) | 1% - 2% | < 0.3% |

> **Note :** Ces benchmarks sont indicatifs et devront être calibrés avec des données réelles du marché algérien au fur et à mesure de l'utilisation de l'outil.

### Annexe B : Patterns de commentaires bots courants en Algérie

**Commentaires génériques universels (score bot élevé) :**
- "Nice!", "Beautiful!", "Amazing!", "Love it!"
- "Great content!", "Keep going!", "Wonderful!"
- Séquences d'émojis seuls : "🔥🔥🔥", "❤️❤️❤️", "💯💯"

**Commentaires en arabe/darija courants mais légitimes (score bot faible) :**
- "ماشاء الله" (Mashallah)
- "تبارك الله" (Tabarak Allah)
- "يعطيك الصحة" (Yatik saha)
- "ربي يحفظك" (Rabbi yahfdek)
- "صح عيدك" / "رمضان كريم" (expressions saisonnières)

**Spam / Promotion (score bot très élevé) :**
- "DM me for collaboration"
- "Check my page for..."
- "I help influencers grow..."
- Commentaires avec des liens

### Annexe C : Liste des hashtags géographiques algériens

```
#alger #oran #constantine #annaba #setif #blida #batna #tlemcen
#bejaia #biskra #tiziouzou #djelfa #msila #chlef #medea
#sidibelabbes #skikda #mostaganem #jijel #relizane #saida
#guelma #oumelbouaghi #bouira #boumerdes #tebessa #khenchela
#soukahras #mila #tiaret #tipaza #tissemsilt #bordj #mascara
#algerie #dz #teamdz #algerienne #algerien #dzpower
#algeria #algiers #visitalgeria #exploredz
```

### Annexe D : Glossaire

| Terme | Définition |
|-------|------------|
| **ER (Engagement Rate)** | Taux d'engagement - ratio interactions/followers |
| **Fake followers** | Comptes fictifs ou inactifs qui suivent un profil |
| **Pod d'engagement** | Groupe privé de comptes qui s'engagent mutuellement pour gonfler les métriques |
| **Snapshot** | Capture de l'état d'un profil à un instant donné |
| **Darija** | Dialecte arabe algérien |
| **Arabizi** | Écriture du darija en lettres latines et chiffres (ex: "3ayni" pour "عيني") |
| **MSA** | Modern Standard Arabic - arabe standard moderne |
| **Wilaya** | Division administrative de l'Algérie (équivalent d'une région/département) |
| **NLP** | Natural Language Processing - traitement automatique du langage naturel |
| **OCR** | Optical Character Recognition - reconnaissance optique de caractères |
| **Scraping** | Extraction automatisée de données depuis des pages web |
| **Rate limiting** | Limitation du nombre de requêtes sur une période donnée |
| **Fallback** | Mécanisme de secours quand le mécanisme principal échoue |

### Annexe E : Références et ressources

- **Instaloader** : https://instaloader.github.io/
- **FastAPI** : https://fastapi.tiangolo.com/
- **Tesseract.js** : https://tesseract.projectnaptha.com/
- **Recharts** : https://recharts.org/
- **Capacitor.js** : https://capacitorjs.com/
- **TailwindCSS** : https://tailwindcss.com/
- **spaCy** : https://spacy.io/
- **Framer Motion** : https://www.framer.com/motion/

---

*Document généré le 19 mars 2026. Ce cahier des charges est un document vivant qui sera mis à jour au fur et à mesure de l'avancement du projet.*
