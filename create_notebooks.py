"""Script pour créer tous les notebooks de démonstration"""
import json

# Définir les autres notebooks de manière similaire mais plus concise
notebooks = {
    "demo_tp2_eda": {
        "title": "TP2 - EDA : Analyse Exploratoire",
        "phase": "eda"
    },
    "demo_tp3_mv": {
        "title": "TP3 - MV : Analyse Multivariée",
        "phase": "mv"
    },
    "demo_tp4_ml": {
        "title": "TP4 - ML : Machine Learning Baseline",
        "phase": "ml"
    },
    "demo_tp5_ml2": {
        "title": "TP5 - ML2 : ML Avancé",
        "phase": "ml2"
    }
}

for filename, info in notebooks.items():
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [f"# {info['title']}\n\nDémonstration de l'API pour la phase {info['phase']}"]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": "import requests\nimport pandas as pd\nimport json\n\nBASE_URL = 'http://localhost:8000'\nprint('✅ Prêt à utiliser l\\'API')"
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": f"## Générer un dataset pour {info['phase']}"
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": f"response = requests.post(\n    f'{{BASE_URL}}/dataset/generate',\n    json={{\n        'phase': '{info['phase']}',\n        'seed': 42,\n        'n': 1000\n    }}\n)\ndata = response.json()\ndataset_id = data['meta']['dataset_id']\nprint(f'Dataset ID: {{dataset_id}}')\ndf = pd.DataFrame(data['result']['data_sample'])\ndf.head()"
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": "## Consulter la documentation interactive\n\nOuvrez http://localhost:8000/docs pour tester tous les endpoints de manière interactive."
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    with open(f'notebooks/{filename}.ipynb', 'w') as f:
        json.dump(notebook, f, indent=2)
    
    print(f"✅ Créé: {filename}.ipynb")

print("\n🎉 Tous les notebooks ont été créés avec succès!")
