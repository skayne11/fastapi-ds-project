# 🚀 Guide de Démarrage Rapide

Ce guide vous permet de démarrer l'API en **moins de 5 minutes** !

---

## Option 1 : Docker (Recommandé) ⚡

### Prérequis
- Docker et Docker Compose installés

### Étapes

```bash
# 1. Lancer l'API
docker-compose up --build

# 2. Accéder à la documentation interactive
# Ouvrez votre navigateur : http://localhost:8000/docs
```

**C'est tout ! ✅** L'API est maintenant accessible.

---

## Option 2 : Sans Docker 🐍

### Prérequis
- Python 3.9 ou supérieur

### Étapes

```bash
# 1. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate  # Windows

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. Accéder à la documentation
# http://localhost:8000/docs
```

---

## 🎯 Premier Test

### Via l'interface Swagger (http://localhost:8000/docs)

1. **Générer un dataset**
   - Cliquez sur `POST /dataset/generate`
   - Cliquez sur "Try it out"
   - Utilisez ce JSON :
   ```json
   {
     "phase": "clean",
     "seed": 42,
     "n": 1000
   }
   ```
   - Cliquez "Execute"
   - **Copiez le `dataset_id`** dans la réponse

2. **Obtenir un rapport qualité**
   - Cliquez sur `GET /clean/report/{dataset_id}`
   - Collez votre `dataset_id`
   - Cliquez "Execute"
   - Vous verrez les défauts dans vos données !

### Via Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Générer un dataset
response = requests.post(
    f"{BASE_URL}/dataset/generate",
    json={"phase": "clean", "seed": 42, "n": 1000}
)
data = response.json()
dataset_id = data["meta"]["dataset_id"]
print(f"Dataset créé : {dataset_id}")

# Obtenir un rapport
response = requests.get(f"{BASE_URL}/clean/report/{dataset_id}")
report = response.json()["report"]
print(f"Doublons : {report['duplicates']}")
print(f"Missing values : {report['missing_values']}")
```

### Via cURL

```bash
# Générer dataset
curl -X POST "http://localhost:8000/dataset/generate" \
  -H "Content-Type: application/json" \
  -d '{"phase":"clean","seed":42,"n":1000}'

# Obtenir rapport (remplacez DATASET_ID)
curl "http://localhost:8000/clean/report/clean_42_1000"
```

---

## 📚 Prochaines Étapes

1. **Explorez les notebooks** : `jupyter notebook` dans le dossier `notebooks/`
2. **Testez les 5 phases** :
   - TP1 - Clean : `/clean/*`
   - TP2 - EDA : `/eda/*`
   - TP3 - MV : `/mv/*`
   - TP4 - ML : `/ml/*`
   - TP5 - ML2 : `/ml2/*`

3. **Documentation complète** : Consultez le [README.md](README.md)

---

## 🆘 Problèmes Courants

### Port 8000 déjà utilisé
```bash
# Arrêter le service existant ou changer de port
uvicorn app.main:app --port 8001
```

### Erreur d'import
```bash
# Vérifier que vous êtes dans le bon dossier
cd fastapi-ds-project

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Docker ne démarre pas
```bash
# Nettoyer et reconstruire
docker-compose down
docker-compose up --build
```

---

## ✅ Validation

Pour vérifier que tout fonctionne :

```bash
# Test health check
curl http://localhost:8000/health

# Doit retourner : {"status":"healthy","service":"fastapi-ds-api"}
```

---

**Bon développement ! 🎉**
