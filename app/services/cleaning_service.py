"""
Service de nettoyage des données (TP1)
Traite : missing values, doublons, outliers, types incohérents
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from datetime import datetime


class CleaningService:
    """
    Service pour le nettoyage et la préparation des données
    
    Fonctionnalités :
    - Imputation des valeurs manquantes (mean, median)
    - Suppression des doublons
    - Traitement des outliers (clip, remove)
    - Conversion des types
    - Encodage des variables catégorielles (one_hot, ordinal)
    """
    
    @staticmethod
    def generate_report(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Génère un rapport qualité sur un dataset
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire contenant :
            - missing_values : taux par colonne
            - duplicates : nombre de doublons
            - outliers : nombre par colonne
            - data_types : types détectés
        """
        report = {
            "n_rows": len(df),
            "n_cols": len(df.columns),
            "missing_values": {},
            "duplicates": int(df.duplicated().sum()),
            "outliers": {},
            "data_types": {}
        }
        
        # Analyser les missing values
        for col in df.columns:
            missing_count = df[col].isna().sum()
            missing_rate = missing_count / len(df) if len(df) > 0 else 0
            report["missing_values"][col] = {
                "count": int(missing_count),
                "rate": float(missing_rate)
            }
        
        # Analyser les outliers (pour colonnes numériques)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in df.columns:
                try:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 3 * IQR
                    upper_bound = Q3 + 3 * IQR
                    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                    report["outliers"][col] = {
                        "count": int(len(outliers)),
                        "rate": float(len(outliers) / len(df)) if len(df) > 0 else 0
                    }
                except:
                    report["outliers"][col] = {"count": 0, "rate": 0.0}
        
        # Analyser les types
        for col in df.columns:
            report["data_types"][col] = str(df[col].dtype)
        
        return report
    
    @staticmethod
    def fit(df: pd.DataFrame, params: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Apprend un pipeline de nettoyage à partir des données
        
        Args:
            df: DataFrame d'entraînement
            params: Paramètres du pipeline
                - impute_strategy: mean | median
                - outlier_strategy: clip | remove
                - categorical_strategy: one_hot | ordinal
                
        Returns:
            Tuple (cleaner_id, cleaner_data)
        """
        # Générer un ID unique pour ce cleaner
        cleaner_id = f"cleaner_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Préparer les métadonnées du cleaner
        cleaner_data = {
            "cleaner_id": cleaner_id,
            "params": params,
            "rules": {},
            "columns": list(df.columns),
            "report_before": CleaningService.generate_report(df)
        }
        
        # Identifier les colonnes numériques et catégorielles
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Apprendre les règles d'imputation pour colonnes numériques
        impute_strategy = params.get("impute_strategy", "mean")
        impute_values = {}
        
        for col in numeric_cols:
            if col in df.columns:
                if impute_strategy == "mean":
                    impute_values[col] = float(df[col].mean())
                elif impute_strategy == "median":
                    impute_values[col] = float(df[col].median())
                else:
                    impute_values[col] = float(df[col].mean())
        
        cleaner_data["rules"]["impute_values"] = impute_values
        
        # Apprendre les règles pour outliers (bornes)
        outlier_strategy = params.get("outlier_strategy", "clip")
        outlier_bounds = {}
        
        for col in numeric_cols:
            if col in df.columns:
                try:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 3 * IQR
                    upper_bound = Q3 + 3 * IQR
                    outlier_bounds[col] = {
                        "lower": float(lower_bound),
                        "upper": float(upper_bound)
                    }
                except:
                    pass
        
        cleaner_data["rules"]["outlier_bounds"] = outlier_bounds
        cleaner_data["rules"]["outlier_strategy"] = outlier_strategy
        
        # Apprendre les règles pour catégorielles
        categorical_strategy = params.get("categorical_strategy", "one_hot")
        categorical_mappings = {}
        
        for col in categorical_cols:
            if col in df.columns:
                unique_values = df[col].dropna().unique().tolist()
                categorical_mappings[col] = {
                    "values": unique_values,
                    "strategy": categorical_strategy
                }
        
        cleaner_data["rules"]["categorical_mappings"] = categorical_mappings
        
        # Mémoriser les types des colonnes
        cleaner_data["rules"]["numeric_cols"] = numeric_cols
        cleaner_data["rules"]["categorical_cols"] = categorical_cols
        
        return cleaner_id, cleaner_data
    
    @staticmethod
    def transform(df: pd.DataFrame, cleaner_data: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Applique le pipeline de nettoyage appris
        
        Args:
            df: DataFrame à nettoyer
            cleaner_data: Pipeline appris avec fit()
            
        Returns:
            Tuple (df_clean, report)
        """
        df_clean = df.copy()
        
        # Compteurs pour le rapport
        counters = {
            "rows_before": len(df_clean),
            "duplicates_removed": 0,
            "missing_imputed": {},
            "outliers_treated": {},
            "types_converted": 0
        }
        
        rules = cleaner_data["rules"]
        params = cleaner_data["params"]
        
        # 1. Supprimer les doublons
        duplicates_before = df_clean.duplicated().sum()
        df_clean = df_clean.drop_duplicates()
        counters["duplicates_removed"] = int(duplicates_before)
        
        # 2. Convertir les types (forcer les colonnes numériques)
        numeric_cols = rules.get("numeric_cols", [])
        for col in numeric_cols:
            if col in df_clean.columns:
                # Convertir en numérique (les valeurs non-numériques deviennent NaN)
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                counters["types_converted"] += 1
        
        # 3. Imputer les valeurs manquantes
        impute_values = rules.get("impute_values", {})
        for col, value in impute_values.items():
            if col in df_clean.columns:
                missing_before = df_clean[col].isna().sum()
                df_clean[col] = df_clean[col].fillna(value)
                counters["missing_imputed"][col] = int(missing_before)
        
        # 4. Traiter les outliers
        outlier_bounds = rules.get("outlier_bounds", {})
        outlier_strategy = rules.get("outlier_strategy", "clip")
        
        for col, bounds in outlier_bounds.items():
            if col in df_clean.columns:
                lower = bounds["lower"]
                upper = bounds["upper"]
                
                if outlier_strategy == "clip":
                    # Clipper les valeurs
                    outliers_before = ((df_clean[col] < lower) | (df_clean[col] > upper)).sum()
                    df_clean[col] = df_clean[col].clip(lower, upper)
                    counters["outliers_treated"][col] = int(outliers_before)
                elif outlier_strategy == "remove":
                    # Supprimer les lignes avec outliers
                    outliers_mask = (df_clean[col] < lower) | (df_clean[col] > upper)
                    outliers_before = outliers_mask.sum()
                    df_clean = df_clean[~outliers_mask]
                    counters["outliers_treated"][col] = int(outliers_before)
        
        # 5. Encoder les variables catégorielles
        categorical_mappings = rules.get("categorical_mappings", {})
        for col, mapping in categorical_mappings.items():
            if col in df_clean.columns:
                strategy = mapping["strategy"]
                
                if strategy == "one_hot":
                    # One-hot encoding
                    dummies = pd.get_dummies(df_clean[col], prefix=col, drop_first=True)
                    df_clean = pd.concat([df_clean, dummies], axis=1)
                    df_clean = df_clean.drop(columns=[col])
                elif strategy == "ordinal":
                    # Ordinal encoding (ordre alphabétique)
                    categories = sorted(mapping["values"])
                    df_clean[col] = pd.Categorical(
                        df_clean[col], 
                        categories=categories, 
                        ordered=True
                    ).codes
        
        counters["rows_after"] = len(df_clean)
        
        # Générer rapport après nettoyage
        report = {
            "counters": counters,
            "report_after": CleaningService.generate_report(df_clean)
        }
        
        return df_clean, report
