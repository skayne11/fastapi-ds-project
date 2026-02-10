# 📝 Commandes Utiles

Ce document regroupe toutes les commandes utiles pour travailler avec le projet.

---

## 🐳 Docker

### Démarrage

```bash
# Construire et lancer tous les services
docker-compose up --build

# Lancer en arrière-plan (detached)
docker-compose up -d

# Lancer uniquement l'API (sans Jupyter)
docker-compose up api

# Reconstruire sans cache
docker-compose build --no-cache
```

### Arrêt

```bash
# Arrêter les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

### Logs

```bash
# Voir tous les logs
docker-compose logs

# Suivre les logs en temps réel
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs api
docker-compose logs jupyter
```

### Entrer dans un conteneur

```bash
# Shell dans le conteneur API
docker-compose exec api bash

# Shell dans le conteneur Jupyter
docker-compose exec jupyter bash
```

---

## 🐍 Python (Sans Docker)

### Environnement Virtuel

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer (Linux/Mac)
source venv/bin/activate

# Activer (Windows)
venv\Scripts\activate

# Désactiver
deactivate
```

### Installation

```bash
# Installer toutes les dépendances
pip install -r requirements.txt

# Installer en mode développement
pip install -e .

# Mettre à jour pip
pip install --upgrade pip
```

### Lancer l'API

```bash
# Lancement standard
uvicorn app.main:app --reload

# Avec host et port spécifiques
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Sans auto-reload (production)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 🧪 Tests

### Pytest

```bash
# Lancer tous les tests
pytest

# Avec verbosité
pytest -v

# Tests spécifiques
pytest tests/test_api.py

# Avec couverture de code
pytest --cov=app tests/

# Générer rapport HTML de couverture
pytest --cov=app --cov-report=html tests/
# Ouvrir htmlcov/index.html
```

### Tests Manuels (cURL)

```bash
# Health check
curl http://localhost:8000/health

# Générer dataset
curl -X POST "http://localhost:8000/dataset/generate" \
  -H "Content-Type: application/json" \
  -d '{"phase":"clean","seed":42,"n":1000}'

# Rapport qualité
curl "http://localhost:8000/clean/report/clean_42_1000"

# Fit pipeline de nettoyage
curl -X POST "http://localhost:8000/clean/fit" \
  -H "Content-Type: application/json" \
  -d '{
    "meta": {"dataset_id": "clean_42_1000"},
    "params": {
      "impute_strategy": "mean",
      "outlier_strategy": "clip",
      "categorical_strategy": "one_hot"
    }
  }'
```

---

## 📓 Jupyter

### Lancement

```bash
# Avec Docker Compose (déjà configuré)
docker-compose up jupyter
# Accessible sur http://localhost:8888

# Sans Docker
jupyter notebook
# Accessible sur http://localhost:8888
```

### Commandes dans Jupyter

```bash
# Lister les notebooks
jupyter notebook list

# Arrêter tous les serveurs
jupyter notebook stop
```

---

## 🔍 Debugging

### Logs API en Direct

```bash
# Avec Docker
docker-compose logs -f api

# Sans Docker (dans le terminal où uvicorn tourne)
# Les logs s'affichent automatiquement
```

### Python REPL Interactif

```bash
# Lancer Python avec imports
python -i -c "
from app.services.dataset_generator import DatasetGenerator
from app.services.cleaning_service import CleaningService
import pandas as pd
"

# Dans le REPL :
# >>> dataset_id, df = DatasetGenerator.generate('clean', 42, 100)
# >>> df.head()
```

### IPython

```bash
# Installer IPython
pip install ipython

# Lancer
ipython

