# 🏗️ Architecture du Projet

Ce document explique l'architecture et les principes de conception du projet.

---

## 📐 Vue d'ensemble

Le projet suit une **architecture en couches** classique pour les APIs REST :

```
┌─────────────────────────────────────────────┐
│           Clients (HTTP Requests)           │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│        Routers (FastAPI Endpoints)          │
│   - Validation des requêtes (Pydantic)     │
│   - Gestion des erreurs HTTP                │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          Services (Logique Métier)          │
│   - Algorithmes data science                │
│   - Transformations                         │
│   - ML pipelines                            │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│      Stockage (In-Memory Dictionaries)      │
│   - Datasets                                │
│   - Cleaners                                │
│   - Modèles ML                              │
└─────────────────────────────────────────────┘
```

---

## 📂 Structure des Dossiers

```
fastapi-ds-project/
│
├── app/                          # Code source de l'application
│   ├── main.py                   # Point d'entrée FastAPI
│   │
│   ├── routers/                  # Couche de routage (endpoints)
│   │   ├── dataset.py            # Génération datasets
│   │   ├── clean.py              # TP1 - Clean
│   │   ├── eda.py                # TP2 - EDA
│   │   ├── mv.py                 # TP3 - Multivarié
│   │   ├── ml.py                 # TP4 - ML
│   │   └── ml2.py                # TP5 - ML2
│   │
│   ├── services/                 # Couche de logique métier
│   │   ├── dataset_generator.py  # Génération de datasets
│   │   ├── cleaning_service.py   # Nettoyage de données
│   │   ├── eda_service.py        # Analyse exploratoire
│   │   ├── mv_service.py         # PCA, Clustering
│   │   ├── ml_service.py         # ML baseline
│   │   └── ml2_service.py        # ML avancé
│   │
│   └── schemas/                  # Modèles Pydantic
│       └── common.py             # Schémas partagés
│
├── notebooks/                    # Notebooks de démonstration
│   ├── demo_tp1_clean.ipynb
│   ├── demo_tp2_eda.ipynb
│   ├── demo_tp3_mv.ipynb
│   ├── demo_tp4_ml.ipynb
│   └── demo_tp5_ml2.ipynb
│
├── tests/                        # Tests unitaires
│   └── test_api.py
│
├── models/                       # Stockage modèles (vide au départ)
├── data/                         # Données (vide au départ)
│
├── Dockerfile                    # Image Docker
├── docker-compose.yml            # Orchestration
├── requirements.txt              # Dépendances Python
└── README.md                     # Documentation principale
```

---

## 🎯 Principes de Conception

### 1. Séparation des Responsabilités

**Routers** (couche présentation)
- Gèrent les requêtes/réponses HTTP
- Validation des entrées avec Pydantic
- Gestion des erreurs (try/catch → HTTPException)
- **NE CONTIENNENT PAS** de logique métier

**Services** (couche métier)
- Contiennent toute la logique data science
- Indépendants de FastAPI (peuvent être réutilisés ailleurs)
- Retournent des structures Python natives (dict, DataFrame)

**Schemas** (modèles de données)
- Validation automatique avec Pydantic
- Documentation automatique dans Swagger
- Type safety

### 2. Contrat API Standardisé

Toutes les requêtes/réponses suivent la même structure :

**Request** :
```json
{
  "meta": {
    "dataset_id": "...",
    "schema_version": "1.0"
  },
  "data": [...],      // Optionnel
  "params": {...}     // Optionnel
}
```

**Response** :
```json
{
  "meta": {
    "dataset_id": "...",
    "schema_version": "1.0"
  },
  "result": {...},    // Résultat principal
  "report": {...},    // Statistiques/métriques
  "artifacts": {...}  // Graphiques, modèles, etc.
}
```

### 3. Reproductibilité

- **Datasets** : Même `seed` → Même dataset
- **Identifiants** : `dataset_id = f"{phase}_{seed}_{n}"`
- **Stockage en mémoire** : Permet de réutiliser les datasets entre endpoints

### 4. Sans Base de Données

- **Stockage** : Dictionnaires Python en mémoire
- **Avantages** :
  - Simplicité (pas de setup DB)
  - Rapidité de développement
  - Idéal pour prototypage/démonstration
- **Limitations** :
  - Données perdues au redémarrage
  - Non adapté pour production à grande échelle

---

## 🔄 Flux de Données Typique

### Exemple : TP1 - Clean

```
1. Client envoie POST /dataset/generate
   ↓
2. Router dataset.py valide la requête
   ↓
3. Service DatasetGenerator.generate()
   - Génère un DataFrame avec défauts
   - Stocke dans _datasets dict
   ↓
4. Router retourne dataset_id + échantillon
   ↓
5. Client envoie POST /clean/fit avec dataset_id
   ↓
6. Router clean.py récupère le dataset
   ↓
7. Service CleaningService.fit()
   - Analyse les données
   - Apprend les règles de nettoyage
   - Retourne cleaner_id + règles
   ↓
8. Client envoie POST /clean/transform
   ↓
9. Service CleaningService.transform()
   - Applique les règles
   - Retourne données nettoyées + rapport
```

---

## 🧩 Modules Clés

### dataset_generator.py

**Responsabilité** : Générer des datasets reproductibles

**Fonctions principales** :
- `generate(phase, seed, n)` → Génère un dataset
- `get_dataset(dataset_id)` → Récupère un dataset existant

