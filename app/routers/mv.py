"""
Router pour l'analyse multivariée (TP3 - MV)
Endpoints : /mv/pca/fit_transform, /mv/cluster/kmeans, /mv/report
"""

from fastapi import APIRouter, HTTPException
from app.schemas.common import MvPcaRequest, MvClusterRequest, StandardResponse, MetaData
from app.services.dataset_generator import DatasetGenerator
from app.services.mv_service import MvService

router = APIRouter()


@router.post("/pca/fit_transform", response_model=StandardResponse)
def mv_pca_fit_transform(request: MvPcaRequest):
    """
    Applique PCA (réduction dimensionnelle)
    
    **Paramètres** :
    - `n_components` : Nombre de composantes (2-5)
    - `scale` : Standardiser les données avant PCA (booléen)
    
    **Retour** :
    - Projection des données (PC1, PC2, ...)
    - Variance expliquée par composante
    - Loadings (contributions des variables)
    - Top variables par composante
    
    **Exemple** :
    ```json
    {
        "meta": {
            "dataset_id": "mv_42_1000"
        },
        "params": {
            "n_components": 3,
            "scale": true
        }
    }
    ```
    """
    try:
        # Récupérer le dataset
        df = DatasetGenerator.get_dataset(request.meta.dataset_id)
        
        # Extraire paramètres
        n_components = request.params.get("n_components", 2)
        scale = request.params.get("scale", True)
        
        # Appliquer PCA
        pca_result = MvService.pca_fit_transform(df, n_components, scale)
        
        # Préparer la réponse
        meta = MetaData(
            dataset_id=request.meta.dataset_id,
            schema_version="1.0"
        )
        
        return StandardResponse(
            meta=meta,
            result=pca_result,
            report={
                "status": "pca_completed",
                "interpretation": {
                    "variance_explained": f"{sum(pca_result['explained_variance_ratio']):.1%}",
                    "top_pc1_contributors": pca_result['top_loadings']['PC1']['top_variables']
                }
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cluster/kmeans", response_model=StandardResponse)
def mv_cluster_kmeans(request: MvClusterRequest):
    """
    Applique clustering K-Means
    
    **Paramètres** :
    - `k` : Nombre de clusters (2-6)
    - `scale` : Standardiser les données avant clustering (booléen)
    
    **Retour** :
    - Labels de cluster par ligne
    - Centroids des clusters
    - Silhouette score (qualité)
    - Tailles des clusters
    
    **Exemple** :
    ```json
    {
        "meta": {
            "dataset_id": "mv_42_1000"
        },
        "params": {
            "k": 3,
            "scale": true
        }
    }
    ```
    """
    try:
        # Récupérer le dataset
        df = DatasetGenerator.get_dataset(request.meta.dataset_id)
        
        # Extraire paramètres
        k = request.params.get("k", 3)
        scale = request.params.get("scale", True)
        
        # Appliquer K-Means
        cluster_result = MvService.cluster_kmeans(df, k, scale)
        
        # Préparer la réponse
        meta = MetaData(
            dataset_id=request.meta.dataset_id,
            schema_version="1.0"
        )
        
        # Interpréter qualité
        silhouette = cluster_result.get("silhouette_score")
        quality = (
            "excellent" if silhouette and silhouette > 0.7
            else "good" if silhouette and silhouette > 0.5
            else "moderate" if silhouette and silhouette > 0.3
            else "weak"
        ) if silhouette is not None else "unknown"
        
        return StandardResponse(
            meta=meta,
            result=cluster_result,
            report={
                "status": "clustering_completed",
                "interpretation": {
                    "silhouette_score": silhouette,
                    "quality": quality,
                    "cluster_sizes": cluster_result["cluster_sizes"]
                }
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/report/{dataset_id}", response_model=StandardResponse)
def mv_report(dataset_id: str):
    """
    Génère un rapport interprétatif pour analyse multivariée
    
    **Paramètre** : dataset_id (dans l'URL)
    
    **Retour** :
    - Insights PCA (variance expliquée, top contributors)
    - Insights clustering (qualité, tailles)
    - Interprétation textuelle
    
    **Exemple** : `GET /mv/report/mv_42_1000`
    """
    try:
        # Récupérer le dataset
        df = DatasetGenerator.get_dataset(dataset_id)
        
        # Générer le rapport
        report = MvService.generate_report(df)
        
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
