# FastAPI Data Science - Projet Fil Rouge

🎓 **Projet pédagogique** : API FastAPI pour un parcours complet Data Scientist en 5 phases

---

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Les 5 Phases du Projet](#les-5-phases-du-projet)
- [Endpoints](#endpoints)
- [Tests](#tests)
- [Structure du Projet](#structure-du-projet)

---

## 🎯 Vue d'ensemble

Ce projet implémente une API complète couvrant l'ensemble du cycle de vie d'un projet Data Science :

1. **TP1 - Clean** : Nettoyage et préparation des données
2. **TP2 - EDA** : Analyse exploratoire et visualisations
3. **TP3 - MV** : Analyse multivariée (PCA, Clustering)
4. **TP4 - ML** : Machine Learning baseline
5. **TP5 - ML2** : ML avancé (tuning, explicabilité)

### ✨ Caractéristiques

- ✅ Génération automatique de datasets reproductibles
- ✅ API RESTful complète avec FastAPI
- ✅ Validation des données avec Pydantic
- ✅ Documentation interactive Swagger (/docs)
- ✅ Architecture modulaire (routers/services/schemas)
- ✅ Dockerisé pour un déploiement facile
- ✅ Sans base de données (stockage en mémoire)
- ✅ Notebooks Jupyter pour démonstration

---

## 🏗️ Architecture

```
fastapi-ds-project/
├── app/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── routers/             # Endpoints par phase
│   │   ├── dataset.py       # Génération datasets
│   │   ├── clean.py         # TP1 - Nettoyage
│   │   ├── eda.py           # TP2 - EDA
│   │   ├── mv.py            # TP3 - Multivarié
│   │   ├── ml.py            # TP4 - ML Baseline
│   │   └── ml2.py           # TP5 - ML Avancé
│   ├── services/            # Logique métier
│   │   ├── dataset_generator.py
│   │   ├── cleaning_service.py
│   │   ├── eda_service.py
│   │   ├── mv_service.py
│   │   ├── ml_service.py
│   │   └── ml2_service.py
│   ├── schemas/             # Modèles Pydantic
│   │   └── common.py
│   └── models/              # Stockage modèles
├── notebooks/
│   ├── demo_tp1_clean.ipynb
│   ├── demo_tp2_eda.ipynb
│   ├── demo_tp3_mv.ipynb
│   ├── demo_tp4_ml.ipynb
│   └── demo_tp5_ml2.ipynb
├── tests/                   # Tests unitaires
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### Principes architecturaux

1. **Séparation des responsabilités** : 
   - Routers → gèrent les requêtes HTTP
   - Services → contiennent la logique métier
   - Schemas → validation des données

2. **Contrat API standardisé** :
   - Request : `{meta, data, params}`
   - Response : `{meta, result, report, artifacts}`

3. **Reproductibilité** : même `seed` → même dataset

---

## 🚀 Installation

### Prérequis

- Docker et Docker Compose
- Ou Python 3.9+

### Option 1 : Avec Docker (recommandé)

```bash
# 1. Cloner le projet
git clone <votre-repo>
cd fastapi-ds-project

# 2. Lancer avec Docker Compose
docker-compose up --build

# L'API sera accessible sur http://localhost:8000
# Documentation : http://localhost:8000/docs
```

### Option 2 : Sans Docker

```bash
# 1. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3 : Avec Jupyter (pour les notebooks)

```bash
# Installer Jupyter
pip install jupyter

# Lancer Jupyter
jupyter notebook

# Ouvrir les notebooks dans notebooks/
```

---

## 📖 Utilisation

### 1. Accéder à la documentation interactive

Ouvrez votre navigateur : **http://localhost:8000/docs**

Vous verrez l'interface Swagger avec tous les endpoints testables.

### 2. Workflow typique

#### Étape 1 : Générer un dataset

```bash
curl -X POST "http://localhost:8000/dataset/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "phase": "clean",
    "seed": 42,
    "n": 1000
  }'
```

Réponse :
```json
{
  "meta": {
    "dataset_id": "clean_42_1000",
    "schema_version": "1.0"
  },
  "result": {
    "columns": ["x1", "x2", "x3", "segment", "target"],
    "data_sample": [...]
  }
}
```

#### Étape 2 : Utiliser le dataset_id dans les endpoints de phase

Exemple pour TP1 (Clean) :
```bash
curl -X POST "http://localhost:8000/clean/fit" \
  -H "Content-Type: application/json" \
  -d '{
    "meta": {
      "dataset_id": "clean_42_1000"
    },
    "params": {
      "impute_strategy": "mean",
      "outlier_strategy": "clip",
      "categorical_strategy": "one_hot"
    }
  }'
```

---

## 🎓 Les 5 Phases du Projet

### TP1 - Clean : Nettoyage des Données

**Objectif** : Transformer des données sales en données propres

**Défauts traités** :
- ❌ Valeurs manquantes (10-20%)
- ❌ Doublons (1-5%)
- ❌ Outliers (1-3%)
- ❌ Types incohérents

**Endpoints** :
- `POST /dataset/generate` - Générer dataset avec défauts
- `POST /clean/fit` - Apprendre pipeline de nettoyage
- `POST /clean/transform` - Appliquer le nettoyage
- `GET /clean/report/{dataset_id}` - Rapport qualité

---

### TP2 - EDA : Analyse Exploratoire

**Objectif** : Produire statistiques et graphiques sans notebook

**Fonctionnalités** :
- 📊 Statistiques descriptives
- 📈 Graphiques interactifs (Plotly)
- 🔗 Corrélations
- 📦 Agrégations par groupe

**Endpoints** :
- `POST /eda/summary` - Stats par variable
- `POST /eda/groupby` - Agrégations
- `POST /eda/correlation` - Matrice de corrélation
- `POST /eda/plots` - Générer graphiques

---

### TP3 - MV : Analyse Multivariée

**Objectif** : PCA et Clustering avec résultats interprétables

**Méthodes** :
- 🎯 PCA (réduction dimensionnelle)
- 🔍 K-Means clustering
- 📊 Loadings et explained variance

**Endpoints** :
- `POST /mv/pca/fit_transform` - PCA avec projections
- `POST /mv/cluster/kmeans` - Clustering K-Means
- `GET /mv/report/{dataset_id}` - Rapport interprétatif

---

### TP4 - ML : Machine Learning Baseline

**Objectif** : Entraîner, évaluer, prédire avec modèles supervisés

**Modèles** :
- 📉 Logistic Regression
- 🌲 Random Forest

**Endpoints** :
- `POST /ml/train` - Entraîner un modèle
- `GET /ml/metrics/{model_id}` - Métriques de performance
- `POST /ml/predict` - Faire des prédictions
- `GET /ml/model-info/{model_id}` - Infos du modèle

---

### TP5 - ML2 : ML Avancé

**Objectif** : Optimisation et explicabilité

**Fonctionnalités** :
- 🎯 Hyperparameter tuning (Grid/Random Search)
- 📊 Feature importance
- 🔍 Permutation importance
- 💡 Explications locales

**Endpoints** :
- `POST /ml2/tune` - Tuning avec CV
- `GET /ml2/feature-importance/{model_id}` - Importance des features
- `POST /ml2/permutation-importance` - Importance par permutation
- `POST /ml2/explain-instance` - Explication locale

---

## 🔌 Endpoints

### Génération de Datasets

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/dataset/generate` | Génère un dataset pour une phase donnée |

### TP1 - Clean

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/clean/fit` | Apprend un pipeline de nettoyage |
| POST | `/clean/transform` | Applique le nettoyage |
| GET | `/clean/report/{dataset_id}` | Rapport qualité |

### TP2 - EDA

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/eda/summary` | Statistiques descriptives |
| POST | `/eda/groupby` | Agrégations par groupe |
| POST | `/eda/correlation` | Matrice de corrélation |
| POST | `/eda/plots` | Génère graphiques |

### TP3 - MV

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/mv/pca/fit_transform` | PCA avec projections |
| POST | `/mv/cluster/kmeans` | Clustering K-Means |
| GET | `/mv/report/{dataset_id}` | Rapport interprétatif |

### TP4 - ML

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/ml/train` | Entraîne un modèle |
| GET | `/ml/metrics/{model_id}` | Métriques |
| POST | `/ml/predict` | Prédictions |
| GET | `/ml/model-info/{model_id}` | Infos modèle |

### TP5 - ML2

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/ml2/tune` | Tuning avec CV |
| GET | `/ml2/feature-importance/{model_id}` | Feature importance |
| POST | `/ml2/permutation-importance` | Permutation importance |
| POST | `/ml2/explain-instance` | Explication locale |

---

## 🧪 Tests

```bash
# Lancer les tests
pytest tests/

# Avec couverture
pytest --cov=app tests/
```

---

## 📊 Exemples de Notebooks

Les notebooks dans `notebooks/` démontrent l'utilisation complète de l'API pour chaque TP :

1. **demo_tp1_clean.ipynb** : Nettoyage de données
2. **demo_tp2_eda.ipynb** : Analyse exploratoire
3. **demo_tp3_mv.ipynb** : PCA et Clustering
4. **demo_tp4_ml.ipynb** : Machine Learning baseline
5. **demo_tp5_ml2.ipynb** : ML avancé avec tuning

---

## 🛠️ Technologies Utilisées

- **FastAPI** : Framework web moderne et rapide
- **Pydantic** : Validation de données
- **Pandas** : Manipulation de données
- **NumPy** : Calculs numériques
- **Scikit-learn** : Machine Learning
- **Plotly** : Visualisations interactives
- **Docker** : Containerisation

---

## 📝 Licence

Projet pédagogique - Ayedesso - 2026

---

## 👥 Auteur

**Ayedesso**  
Projet fil rouge FastAPI - Parcours Data Scientist

---

## 🆘 Support

Pour toute question :
1. Consultez la documentation interactive : `/docs`
2. Vérifiez les notebooks de démonstration
3. Consultez les tests pour des exemples d'utilisation

---

**Bon développement ! 🚀**