**Stockage** :
```python
_datasets: Dict[str, pd.DataFrame] = {}
```

### cleaning_service.py (TP1)

**Responsabilité** : Nettoyage de données

**Fonctions principales** :
- `generate_report(df)` → Analyse qualité
- `fit(df, params)` → Apprend pipeline de nettoyage
- `transform(df, cleaner_data)` → Applique le nettoyage

**Traite** :
- Missing values (imputation)
- Doublons (suppression)
- Outliers (clip ou remove)
- Types cassés (conversion)
- Variables catégorielles (encoding)

### eda_service.py (TP2)

**Responsabilité** : Analyse exploratoire

**Fonctions principales** :
- `summary(df)` → Statistiques descriptives
- `groupby(df, by, metrics)` → Agrégations
- `correlation(df)` → Matrice de corrélation
- `plots(df)` → Graphiques Plotly (JSON)

### mv_service.py (TP3)

**Responsabilité** : Analyse multivariée

**Fonctions principales** :
- `pca_fit_transform(df, n_components, scale)` → PCA avec loadings
- `cluster_kmeans(df, k, scale)` → Clustering K-Means
- `generate_report(df)` → Rapport interprétatif

### ml_service.py (TP4)

**Responsabilité** : ML baseline

**Fonctions principales** :
- `train(df, model_type)` → Entraîne LogReg ou RF
- `predict(model_data, X)` → Prédictions
- `get_model_info(model_data)` → Infos modèle

**Stockage** :
```python
_models: Dict[str, Dict[str, Any]] = {}
```

### ml2_service.py (TP5)

**Responsabilité** : ML avancé

**Fonctions principales** :
- `tune_model(df, model_type, search, cv)` → Hyperparameter tuning
- `feature_importance(model_data)` → Importance native
- `permutation_importance_analysis()` → Importance par permutation
- `explain_instance(model_data, instance)` → Explication locale

---

## 🔐 Validation et Gestion d'Erreurs

### Validation des Entrées

Toutes les entrées sont validées par **Pydantic** :

```python
class DatasetGenerateRequest(BaseModel):
    phase: str
    seed: int
    n: int = Field(..., gt=0)  # n doit être > 0
```

Si validation échoue → **422 Unprocessable Entity**

### Gestion d'Erreurs

Pattern utilisé dans tous les routers :

```python
try:
    # Logique métier
    result = service.do_something()
    return StandardResponse(...)
except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
```

Codes HTTP utilisés :
- **200** : Succès
- **400** : Erreur client (paramètres invalides)
- **404** : Ressource introuvable (dataset_id, model_id)
- **422** : Validation Pydantic échouée

---

## 🚀 Extensibilité

### Ajouter une Nouvelle Phase

1. **Créer un service** dans `app/services/`
2. **Créer un router** dans `app/routers/`
3. **Enregistrer le router** dans `app/main.py` :
   ```python
   app.include_router(new_phase.router, prefix="/new", tags=["New Phase"])
   ```
4. **Créer un notebook** de démonstration

### Ajouter un Nouveau Modèle ML

Dans `ml_service.py` ou `ml2_service.py`, ajouter :

```python
elif model_type == "xgboost":
    from xgboost import XGBClassifier
    model = XGBClassifier(random_state=42)
```

### Passer à une Base de Données

1. Ajouter SQLAlchemy dans `requirements.txt`
2. Créer `app/database.py` avec configuration DB
3. Créer des modèles ORM dans `app/models/`
4. Remplacer les dictionnaires en mémoire par des requêtes DB

---

## 📊 Performance et Scalabilité

### État Actuel (In-Memory)

**Avantages** :
- ✅ Rapide (pas d'I/O disque)
- ✅ Simple (pas de setup DB)
- ✅ Idéal pour développement/démonstration

**Limitations** :
- ❌ Données perdues au redémarrage
- ❌ Limité par la RAM
- ❌ Pas de persistance
- ❌ Une seule instance (pas de scaling horizontal)

### Améliorations Possibles

1. **Persistance** : PostgreSQL + SQLAlchemy
2. **Cache** : Redis pour datasets fréquents
3. **Files d'attente** : Celery pour long-running tasks (tuning)
4. **Object Storage** : S3/MinIO pour modèles et datasets
5. **Monitoring** : Prometheus + Grafana

---

## 🧪 Tests

### Tests Unitaires

Fichier : `tests/test_api.py`

**Coverage actuelle** :
- ✅ Endpoints de base (/, /health)
- ✅ Génération de datasets
- ✅ Pipeline de nettoyage (fit + transform)
- ✅ Gestion d'erreurs

**Lancer les tests** :
```bash
pytest tests/
```

---

## 🐳 Docker

### Image Docker

`Dockerfile` crée une image Python minimale avec :
- Python 3.11-slim
- Dependencies de requirements.txt
- Code de l'application

### Docker Compose

`docker-compose.yml` lance 2 services :
1. **api** : L'API FastAPI (port 8000)
2. **jupyter** : Serveur Jupyter (port 8888)

**Volumes montés** :
- Code synchronisé en temps réel (développement)
- Modèles et données persistants

---

## 📚 Ressources

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [Scikit-learn](https://scikit-learn.org/)
- [Plotly](https://plotly.com/python/)

---

**Maintenu par** : Ayedesso  
**Dernière mise à jour** : 10 février 2026
