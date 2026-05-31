# Mini-Projet SIG — Tableau de Bord Climatique Marrakech-Safi

Application Streamlit de visualisation climatique interactive pour la région Marrakech-Safi, Maroc.

## Fonctionnalités

- **Carte interactive** avec fond OpenStreetMap + calque MNT (OpenTopoMap)
- **Navigation hiérarchique** : Province → Commune
- **Données climatiques** via **Open-Meteo API** (prévisions 16 jours)
- **Moyenne spatiale** calculée sur une grille de points à l'intérieur du polygone
- **Graphiques** : T2m en courbe, Précipitation en barres
- **Sources multiples** : architecture extensible (Open-Meteo actif, ECMWF/Copernicus/NASA POWER en démonstration)

## Stack Technique

| Composant | Technologie |
|-----------|------------|
| Framework | Python 3.13 + Streamlit 1.58.0 |
| Données vectorielles | GeoPandas 1.1.3 / Shapefiles |
| Carte | Folium 0.20.0 + OpenTopoMap XYZ |
| Graphiques | Plotly 6.7.0 |
| API Climat | Open-Meteo (gratuit, sans clé) |

## Structure du Projet

```
mini-projet-gis/
├── app.py                  # Orchestrateur Streamlit
├── data_loader.py          # Chargement shapefiles + helpers géométriques
├── climate_api.py          # Client Open-Meteo + sources climatiques
├── map_utils.py            # Construction carte Folium
├── requirements.txt        # Dépendances
├── data/                   # Shapefiles (3 niveaux : Régions, Provinces, Communes)
│   ├── Regions_WGS84.*
│   ├── Provinces_WGS84.*
│   └── communes_WGS84.*
├── README.md
└── PROJECT_MAP.md
```

## Installation

```bash
git clone <https://github.com/Oussama134-debug/MiniProject_GeospatialWebApplication>
cd mini-projet-gis
pip install -r requirements.txt
streamlit run app.py
```

## Déploiement

Déployé sur Streamlit Cloud : [URL à compléter]

## Auteur

Projet réalisé dans le cadre du module SIG — Systèmes d'Information Géographique.
