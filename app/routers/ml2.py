"""
Router pour Machine Learning Avancé (TP5 - ML2)
Endpoints : /ml2/tune, /ml2/feature-importance, /ml2/permutation-importance, /ml2/explain-instance
"""

from fastapi import APIRouter, HTTPException
from app.schemas.common import (
    Ml2TuneRequest, Ml2PermutationImportanceRequest, 
    Ml2ExplainInstanceRequest, StandardResponse, MetaData
)
from app.services.dataset_generator import DatasetGenerator, store_model, get_model
from app.services.ml2_service import Ml2Service

router = APIRouter()


@router.post("/tune", response_model=StandardResponse)
def ml2_tune(request: Ml2TuneRequest):
    """
    Optimise les hyperparamètres via Grid/Random Search avec CV
    
    **Paramètres** :
    - `model_type` : Type de modèle (logreg, rf)
    - `search` : Type de recherche (grid, random)
    - `cv` : Nombre de folds pour cross-validation (3 ou 5)
    
    **Retour** :
    - best_model_id
    - best_params
    - cv_results_summary (top 5 configs)
    
    **Exemple** :
    ```json
    {
        "meta": {
            "dataset_id": "ml_42_1000"
        },
        "params": {
            "model_type": "rf",
            "search": "grid",
            "cv": 5
        }
    }
    ```
    """
    try:
        # Récupérer le dataset
        df = DatasetGenerator.get_dataset(request.meta.dataset_id)
        
        # Extraire paramètres
        model_type = request.params.get("model_type", "logreg")
        search_type = request.params.get("search", "grid")
        cv = request.params.get("cv", 3)
        
        # Tuner le modèle
        best_model_id, model_data = Ml2Service.tune_model(df, model_type, search_type, cv)
        
        # Stocker le modèle
        store_model(best_model_id, model_data)
        
        # Préparer la réponse
        meta = MetaData(
            dataset_id=request.meta.dataset_id,
            schema_version="1.0"
        )
        
        result = {
            "best_model_id": best_model_id,
            "best_params": model_data["best_params"],
            "best_score": model_data["best_score"],
            "cv_folds": cv,
            "search_type": search_type
        }
        
        report = {
            "status": "tuning_completed",
            "top_configs": model_data["top_configs"]
        }
        
        return StandardResponse(
            meta=meta,
            result=result,
            report=report
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/feature-importance/{model_id}", response_model=StandardResponse)
def ml2_feature_importance(model_id: str):
    """
    Extrait l'importance des features
    
    **Paramètre** : model_id (dans l'URL)
    
    **Retour** :
    - Importance par feature
    - Top 10 features
    - Méthode utilisée (RF: native, LogReg: coefficients)
    
    **Exemple** : `GET /ml2/feature-importance/tuned_rf_20260210_143022`
    """
    try:
        # Récupérer le modèle
        model_data = get_model(model_id)
        
        # Extraire feature importance
        importance_result = Ml2Service.feature_importance(model_data)
        
        # Préparer la réponse
        meta = MetaData(
            dataset_id="N/A",
            schema_version="1.0"
        )
        
        return StandardResponse(
            meta=meta,
            result=importance_result,
            report={"status": "feature_importance_computed"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/permutation-importance", response_model=StandardResponse)
def ml2_permutation_importance(request: Ml2PermutationImportanceRequest):
    """
    Calcule permutation importance (modèle-agnostique)
    
    **Paramètres** :
    - `model_id` : ID du modèle
    - `n_repeats` : Nombre de répétitions
    
    **Retour** :
    - Importance par permutation (moyenne + écart-type)
    - Top 10 features
    
    **Exemple** :
    ```json
    {
        "meta": {
            "dataset_id": "ml_42_1000"
        },
        "params": {
            "model_id": "tuned_rf_20260210_143022",
            "n_repeats": 10
        }
    }
    ```
    """
    try:
        # Récupérer le dataset et le modèle
        df = DatasetGenerator.get_dataset(request.meta.dataset_id)
        model_id = request.params.get("model_id")
        n_repeats = request.params.get("n_repeats", 10)
        
        if not model_id:
            raise ValueError("model_id manquant dans params")
        
        model_data = get_model(model_id)
        
        # Vérifier que target existe
        if 'target' not in df.columns:
            raise ValueError("Colonne 'target' manquante")
        
        X = df.drop(columns=['target'])
        y = df['target']
        
        # Calculer permutation importance
        perm_result = Ml2Service.permutation_importance_analysis(
            model_data, X, y, n_repeats
        )
        
        # Préparer la réponse
        meta = MetaData(
            dataset_id=request.meta.dataset_id,
            schema_version="1.0"
        )
        
        return StandardResponse(
            meta=meta,
            result=perm_result,
            report={"status": "permutation_importance_computed"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/explain-instance", response_model=StandardResponse)
def ml2_explain_instance(request: Ml2ExplainInstanceRequest):
    """
    Explication locale d'une prédiction
    
    **Paramètres** :
    - `model_id` : ID du modèle
    - `data` : Une seule ligne de features
    
    **Retour** :
    - Prédiction
    - Probabilité
    - Contributions par feature
    - Top 5 facteurs positifs/négatifs
    
    **Exemple** :
    ```json
    {
        "meta": {
            "dataset_id": "ml_42_1000"
        },
        "data": [
            {"x1": 100, "x2": 50, "x3": 30, "x4": 20, "x5": 15, "x6": 10, "segment": "A"}
        ],
        "params": {
            "model_id": "tuned_logreg_20260210_143022"
        }
    }
    ```
    """
    try:
        # Extraire paramètres
        model_id = request.params.get("model_id")
        
        if not model_id:
            raise ValueError("model_id manquant dans params")
        
        # Récupérer le modèle
        model_data = get_model(model_id)
        
        # Convertir data en DataFrame
        import pandas as pd
        instance = pd.DataFrame(request.data)
        
        if len(instance) != 1:
            raise ValueError("Une seule ligne attendue dans data")
        
        # Expliquer l'instance
        explanation = Ml2Service.explain_instance(model_data, instance)
        
        # Préparer la réponse
        meta = MetaData(
            dataset_id=request.meta.dataset_id,
            schema_version="1.0"
        )
        
        return StandardResponse(
            meta=meta,
            result=explanation,
            report={"status": "instance_explained"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
