# CivilCalc RPA 2024

**Calcul parasismique — Règlement Parasismique Algérien RPA 2024 (DTR BC 2.48)**

Application de bureau pour le calcul et la vérification parasismique des bâtiments selon le RPA 2024. Interface graphique PySide6, moteurs de calcul modulaires, intégration ETABS via COM, génération de rapports PDF/Word.

---

## Table des matières

- [Aperçu](#aperçu)
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Architecture](#architecture)
- [Moteurs de calcul](#moteurs-de-calcul)
- [Intégration ETABS](#intégration-etabs)
- [Structure du projet](#structure-du-projet)
- [Tests](#tests)
- [Dépendances](#dépendances)
- [Références](#références)

---

## Aperçu

CivilCalc RPA 2024 est un outil de calcul parasismique conforme au **Règlement Parasismique Algérien RPA 2024 (DTR BC 2.48)**. Il couvre l'ensemble du cycle de vérification sismique d'un bâtiment :

1. Définition des paramètres sismiques (zone, site, usage, structure)
2. Génération du spectre de réponse de calcul
3. Calcul de l'effort tranchant à la base
4. Distribution des forces latérales par niveau
5. Vérification des déplacements inter-étages
6. Effet P-Delta
7. Stabilité au renversement
8. Vérification des diaphragmes (Article 5.6)
9. Justification des planchers
10. Dimensionnement des fondations
11. Dimensionnement des voiles et linteaux
12. Vérification des noyaux

---

## Fonctionnalités

### Calculs RPA 2024
- Paramètres sismiques : accélération A, importance I, site S, comportement R, qualité Qf
- Spectre de réponse élastique et de dimensionnement (4 zones, 0.01–4s)
- Effort tranchant V = λ × Sad/g(T) × W (Éqn 4.1)
- Distribution des forces par niveau (Wihi)
- Déplacements inélastiques dr = R × de
- Effet P-Delta : θk = Pk × Δk / (Vk × hk)
- Renversement : Mr vs Ms
- Facteur de qualité Qf = 1 + Σ(Pq) (Tableau 3.18, Éqn 3.23)
- 26 types de structures avec catégories (a), (b), (c)
- Diaphragmes rigides/souples (Article 5.6 RPA 2024)

### Intégration ETABS
- Connexion COM directe à ETABS (SapModel)
- Extraction automatique : périodes modales, efforts aux étages, réactions, déplacements
- Extraction des efforts dans les voiles (Section Cut / Pier Forces)
- Détection automatique des noms de cas de charge
- Générateur de combinaisons RPA 2024 / CBA 93
- Analyse critique des poteaux (Nmax/Nmin/M3max/M2max)
- Analyse critique des poutres (M3+/M3−/V2max)
- Import alternatif par fichiers CSV/Excel

### Interface utilisateur
- Thème sombre (dark mode)
- 10 onglets spécialisés
- Graphiques interactifs (spectre, déplacements, efforts)
- Tableaux de résultats avec codes couleur
- Barre de progression multi-thread
- Base de données SQLite pour les projets

### Rapports
- Export PDF (reportlab)
- Export Word (python-docx)

---

## Installation

### Prérequis
- Python 3.9 ou supérieur
- Windows (pour le module ETABS COM)
- ETABS 19+ (optionnel, pour l'intégration COM)

### Dépendances
```bash
pip install -r requirements.txt
```

Le fichier `requirements.txt` contient :
```
numpy>=1.21
PySide6>=6.6.0
pandas>=1.3.0
comtypes>=1.1.0
openpyxl>=3.0.0
rich>=13.0.0
reportlab>=4.0.0
python-docx>=0.8.11
```

### Vérification
```bash
python tests\test_moteurs.py
```
Tous les tests doivent passer (10/10).

---

## Utilisation

### Lancement de l'interface graphique
```bash
python main.py
```
Un écran de démarrage (splash) s'affiche pendant le chargement, puis la fenêtre principale apparaît.

### Lancement en ligne de commande (tests uniquement)
```bash
python Civil_Calc_RPA2024.py
```

### Workflow typique

1. **Onglet Projet** — Saisir les informations générales (nom, dimensions, matériaux)
2. **Onglet Spectre** — Définir la zone sismique, le site, l'usage, le type de structure → calculer le spectre
3. **Onglet RPA 2024** — Saisir les données des étages (poids, hauteurs) ou importer depuis ETABS → lancer les vérifications
4. **Onglet Diaphragme** — Vérifier les diaphragmes (Article 5.6)
5. **Onglet Fondations** — Dimensionner semelles et radier
6. **Onglet Voiles** — Dimensionner les voiles et linteaux
7. **Onglet ETABS** — Connecter ETABS, extraire les données, générer les combinaisons
8. **Onglet Rapport** — Générer la note de calcul PDF ou Word

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      main.py (GUI)                      │
│              Civil_Calc_RPA2024.py (CLI)                │
├─────────────────────────────────────────────────────────┤
│                      ui/ (PySide6)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │  Tabs    │ │ MainWin  │ │ Styles   │ │ Widgets  │   │
│  │ (10 ong.)│ │          │ │ (dark)   │ │(tables,  │   │
│  │          │ │          │ │          │ │ graphes) │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
├─────────────────────────────────────────────────────────┤
│                   engines/ (moteurs)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │Spectre   │ │Cisaillem.│ │Distrib.  │ │Déplac.   │   │
│  │P-Delta   │ │Renvers.  │ │Fondations│ │Voiles    │   │
│  │Diaphragme│ │Planchers │ │Noyau     │ │Projet    │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
├─────────────────────────────────────────────────────────┤
│          etabs/ (intégration ETABS COM)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │Connector │ │Importer  │ │Combinais.│ │Extractor │   │
│  │COM       │ │Données   │ │RPA/CBA   │ │Réactions │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
├─────────────────────────────────────────────────────────┤
│     data/         reports/         core/                │
│  rpa2024_tables  pdf_generator   database.py            │
│  (règlement)     docx_generator  (SQLite)               │
└─────────────────────────────────────────────────────────┘
```

### Principe MVC
- **Modèle** : `data/rpa2024_tables.py` (données réglementaires), `core/database.py` (projets)
- **Moteur** : `engines/` (calculs purs, indépendants de l'interface)
- **Vue** : `ui/` (PySide6, affichage et interaction)
- **Données ETABS** : `etabs/` (extraction et synchronisation)

Chaque moteur hérite de `BaseEngine` et implémente une méthode `calculate()` qui retourne un `Result(status, values, warnings)`.

---

## Moteurs de calcul

| Moteur | Classe | Description |
|---|---|---|
| Paramètres sismiques | `SeismicParamsEngine` | Calcule A, I, S, R, Qf, T1, T2, T3 à partir de la zone, site, usage, structure |
| Spectre | `SpectrumEngine` | Génère le spectre RPA 2024 sur 0.01–4s (4 zones) |
| Effort tranchant | `BaseShearEngine` | V = λ × Sad/g(T) × W, vérification V_min |
| Distribution forces | `ForceDistributionEngine` | Fi = V × (Wi × Hi) / Σ(Wj × Hj) |
| Déplacements | `DisplacementEngine` | Vérification Δk/hk ≤ 1.5% (selon matériau) |
| P-Delta | `PDeltaEngine` | θk = Pk × Δk / (Vk × hk) |
| Renversement | `OverturningEngine` | Mr = Σ(Fi × Hi) vs Ms = W × B/2 |
| Fondations | `FoundationEngine` | Semelles isolées, filantes, radier nervuré |
| Voiles & linteaux | `WallEngine` | Compression, cisaillement, ferraillage |
| Diaphragme | `VerificationDiaphragmeRPA` | Article 5.6 — Fpx, Vd, Nd, Nc, Md |
| Projet complet | `ProjectEngine` | Orchestre les 7 étapes RPA 2024 |

---

## Intégration ETABS

### Connexion COM
```python
from etabs.com_connector import COMConnector
conn = COMConnector()
ok, msg = conn.connecter()  # Attache à ETABS en cours d'exécution
```

### Import des données
```python
from etabs.data_importer import ETABSDataImporter
imp = ETABSDataImporter(conn.SapModel)
data = imp.importer_tout(cas_sismique_x='Ex_static',
                          cas_sismique_y='Ey_static',
                          cas_gravite='Dead')
```

Le module d'import extrait automatiquement :
- Périodes et participation modales
- Efforts tranchants par étage (Vx, Vy)
- Déplacements par étage
- Réactions globales et par joint
- Efforts dans les voiles (Section Cut / Pier Forces)
- Masses et poids par étage

### Générateur de combinaisons
```python
from etabs.combinaisons import RPAComboGenerator
gen = RPAComboGenerator(conn.SapModel,
                         cas_x='Ex_static', cas_y='Ey_static',
                         cas_g='Dead', cas_q='Live')
crees, ignores = gen.generer(psi=0.20)  # ψ selon usage
```

L'interface graphique (onglet ETABS) propose :
- Détection automatique des cas de charge
- Paramètres sismiques (zone, site, usage)
- Facteur de qualité Qf selon catégorie
- Génération des combinaisons ELU RPA 2024
- Analyse critique poteaux (Nmax/Nmin/M3max/M2max)
- Analyse critique poutres (M3+/M3−/V2max)

---

## Structure du projet

```
CivilCalc_RPA2024/
├── main.py                       # Lanceur interface graphique (PySide6)
├── Civil_Calc_RPA2024.py         # Lanceur ligne de commande (tests)
├── requirements.txt              # Dépendances Python
├── .gitignore
├── README.md
│
├── core/
│   ├── __init__.py
│   └── database.py               # Gestion base SQLite (projets)
│
├── data/
│   ├── __init__.py
│   ├── rpa2024_tables.py         # Tables réglementaires RPA 2024
│   └── projets.db                # Base de données SQLite
│
├── engines/                      # Moteurs de calcul (indépendants GUI)
│   ├── __init__.py
│   ├── base_engine.py            # Classe de base (BaseEngine, Result, Status)
│   ├── base_shear.py             # Effort tranchant à la base
│   ├── displacement.py           # Déplacements inter-étages
│   ├── force_distribution.py     # Distribution des forces latérales
│   ├── foundations.py            # Fondations (semelles, radier)
│   ├── justification_planchers.py # Justification des planchers (Art 5.6)
│   ├── overturning.py            # Renversement
│   ├── pdelta.py                 # Effet P-Delta
│   ├── project_engine.py         # Moteur projet complet (7 étapes)
│   ├── rpa_verif.py              # Agrégation vérifications RPA
│   ├── seismic_params.py         # Paramètres sismiques
│   ├── spectrum.py               # Spectre de réponse
│   ├── verification_diaphragme_rpa.py # Vérification diaphragme
│   └── walls.py                  # Voiles et linteaux
│
├── etabs/                        # Intégration ETABS
│   ├── __init__.py
│   ├── com_connector.py          # Connexion COM ETABS
│   ├── combinaisons.py           # Générateur combinaisons RPA/CBA
│   ├── data_importer.py          # Import données ETABS
│   ├── diagnostic.py             # Diagnostic structurel
│   ├── diaphragme_checker.py     # Vérification diaphragme (COM)
│   ├── file_importer.py          # Import CSV/Excel
│   ├── noyau_checker.py          # Vérification noyau (COM)
│   └── reactions_extractor.py    # Extraction réactions par joint
│
├── reports/
│   ├── __init__.py
│   ├── pdf_generator.py          # Génération rapport PDF
│   └── docx_generator.py         # Génération rapport Word
│
├── ui/                           # Interface utilisateur PySide6
│   ├── __init__.py
│   ├── main_window.py            # Fenêtre principale
│   ├── styles.py                 # Thème sombre (QSS)
│   ├── tabs/
│   │   ├── __init__.py
│   │   ├── tab_projet.py         # Projet (dimensions, matériaux)
│   │   ├── tab_spectre.py        # Spectre de réponse
│   │   ├── tab_rpa.py            # Vérifications RPA 2024
│   │   ├── tab_etabs.py          # Intégration ETABS
│   │   ├── tab_diaphragme.py     # Vérification diaphragme
│   │   ├── tab_justification_planchers.py # Planchers Art 5.6
│   │   ├── tab_noyau.py          # Vérification noyau
│   │   ├── tab_fondations.py     # Dimensionnement fondations
│   │   ├── tab_voiles.py         # Voiles et linteaux
│   │   └── tab_rapport.py        # Génération de rapports
│   └── widgets/
│       ├── __init__.py
│       ├── result_table.py       # Tableau de résultats stylé
│       └── chart_widget.py       # Graphique matplotlib
│
├── tests/
│   ├── __init__.py
│   └── test_moteurs.py           # Tests unitaires des moteurs
│
└── Resultats_Art56/
    ├── RPA2024_Art56_Diaphragmes.json
    ├── RPA2024_Art56_Diaphragmes.txt
    └── RPA2024_Art56_Diaphragmes.xlsx
```

---

## Tests

```bash
python tests\test_moteurs.py
```

La suite de tests couvre les 10 moteurs avec un jeu de données commun (bâtiment R+5) :

| # | Test | Vérification |
|---|---|---|
| 1 | Spectre | Génération du spectre RPA 2024, valeurs Sa aux points clés |
| 2 | Effort tranchant | V = λ·Sad·W, V_min, comparaison T_ETABS vs T_emp |
| 3 | Distribution | ΣFi = V, répartition proportionnelle Wihi |
| 4 | Déplacements | Δk/hk ≤ 1.5%, déplacements inélastiques dr = R·de |
| 5 | P-Delta | θk = Pk·Δk/Vk·hk, classification |
| 6 | Renversement | Mr = Σ(Fi·Hi), Ms = W·B/2, ratio ≥ 1.0 |
| 7 | Fondations | Semelle isolée, filante, radier |
| 8 | Voiles & linteaux | Compression, cisaillement, ferraillage |
| 9 | Paramètres sismiques | A, I, R, S, T1, T2, T3 |
| 10 | Projet complet | Pipeline complet 7 étapes |

---

## Dépendances

| Paquet | Version | Rôle |
|---|---|---|
| PySide6 | ≥ 6.6.0 | Interface graphique Qt |
| numpy | ≥ 1.21 | Calculs numériques, vecteurs |
| pandas | ≥ 1.3.0 | Import CSV/Excel |
| comtypes | ≥ 1.1.0 | Connexion COM ETABS |
| openpyxl | ≥ 3.0.0 | Export/import Excel |
| reportlab | ≥ 4.0.0 | Génération rapports PDF |
| python-docx | ≥ 0.8.11 | Génération rapports Word |
| rich | ≥ 13.0.0 | Sortie console formatée |

---

## Références

- **RPA 2024** — Règlement Parasismique Algérien, DTR BC 2.48
- **CBA 93** — Règlement des Charges et Surcharges
- **ETABS** — Integrated Building Design Software (CSI)
- **DTR BC 2.48** — Document Technique Réglementaire "Règlement Parasismique Algérien"

---

## Licence

Projet interne — Utilisation réservée au cadre professionnel du génie civil et du calcul parasismique.

---

*Documentation générée le 11 juillet 2026.*
