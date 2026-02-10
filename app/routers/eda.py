"""
Router pour l'analyse exploratoire (TP2 - EDA)
Endpoints : /eda/summary, /eda/groupby, /eda/correlation, /eda/plots
"""

from fastapi import APIRouter, HTTPException
from app.schemas.common import (
    EdaSummaryRequest, EdaGroupbyRequest, EdaCorrelationRequest, 
    EdaPlotsRequest, StandardResponse, MetaData
)
from app.services.dataset_generator import DatasetGenerator
from app.services.eda_service import EdaService

router = APIRouter()


@router.post("/summary", response_model=StandardResponse)
def eda_summary(request: EdaSummaryRequest):
    """
    Génère un résumé statistique complet du dataset
    
    **Retour** :
    - Statistiques par variable (count, mean, std, min, max, quantiles)
    - Missing rate par variable
    - Pour catégorielles : top values
    
    **Exemple** :
    ```json
    {
        "meta": {
            "dataset_id": "eda_42_1000"
        }
    }
    ```
    """
    try:
        # Récupérer le dataset
        df = DatasetGenerator.get_dataset(request.meta.dataset_id)
        
        # Générer le résumé
        summary = EdaService.summary(df)
        
        # Préparer la réponse
        meta = MetaData(
            dataset_id=request.meta.dataset_id,
            schema_version="1.0"
        )
        
        return StandardResponse(
            meta=meta,
            result=summary,
            report={"status": "summary_generated"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/groupby", response_model=StandardResponse)
def eda_groupby(request: EdaGroupbyRequest):
    """
    Agrégation par groupe avec métriques spécifiées
    
    **Paramètres** :
    - `by` : Colonne de groupement (ex: "segment")
    - `metrics` : Liste de métriques (mean, median, sum, count, std, min, max)
    
    **Exemple** :
    ```json
    {
        "meta": {
            "dataset_id": "eda_42_1000"
        },
        "params": {
            "by": "segment",
            "metrics": ["mean", "median"]
        }
    }
    ```
    """
    try:
        # Récupérer le dataset
        df = DatasetGenerator.get_dataset(request.meta.dataset_id)
        
        # Extraire paramètres
        by = request.params.get("by")
        metrics = request.params.get("metrics", ["mean"])
        
        if not by:
            raise ValueError("Paramètre 'by' manquant")
        
        # Générer l'agrégation
        groupby_result = EdaService.groupby(df, by, metrics)
        
        # Préparer la réponse
        meta = MetaData(
            dataset_id=request.meta.dataset_id,
            schema_version="1.0"
        )
        
        return StandardResponse(
            meta=meta,
            result=groupby_result,
            report={"status": "groupby_completed"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/correlation", response_model=StandardResponse)
def eda_correlation(request: EdaCorrelationRequest):
    """
    Calcule la matrice de corrélation (Pearson)
    
    **Retour** :
    - Matrice de corrélation complète
    - Top 10 paires de variables corrélées
    
    **Exemple** :
    ```json
    {
        "meta": {
            "dataset_id": "eda_42_1000"
        }
    }
    ```
    """
    try:
        # Récupérer le dataset
        df = DatasetGenerator.get_dataset(request.meta.dataset_id)
        
        # Calculer corrélation
        correlation_result = EdaService.correlation(df)
        
        # Préparer la réponse
        meta = MetaData(
            dataset_id=request.meta.dataset_id,
            schema_version="1.0"
        )
        
        return StandardResponse(
            meta=meta,
            result=correlation_result,
            report={"status": "correlation_computed"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/plots", response_model=StandardResponse)
def eda_plots(request: EdaPlotsRequest):
    """
    Génère des graphiques interactifs (Plotly JSON)
    
    **Graphiques générés** :
    - Histogramme (distribution variable numérique)
    - Boxplot par segment
    - Barplot (distribution variable catégorielle)
    - Scatter plot (2 variables numériques)
    - Heatmap de corrélation
    
    **Exemple** :
    ```json
    {
        "meta": {
            "dataset_id": "eda_42_1000"
        }
    }
    ```
    
    **Retour** : Artefacts (graphiques en format Plotly JSON)
    """
    try:
        # Récupérer le dataset
        df = DatasetGenerator.get_dataset(request.meta.dataset_id)
        
        # Générer les graphiques
        params = request.params or {}
        artifacts = EdaService.plots(df, params)
        
        # Préparer la réponse
        meta = MetaData(
            dataset_id=request.meta.dataset_id,
            schema_version="1.0"
        )
        
        return StandardResponse(
            meta=meta,
            result={"n_plots": len(artifacts)},
            artifacts=artifacts,
            report={"status": "plots_generated"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
