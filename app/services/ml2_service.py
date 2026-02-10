"""
Service Machine Learning Avancé (TP5 - ML2)
Tuning, Feature Importance, Explicabilité
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, Tuple, List
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class Ml2Service:
    """
    Service pour Machine Learning Avancé
    
    Fonctionnalités :
    - Hyperparameter tuning (Grid Search, Random Search)
    - Feature importance (native + permutation)
    - Explicabilité locale (LIME-like)
    - Cross-validation
    """
    
    @staticmethod
    def tune_model(
        df: pd.DataFrame, 
        model_type: str, 
        search_type: str = "grid", 
        cv: int = 3
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Optimise les hyperparamètres d'un modèle via Grid/Random Search
        
        Args:
            df: DataFrame avec features + target
            model_type: Type de modèle (logreg, rf)
            search_type: Type de recherche (grid, random)
            cv: Nombre de folds pour cross-validation
            
        Returns:
            Tuple (best_model_id, model_data)
        """
        # Vérifier que target existe
        if 'target' not in df.columns:
            raise ValueError("Colonne 'target' manquante")
        
        # Séparer features et target
        X = df.drop(columns=['target'])
        y = df['target']
        
        # Preprocessing
        categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
        
        X_processed = X.copy()
        if len(categorical_cols) > 0:
            X_processed = pd.get_dummies(X_processed, columns=categorical_cols, drop_first=True)
        
        # Imputer NA
        for col in X_processed.columns:
            if X_processed[col].isna().any():
                X_processed[col] = X_processed[col].fillna(X_processed[col].mean())
        
        # Standardisation
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_processed)
        
        # Définir grilles de paramètres
        if model_type == "logreg":
            model = LogisticRegression(random_state=42, max_iter=1000)
            param_grid = {
                'C': [0.01, 0.1, 1, 10, 100],
                'penalty': ['l2'],
                'solver': ['lbfgs', 'liblinear']
            }
        elif model_type == "rf":
            model = RandomForestClassifier(random_state=42)
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
        else:
            raise ValueError(f"Type de modèle inconnu: {model_type}")
        
        # Recherche d'hyperparamètres
        if search_type == "grid":
            search = GridSearchCV(
                model, 
                param_grid, 
                cv=cv, 
                scoring='f1',
                n_jobs=-1
            )
        elif search_type == "random":
            search = RandomizedSearchCV(
                model,
                param_grid,
                n_iter=10,
                cv=cv,
                scoring='f1',
                random_state=42,
                n_jobs=-1
            )
        else:
            raise ValueError(f"Type de recherche inconnu: {search_type}")
        
        # Fit
        search.fit(X_scaled, y)
        
        # Meilleur modèle
        best_model = search.best_estimator_
        
        # Résultats CV
        cv_results = pd.DataFrame(search.cv_results_)
        cv_results_sorted = cv_results.sort_values('rank_test_score')
        
        # Top 5 configs
        top_configs = []
        for idx, row in cv_results_sorted.head(5).iterrows():
            top_configs.append({
                "params": row['params'],
                "mean_score": float(row['mean_test_score']),
                "std_score": float(row['std_test_score'])
            })
        
        # Générer model_id
        model_id = f"tuned_{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Stocker les métadonnées
        model_data = {
            "model_id": model_id,
            "model_type": model_type,
            "model_object": best_model,
            "scaler": scaler,
            "features": X_processed.columns.tolist(),
            "categorical_cols": categorical_cols,
            "created_at": datetime.now().isoformat(),
            "best_params": search.best_params_,
            "best_score": float(search.best_score_),
            "cv_folds": cv,
            "search_type": search_type,
            "top_configs": top_configs
        }
        
        return model_id, model_data
    
    @staticmethod
    def feature_importance(model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait l'importance des features
        
        Pour RandomForest : importance native
        Pour LogisticRegression : coefficients (valeur absolue)
        
        Args:
            model_data: Données du modèle
            
        Returns:
            Dictionnaire avec importance par feature
        """
        model = model_data["model_object"]
        features = model_data["features"]
        model_type = model_data["model_type"]
        
        importance_dict = {}
        
        if hasattr(model, 'feature_importances_'):
            # RandomForest
            importances = model.feature_importances_
            for feat, imp in zip(features, importances):
                importance_dict[feat] = float(imp)
        
        elif hasattr(model, 'coef_'):
            # LogisticRegression
            coefficients = model.coef_[0]
            for feat, coef in zip(features, coefficients):
                importance_dict[feat] = float(abs(coef))
        
        else:
            raise ValueError("Modèle sans feature importance disponible")
        
        # Trier par importance décroissante
        sorted_importance = dict(sorted(
            importance_dict.items(), 
            key=lambda x: x[1], 
            reverse=True
        ))
        
        # Top 10
        top_features = list(sorted_importance.items())[:10]
        
        return {
            "model_type": model_type,
            "all_features": sorted_importance,
            "top_features": {feat: imp for feat, imp in top_features},
            "n_features": len(features)
        }
    
    @staticmethod
    def permutation_importance_analysis(
        model_data: Dict[str, Any],
        X: pd.DataFrame,
        y: pd.Series,
        n_repeats: int = 10
    ) -> Dict[str, Any]:
        """
        Calcule permutation importance (modèle-agnostique)
        
        Args:
            model_data: Données du modèle
            X: Features
            y: Target
            n_repeats: Nombre de répétitions
            
        Returns:
            Dictionnaire avec importance par permutation
        """
        model = model_data["model_object"]
        scaler = model_data["scaler"]
        categorical_cols = model_data["categorical_cols"]
        features = model_data["features"]
        
        # Preprocessing
        X_processed = X.copy()
        if len(categorical_cols) > 0:
            X_processed = pd.get_dummies(X_processed, columns=categorical_cols, drop_first=True)
        
        # Ajouter colonnes manquantes
        for col in features:
            if col not in X_processed.columns:
                X_processed[col] = 0
        
        X_processed = X_processed[features]
        
        # Imputer NA
        for col in X_processed.columns:
            if X_processed[col].isna().any():
                X_processed[col] = X_processed[col].fillna(0)
        
        # Standardisation
        X_scaled = scaler.transform(X_processed)
        
        # Calculer permutation importance
        perm_importance = permutation_importance(
            model, 
            X_scaled, 
            y, 
            n_repeats=n_repeats,
            random_state=42,
            scoring='f1'
        )
        
        # Créer dictionnaire
        importance_dict = {}
        for feat, imp_mean, imp_std in zip(
            features, 
            perm_importance.importances_mean,
            perm_importance.importances_std
        ):
            importance_dict[feat] = {
                "mean": float(imp_mean),
                "std": float(imp_std)
            }
        
        # Trier par importance moyenne
        sorted_importance = dict(sorted(
            importance_dict.items(),
            key=lambda x: x[1]["mean"],
            reverse=True
        ))
        
        # Top 10
        top_features = list(sorted_importance.items())[:10]
        
        return {
            "permutation_importance": sorted_importance,
            "top_features": {feat: vals for feat, vals in top_features},
            "n_repeats": n_repeats
        }
    
    @staticmethod
    def explain_instance(
        model_data: Dict[str, Any],
        instance: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Explication locale d'une prédiction
        
        Pour LogReg : contribution ≈ coef × valeur standardisée
        Pour RF : approximation via importance locale
        
        Args:
            model_data: Données du modèle
            instance: Une seule ligne de features
            
        Returns:
            Dictionnaire avec explication
        """
        model = model_data["model_object"]
        scaler = model_data["scaler"]
        categorical_cols = model_data["categorical_cols"]
        features = model_data["features"]
        model_type = model_data["model_type"]
        
        # Preprocessing
        X_processed = instance.copy()
        if len(categorical_cols) > 0:
            X_processed = pd.get_dummies(X_processed, columns=categorical_cols, drop_first=True)
        
        # Ajouter colonnes manquantes
        for col in features:
            if col not in X_processed.columns:
                X_processed[col] = 0
        
        X_processed = X_processed[features]
        
        # Imputer NA
        for col in X_processed.columns:
            if X_processed[col].isna().any():
                X_processed[col] = X_processed[col].fillna(0)
        
        # Standardisation
        X_scaled = scaler.transform(X_processed)
        
        # Prédiction
        prediction = model.predict(X_scaled)[0]
        try:
            proba = model.predict_proba(X_scaled)[0][1]
        except:
            proba = None
        
        # Explication
        contributions = {}
        
        if hasattr(model, 'coef_'):
            # LogisticRegression : contribution = coef × valeur standardisée
            coefficients = model.coef_[0]
            for feat, coef, val in zip(features, coefficients, X_scaled[0]):
                contribution = coef * val
                contributions[feat] = float(contribution)
        
        elif hasattr(model, 'feature_importances_'):
            # RandomForest : approximation simple
            importances = model.feature_importances_
            for feat, imp, val in zip(features, importances, X_scaled[0]):
                # Contribution approximative (importance × écart à la moyenne)
                contribution = imp * val
                contributions[feat] = float(contribution)
        
        # Trier par contribution absolue
        sorted_contributions = dict(sorted(
            contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        ))
        
        # Top 5 facteurs
        top_positive = {k: v for k, v in sorted_contributions.items() if v > 0}
        top_negative = {k: v for k, v in sorted_contributions.items() if v < 0}
        
        top_positive = dict(list(top_positive.items())[:5])
        top_negative = dict(list(top_negative.items())[:5])
        
        return {
            "prediction": int(prediction),
            "probability": float(proba) if proba is not None else None,
            "model_type": model_type,
            "contributions": sorted_contributions,
            "top_positive_factors": top_positive,
            "top_negative_factors": top_negative,
            "interpretation": (
                f"Prédiction: classe {prediction} "
                f"(probabilité: {proba:.2%})" if proba is not None else ""
            )
        }
