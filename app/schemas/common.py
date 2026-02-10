"""
Schémas Pydantic pour la validation des données
Structure standardisée pour toutes les requêtes et réponses
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# SCHÉMAS DE BASE (ENVELOPPE STANDARD)
# ============================================================================

class MetaData(BaseModel):
    """
    Métadonnées présentes dans toutes les requêtes/réponses
    Permet le traçage et la versionnement
    """
    dataset_id: Optional[str] = Field(None, description="Identifiant unique du dataset")
    schema_version: str = Field(default="1.0", description="Version du schéma de données")
    
    class Config:
        json_schema_extra = {
            "example": {
                "dataset_id": "clean_42_1000",
                "schema_version": "1.0"
            }
        }


class StandardRequest(BaseModel):
    """
    Structure standard pour toutes les requêtes
    - meta : métadonnées
    - data : données (optionnel)
    - params : paramètres spécifiques à l'endpoint
    """
    meta: MetaData
    data: Optional[List[Dict[str, Any]]] = Field(None, description="Données d'entrée (records)")
    params: Optional[Dict[str, Any]] = Field(None, description="Paramètres spécifiques")
    
    class Config:
        json_schema_extra = {
            "example": {
                "meta": {
                    "dataset_id": "clean_42_1000",
                    "schema_version": "1.0"
                },
                "params": {
                    "impute_strategy": "mean"
                }
            }
        }


class StandardResponse(BaseModel):
    """
    Structure standard pour toutes les réponses
    - meta : métadonnées
    - result : résultat principal
    - report : rapport/statistiques
    - artifacts : artefacts (graphiques, modèles, etc.)
    """
    meta: MetaData
    result: Optional[Dict[str, Any]] = Field(None, description="Résultat principal")
    report: Optional[Dict[str, Any]] = Field(None, description="Rapport/statistiques")
    artifacts: Optional[Dict[str, Any]] = Field(None, description="Artefacts (graphiques, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "meta": {
                    "dataset_id": "clean_42_1000",
                    "schema_version": "1.0"
                },
                "result": {
                    "status": "success"
                },
                "report": {
                    "missing_values": 150,
                    "duplicates": 25
                }
            }
        }


# ============================================================================
# SCHÉMAS POUR LA GÉNÉRATION DE DATASETS
# ============================================================================

class DatasetGenerateRequest(BaseModel):
    """
    Requête pour générer un dataset
    """
    phase: str = Field(..., description="Phase du projet (clean, eda, mv, ml, ml2)")
    seed: int = Field(..., description="Graine aléatoire pour reproductibilité")
    n: int = Field(..., description="Nombre de lignes du dataset", gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "phase": "clean",
                "seed": 42,
                "n": 1000
            }
        }


class DatasetGenerateResponse(BaseModel):
    """
    Réponse après génération d'un dataset
    """
    meta: MetaData
    result: Dict[str, Any] = Field(..., description="Informations sur le dataset généré")
    
    class Config:
        json_schema_extra = {
            "example": {
                "meta": {
                    "dataset_id": "clean_42_1000",
                    "schema_version": "1.0"
                },
                "result": {
                    "columns": ["x1", "x2", "x3", "segment", "target"],
                    "n_rows": 1000,
                    "data_sample": []
                }
            }
        }


# ============================================================================
# SCHÉMAS SPÉCIFIQUES TP1 - CLEAN
# ============================================================================

class CleanFitParams(BaseModel):
    """
    Paramètres pour l'apprentissage du pipeline de nettoyage
    """
    impute_strategy: str = Field("mean", description="Stratégie d'imputation (mean, median)")
    outlier_strategy: str = Field("clip", description="Stratégie pour les outliers (clip, remove)")
    categorical_strategy: str = Field("one_hot", description="Stratégie pour variables catégorielles (one_hot, ordinal)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "impute_strategy": "mean",
                "outlier_strategy": "clip",
                "categorical_strategy": "one_hot"
            }
        }


class CleanFitRequest(BaseModel):
    """
    Requête pour fitter un pipeline de nettoyage
    """
    meta: MetaData
    params: CleanFitParams


class CleanTransformRequest(BaseModel):
    """
    Requête pour transformer des données avec un pipeline appris
    """
    meta: MetaData
    params: Dict[str, Any] = Field(..., description="Contient cleaner_id")


# ============================================================================
# SCHÉMAS SPÉCIFIQUES TP2 - EDA
# ============================================================================

class EdaSummaryRequest(BaseModel):
    """
    Requête pour obtenir un résumé statistique
    """
    meta: MetaData


class EdaGroupbyRequest(BaseModel):
    """
    Requête pour agrégation par groupe
    """
    meta: MetaData
    params: Dict[str, Any] = Field(
        ..., 
        description="Contient 'by' (colonne de groupement) et 'metrics' (liste de métriques)"
    )


class EdaCorrelationRequest(BaseModel):
    """
    Requête pour matrice de corrélation
    """
    meta: MetaData


class EdaPlotsRequest(BaseModel):
    """
    Requête pour générer des graphiques
    """
    meta: MetaData
    params: Optional[Dict[str, Any]] = Field(None, description="Paramètres optionnels pour les plots")


# ============================================================================
# SCHÉMAS SPÉCIFIQUES TP3 - MV
# ============================================================================

class MvPcaRequest(BaseModel):
    """
    Requête pour PCA
    """
    meta: MetaData
    params: Dict[str, Any] = Field(
        ..., 
        description="Contient 'n_components' (2-5) et 'scale' (bool)"
    )


class MvClusterRequest(BaseModel):
    """
    Requête pour clustering K-Means
    """
    meta: MetaData
    params: Dict[str, Any] = Field(
        ..., 
        description="Contient 'k' (2-6) et 'scale' (bool)"
    )


# ============================================================================
# SCHÉMAS SPÉCIFIQUES TP4 - ML
# ============================================================================

class MlTrainRequest(BaseModel):
    """
    Requête pour entraîner un modèle
    """
    meta: MetaData
    params: Dict[str, Any] = Field(
        ..., 
        description="Contient 'model_type' (logreg, rf)"
    )


class MlPredictRequest(BaseModel):
    """
    Requête pour faire des prédictions
    """
    meta: MetaData
    data: List[Dict[str, Any]] = Field(..., description="Données sans target")
    params: Dict[str, Any] = Field(..., description="Contient 'model_id'")


# ============================================================================
# SCHÉMAS SPÉCIFIQUES TP5 - ML2
# ============================================================================

class Ml2TuneRequest(BaseModel):
    """
    Requête pour tuning d'hyperparamètres
    """
    meta: MetaData
    params: Dict[str, Any] = Field(
        ..., 
        description="Contient 'model_type', 'search' (grid/random), 'cv' (3 ou 5)"
    )


class Ml2PermutationImportanceRequest(BaseModel):
    """
    Requête pour permutation importance
    """
    meta: MetaData
    params: Dict[str, Any] = Field(..., description="Contient 'model_id' et 'n_repeats'")


class Ml2ExplainInstanceRequest(BaseModel):
    """
    Requête pour explication locale d'une instance
    """
    meta: MetaData
    data: List[Dict[str, Any]] = Field(..., description="Une seule ligne de features")
    params: Dict[str, Any] = Field(..., description="Contient 'model_id'")
