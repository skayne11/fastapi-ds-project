"""
Router pour le nettoyage des données (TP1 - Clean)
Endpoints : /clean/fit, /clean/transform, /clean/report
"""

from fastapi import APIRouter, HTTPException
from app.schemas.common import CleanFitRequest, CleanTransformRequest, StandardRequest, StandardResponse, MetaData
from app.services.dataset_generator import DatasetGenerator, store_cleaner, get_cleaner
from app.services.cleaning_service import CleaningService

router = APIRouter()


@router.post("/fit", response_model=StandardResponse)
def clean_fit(request: CleanFitRequest):
    """
    Apprend un pipeline de nettoyage à partir des données
    
    **Paramètres** :
    - `impute_strategy` : Stratégie d'imputation (mean, median)
    - `outlier_strategy` : Traitement des outliers (clip, remove)
    - `categorical_strategy` : Encodage catégorielles (one_hot, ordinal)
    
    **Exemple** :
    ```json
    {
        "meta": {
            "dataset_id": "clean_42_1000"
        },
        "params": {
            "impute_strategy": "mean",
            "outlier_strategy": "clip",
            "categorical_strategy": "one_hot"
        }
    }
    ```
    
    **Retour** : cleaner_id + résumé des règles + rapport qualité avant
    """
    try:
        # Récupérer le dataset
        df = DatasetGenerator.get_dataset(request.meta.dataset_id)
        
        # Fitter le pipeline de nettoyage
        params = request.params.model_dump()
        cleaner_id, cleaner_data = CleaningService.fit(df, params)
        
        # Stocker le cleaner
        store_cleaner(cleaner_id, cleaner_data)
        
        # Préparer la réponse
        meta = MetaData(
            dataset_id=request.meta.dataset_id,
            schema_version="1.0"
        )
        
        result = {
            "cleaner_id": cleaner_id,
            "status": "fitted",
            "params_used": params
        }
        
        report = {
            "rules_learned": {
                "impute_values_count": len(cleaner_data["rules"].get("impute_values", {})),
                "outlier_bounds_count": len(cleaner_data["rules"].get("outlier_bounds", {})),
                "categorical_mappings_count": len(cleaner_data["rules"].get("categorical_mappings", {}))
            },
            "quality_before": cleaner_data["report_before"]
        }
        
        return StandardResponse(
            meta=meta,
            result=result,
            report=report
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/transform", response_model=StandardResponse)
def clean_transform(request: CleanTransformRequest):
    """
    Applique le pipeline de nettoyage appris
    
    **Paramètres** :
    - `cleaner_id` : ID du pipeline appris avec /fit
    
    **Exemple** :
    ```json
    {
        "meta": {
            "dataset_id": "clean_42_1000"
        },
        "params": {
            "cleaner_id": "cleaner_20260210_143022"
        }
    }
    ```
    
    **Retour** : Données nettoyées + compteurs (imputations, doublons, outliers)
    """
    try:
        # Récupérer le dataset et le cleaner
        df = DatasetGenerator.get_dataset(request.meta.dataset_id)
        cleaner_id = request.params.get("cleaner_id")
        
        if not cleaner_id:
            raise ValueError("cleaner_id manquant dans params")
        
        cleaner_data = get_cleaner(cleaner_id)
        
        # Appliquer la transformation
        df_clean, transform_report = CleaningService.transform(df, cleaner_data)
        
        # Stocker le dataset nettoyé
        cleaned_dataset_id = f"{request.meta.dataset_id}_cleaned"
        DatasetGenerator._datasets[cleaned_dataset_id] = df_clean
        
        # Préparer la réponse
        meta = MetaData(
            dataset_id=cleaned_dataset_id,
            schema_version="1.0"
        )
        
        result = {
            "processed_dataset_id": cleaned_dataset_id,
            "n_rows": len(df_clean),
            "n_cols": len(df_clean.columns),
            "columns": df_clean.columns.tolist(),
            "data_sample": df_clean.head(20).to_dict(orient='records')
        }
        
        return StandardResponse(
            meta=meta,
            result=result,
            report=transform_report
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/report/{dataset_id}", response_model=StandardResponse)
def clean_report(dataset_id: str):
    """
    Génère un rapport qualité sur un dataset (sans transformation)
    
    **Paramètre** : dataset_id (dans l'URL)
    
    **Retour** :
    - Taux de missing values par colonne
    - Nombre de doublons
    - Nombre d'outliers par colonne
    - Types détectés
    
    **Exemple** : `GET /clean/report/clean_42_1000`
    """
    try:
        # Récupérer le dataset
        df = DatasetGenerator.get_dataset(dataset_id)
        
        # Générer le rapport
        report = CleaningService.generate_report(df)
        
        # Préparer la réponse
        meta = MetaData(
            dataset_id=dataset_id,
            schema_version="1.0"
        )
        
        return StandardResponse(
            meta=meta,
            result={"status": "report_generated"},
            report=report
        )
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
