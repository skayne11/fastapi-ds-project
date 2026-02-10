"""
Service d'analyse exploratoire des données (TP2 - EDA)
Statistiques descriptives et visualisations
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List


class EdaService:
    """
    Service pour l'analyse exploratoire des données (EDA)
    
    Fonctionnalités :
    - Statistiques descriptives par variable
    - Agrégations par groupe
    - Matrice de corrélation
    - Graphiques interactifs (Plotly JSON)
    """
    
    @staticmethod
    def summary(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Génère un résumé statistique complet du dataset
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire avec statistiques par variable
        """
        summary_dict = {}
        
        for col in df.columns:
            col_stats = {
                "type": str(df[col].dtype),
                "count": int(df[col].count()),
                "missing_count": int(df[col].isna().sum()),
                "missing_rate": float(df[col].isna().sum() / len(df))
            }
            
            # Statistiques pour colonnes numériques
            if pd.api.types.is_numeric_dtype(df[col]):
                col_stats.update({
                    "mean": float(df[col].mean()) if not df[col].isna().all() else None,
                    "std": float(df[col].std()) if not df[col].isna().all() else None,
                    "min": float(df[col].min()) if not df[col].isna().all() else None,
                    "25%": float(df[col].quantile(0.25)) if not df[col].isna().all() else None,
                    "50%": float(df[col].quantile(0.50)) if not df[col].isna().all() else None,
                    "75%": float(df[col].quantile(0.75)) if not df[col].isna().all() else None,
                    "max": float(df[col].max()) if not df[col].isna().all() else None,
                })
            
            # Statistiques pour colonnes catégorielles
            else:
                value_counts = df[col].value_counts().to_dict()
                col_stats.update({
                    "unique_count": int(df[col].nunique()),
                    "top_values": {str(k): int(v) for k, v in list(value_counts.items())[:5]}
                })
            
            summary_dict[col] = col_stats
        
        return {
            "n_rows": len(df),
            "n_cols": len(df.columns),
            "variables": summary_dict
        }
    
    @staticmethod
    def groupby(df: pd.DataFrame, by: str, metrics: List[str]) -> Dict[str, Any]:
        """
        Agrégation par groupe avec métriques spécifiées
        
        Args:
            df: DataFrame
            by: Colonne de groupement
            metrics: Liste de métriques (mean, median, sum, count, std, min, max)
            
        Returns:
            Dictionnaire avec résultats agrégés
        """
        if by not in df.columns:
            raise ValueError(f"Colonne '{by}' introuvable dans le dataset")
        
        # Identifier les colonnes numériques (excluant la colonne de groupement)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        results = {}
        
        for metric in metrics:
            if metric == "mean":
                agg_df = df.groupby(by)[numeric_cols].mean()
            elif metric == "median":
                agg_df = df.groupby(by)[numeric_cols].median()
            elif metric == "sum":
                agg_df = df.groupby(by)[numeric_cols].sum()
            elif metric == "count":
                agg_df = df.groupby(by)[numeric_cols].count()
            elif metric == "std":
                agg_df = df.groupby(by)[numeric_cols].std()
            elif metric == "min":
                agg_df = df.groupby(by)[numeric_cols].min()
            elif metric == "max":
                agg_df = df.groupby(by)[numeric_cols].max()
            else:
                continue
            
            # Convertir en records
            agg_df = agg_df.reset_index()
            results[metric] = agg_df.to_dict(orient='records')
        
        return {
            "grouped_by": by,
            "metrics": metrics,
            "results": results
        }
    
    @staticmethod
    def correlation(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcule la matrice de corrélation (Pearson)
        
        Args:
            df: DataFrame
            
        Returns:
            Dictionnaire avec matrice de corrélation et top paires
        """
        # Sélectionner uniquement les colonnes numériques
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {
                "error": "Aucune colonne numérique trouvée",
                "correlation_matrix": {},
                "top_correlations": []
            }
        
        # Calculer la matrice de corrélation
        corr_matrix = numeric_df.corr()
        
        # Convertir en dictionnaire
        corr_dict = corr_matrix.to_dict()
        
        # Extraire les top paires de corrélations (hors diagonale)
        top_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]
                
                if not np.isnan(corr_value):
                    top_pairs.append({
                        "var1": col1,
                        "var2": col2,
                        "correlation": float(corr_value)
                    })
        
        # Trier par valeur absolue de corrélation (décroissant)
        top_pairs = sorted(top_pairs, key=lambda x: abs(x["correlation"]), reverse=True)
        
        return {
            "correlation_matrix": corr_dict,
            "top_correlations": top_pairs[:10]  # Top 10
        }
    
    @staticmethod
    def plots(df: pd.DataFrame, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Génère des graphiques interactifs (Plotly JSON)
        
        Args:
            df: DataFrame
            params: Paramètres optionnels
            
        Returns:
            Dictionnaire d'artefacts (graphiques en JSON)
        """
        artifacts = {}
        
        # Identifier colonnes numériques et catégorielles
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # 1. Histogramme (première variable numérique)
        if len(numeric_cols) > 0:
            col = numeric_cols[0]
            fig = px.histogram(
                df, 
                x=col, 
                title=f"Distribution de {col}",
                labels={col: col},
                nbins=30
            )
            artifacts["histogram"] = fig.to_json()
        
        # 2. Boxplot par segment (si segment existe)
        if len(numeric_cols) > 0 and len(categorical_cols) > 0:
            numeric_col = numeric_cols[0]
            categorical_col = categorical_cols[0]
            
            fig = px.box(
                df,
                x=categorical_col,
                y=numeric_col,
                title=f"{numeric_col} par {categorical_col}",
                labels={numeric_col: numeric_col, categorical_col: categorical_col}
            )
            artifacts["boxplot"] = fig.to_json()
        
        # 3. Barplot (distribution première variable catégorielle)
        if len(categorical_cols) > 0:
            col = categorical_cols[0]
            value_counts = df[col].value_counts()
            
            fig = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                title=f"Distribution de {col}",
                labels={"x": col, "y": "Fréquence"}
            )
            artifacts["barplot"] = fig.to_json()
        
        # 4. Scatter plot (2 premières variables numériques)
        if len(numeric_cols) >= 2:
            col1 = numeric_cols[0]
            col2 = numeric_cols[1]
            
            # Ajouter couleur par segment si disponible
            color = categorical_cols[0] if len(categorical_cols) > 0 else None
            
            fig = px.scatter(
                df,
                x=col1,
                y=col2,
                color=color,
                title=f"{col1} vs {col2}",
                labels={col1: col1, col2: col2}
            )
            artifacts["scatterplot"] = fig.to_json()
        
        # 5. Matrice de corrélation (heatmap)
        if len(numeric_cols) >= 2:
            numeric_df = df[numeric_cols]
            corr = numeric_df.corr()
            
            fig = go.Figure(data=go.Heatmap(
                z=corr.values,
                x=corr.columns,
                y=corr.columns,
                colorscale='RdBu',
                zmid=0,
                text=corr.values.round(2),
                texttemplate='%{text}',
                textfont={"size": 10}
            ))
            
            fig.update_layout(
                title="Matrice de Corrélation",
                xaxis_title="Variables",
                yaxis_title="Variables"
            )
            
            artifacts["correlation_heatmap"] = fig.to_json()
        
        return artifacts