# Avec imports automatiques
ipython -i -c "
from app.services.dataset_generator import DatasetGenerator
import pandas as pd
"
```

---

## 📊 Analyse de Données

### Pandas

```bash
# Dans Python/IPython
python
>>> import pandas as pd
>>> from app.services.dataset_generator import DatasetGenerator
>>> dataset_id, df = DatasetGenerator.generate('clean', 42, 1000)
>>> df.info()
>>> df.describe()
>>> df.head()
```

---

## 🔧 Maintenance

### Nettoyage

```bash
# Supprimer les fichiers Python compilés
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Supprimer les fichiers Jupyter temporaires
find . -type d -name .ipynb_checkpoints -exec rm -rf {} +

# Nettoyer Docker
docker system prune -a
```

### Mise à Jour des Dépendances

```bash
# Lister les packages outdated
pip list --outdated

# Mettre à jour un package
pip install --upgrade <package>

# Regénérer requirements.txt (après mise à jour)
pip freeze > requirements.txt
```

---

## 📦 Export/Import

### Exporter un Dataset

```python
# Dans Python
from app.services.dataset_generator import DatasetGenerator
import pandas as pd

dataset_id, df = DatasetGenerator.generate('clean', 42, 1000)
df.to_csv('data/export.csv', index=False)
df.to_excel('data/export.xlsx', index=False)
```

### Exporter un Modèle

```python
# Dans Python
import joblib
from app.services.dataset_generator import get_model

model_data = get_model('model_logreg_...')
joblib.dump(model_data['model_object'], 'models/my_model.pkl')
```

---

## 🌐 API Requests (Python)

### Avec requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Générer dataset
response = requests.post(
    f"{BASE_URL}/dataset/generate",
    json={"phase": "clean", "seed": 42, "n": 1000}
)
data = response.json()
dataset_id = data["meta"]["dataset_id"]

# Obtenir rapport
response = requests.get(f"{BASE_URL}/clean/report/{dataset_id}")
report = response.json()
```

### Avec httpx (async)

```python
import asyncio
import httpx

async def test_api():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/dataset/generate",
            json={"phase": "clean", "seed": 42, "n": 1000}
        )
        print(response.json())

asyncio.run(test_api())
```

---

## 🚀 Déploiement

### Production avec Uvicorn

```bash
# Avec Gunicorn + Uvicorn workers
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Variables d'Environnement

```bash
# Créer un fichier .env
echo "API_VERSION=1.0.0" > .env
echo "DEBUG=false" >> .env

# Charger dans Python
from dotenv import load_dotenv
load_dotenv()
```

---

## 📚 Documentation

### Générer Documentation API

```bash
# Documentation interactive
# Déjà disponible sur http://localhost:8000/docs (Swagger)
# Et http://localhost:8000/redoc (ReDoc)
```

### Générer Documentation Code

```bash
# Installer Sphinx
pip install sphinx sphinx-rtd-theme

# Initialiser
sphinx-quickstart docs

# Générer HTML
cd docs
make html
```

---

## 💡 Astuces

### Lancer API + Jupyter en une commande

```bash
docker-compose up -d && \
  echo "API: http://localhost:8000/docs" && \
  echo "Jupyter: http://localhost:8888"
```

### Surveiller les changements de fichiers

```bash
# Installer watchdog
pip install watchdog

# Relancer tests automatiquement
pytest-watch
```

### Formater le code automatiquement

```bash
# Installer black et isort
pip install black isort

# Formater tout le code
black app/ tests/
isort app/ tests/
```

### Linter

```bash
# Installer flake8
pip install flake8

# Linter le code
flake8 app/ tests/
```

---

## 🆘 Troubleshooting

### Port déjà utilisé

```bash
# Trouver le processus utilisant le port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Tuer le processus
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

### Problèmes d'imports

```bash
# Vérifier que vous êtes dans le bon dossier
pwd

# Vérifier PYTHONPATH
echo $PYTHONPATH

# Ajouter le dossier courant au PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Espace disque Docker

```bash
# Voir l'espace utilisé
docker system df

# Nettoyer
docker system prune -a --volumes
```

---

**Dernière mise à jour** : 10 février 2026
