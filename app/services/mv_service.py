"""
Service d'analyse multivariée (TP3 - MV)
PCA et Clustering avec résultats interprétables
"""

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from typing import Dict, Any, Tuple


class MvService:
    """
    Service pour l'analyse multivariée
    
    Fonctionnalités :
    - PCA (réduction dimensionnelle) avec loadings
    - K-Means clustering avec métriques
    - Rapports interprétatifs
    """
    
    @staticmethod
    def pca_fit_transform(df: pd.DataFrame, n_components: int, scale: bool = True) -> Dict[str, Any]:
        """
        Applique PCA et retourne projections + loadings
        
        Args:
            df: DataFrame (uniquement colonnes numériques)
            n_components: Nombre de composantes (2-5)
            scale: Si True, standardise les données avant PCA
            
        Returns:
            Dictionnaire avec :
            - projection : données projetées (PC1, PC2, ...)
            - explained_variance_ratio : variance expliquée par composante
            - loadings : contributions des variables originales
        """
        # Sélectionner colonnes numériques
        numeric_df = df.select_dtypes(include=[np.number])
        
        # Supprimer les NA
        numeric_df = numeric_df.dropna()
        
        if numeric_df.empty:
            raise ValueError("Aucune donnée numérique valide pour PCA")
        
        # Standardiser si demandé
        if scale:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(numeric_df)
        else:
            X_scaled = numeric_df.values
        
        # Appliquer PCA
        pca = PCA(n_components=n_components)
        X_pca = pca.fit_transform(X_scaled)
        
        # Créer DataFrame avec projections
        pc_columns = [f"PC{i+1}" for i in range(n_components)]
        projection_df = pd.DataFrame(X_pca, columns=pc_columns)
        
        # Calculer loadings (contributions des variables)
        loadings = pd.DataFrame(
            pca.components_.T,
            columns=pc_columns,
            index=numeric_df.columns
        )
        
        # Identifier top variables pour chaque PC
        top_loadings = {}
        for pc in pc_columns:
            # Trier par valeur absolue
            sorted_loadings = loadings[pc].abs().sort_values(ascending=False)
            top_loadings[pc] = {
                "top_variables": sorted_loadings.head(3).index.tolist(),
                "values": sorted_loadings.head(3).values.tolist()
            }
        
        return {
            "projection": projection_df.to_dict(orient='records'),
            "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
            "cumulative_variance": np.cumsum(pca.explained_variance_ratio_).tolist(),
            "loadings": loadings.to_dict(),
            "top_loadings": top_loadings,
            "n_components": n_components,
            "original_features": numeric_df.columns.tolist()
        }
    
    @staticmethod
    def cluster_kmeans(df: pd.DataFrame, k: int, scale: bool = True) -> Dict[str, Any]:
        """
        Applique K-Means clustering
        
        Args:
            df: DataFrame (uniquement colonnes numériques)
            k: Nombre de clusters (2-6)
            scale: Si True, standardise les données avant clustering
            
        Returns:
            Dictionnaire avec :
            - labels : étiquettes de cluster par ligne
            - centroids : centres des clusters
            - silhouette : score de silhouette (qualité clustering)
            - cluster_sizes : tailles des clusters
        """
        # Sélectionner colonnes numériques
        numeric_df = df.select_dtypes(include=[np.number])
        
        # Supprimer les NA
        numeric_df = numeric_df.dropna()
        
        if numeric_df.empty:
            raise ValueError("Aucune donnée numérique valide pour clustering")
        
        # Standardiser si demandé
        if scale:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(numeric_df)
        else:
            X_scaled = numeric_df.values
        
        # Appliquer K-Means
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        
        # Calculer silhouette score (si k >= 2 et au moins k points)
        silhouette = None
        if k >= 2 and len(X_scaled) >= k:
            try:
                silhouette = silhouette_score(X_scaled, labels)
            except:
                silhouette = None
        
        # Compter tailles des clusters
        unique, counts = np.unique(labels, return_counts=True)
        cluster_sizes = {f"cluster_{i}": int(count) for i, count in zip(unique, counts)}
        
        # Centroids (dans l'espace original si scale=True, sinon standardisé)
        if scale:
            # Retransformer les centroids dans l'espace original
            centroids = scaler.inverse_transform(kmeans.cluster_centers_)
        else:
            centroids = kmeans.cluster_centers_
        
        centroids_df = pd.DataFrame(
            centroids,
            columns=numeric_df.columns,
            index=[f"cluster_{i}" for i in range(k)]
        )
        
        return {
            "labels": labels.tolist(),
            "n_clusters": k,
            "cluster_sizes": cluster_sizes,
            "centroids": centroids_df.to_dict(),
            "silhouette_score": float(silhouette) if silhouette is not None else None,
            "inertia": float(kmeans.inertia_),
            "features_used": numeric_df.columns.tolist()
        }
    
    @staticmethod
    def generate_report(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Génère un rapport interprétatif pour analyse multivariée
        
        Args:
            df: DataFrame
            
        Returns:
            Dictionnaire avec insights interprétatifs
        """
        numeric_df = df.select_dtypes(include=[np.number]).dropna()
        
        if numeric_df.empty:
            return {"error": "Aucune donnée numérique pour analyse"}
        
        # PCA automatique avec 2 composantes
        pca_result = MvService.pca_fit_transform(numeric_df, n_components=2, scale=True)
        
        # Clustering automatique avec 3 clusters
        cluster_result = MvService.cluster_kmeans(numeric_df, k=3, scale=True)
        
        # Extraire insights
        report = {
            "n_features": len(numeric_df.columns),
            "n_samples": len(numeric_df),
            "pca_insights": {
                "variance_explained_by_pc1_pc2": sum(pca_result["explained_variance_ratio"][:2]),
                "top_contributors_pc1": pca_result["top_loadings"]["PC1"]["top_variables"],
                "top_contributors_pc2": pca_result["top_loadings"]["PC2"]["top_variables"]
            },
            "clustering_insights": {
                "n_clusters": cluster_result["n_clusters"],
                "cluster_sizes": cluster_result["cluster_sizes"],
                "silhouette_score": cluster_result["silhouette_score"],
                "quality": (
                    "excellent" if cluster_result["silhouette_score"] and cluster_result["silhouette_score"] > 0.7
                    else "good" if cluster_result["silhouette_score"] and cluster_result["silhouette_score"] > 0.5
                    else "moderate" if cluster_result["silhouette_score"] and cluster_result["silhouette_score"] > 0.3
                    else "weak"
                ) if cluster_result["silhouette_score"] is not None else "unknown"
            },
            "interpretation": {
                "message": f"Les 2 premières composantes principales expliquent {sum(pca_result['explained_variance_ratio'][:2]):.1%} de la variance totale.",
                "pc1_driven_by": pca_result["top_loadings"]["PC1"]["top_variables"][:2],
                "pc2_driven_by": pca_result["top_loadings"]["PC2"]["top_variables"][:2],
                "clustering_quality": cluster_result["silhouette_score"]
            }
        }
        
        return report
