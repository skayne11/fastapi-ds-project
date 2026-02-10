"""
Application FastAPI - Projet Data Science en 5 phases
Point d'entrée principal
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import dataset, clean, eda, mv, ml, ml2

# Créer l'application FastAPI
app = FastAPI(
    title="FastAPI Data Science - Projet Fil Rouge",
    description="""
    API complète pour un parcours Data Scientist en 5 phases :
    
    - **TP1 - Clean** : Nettoyage et préparation des données
    - **TP2 - EDA** : Analyse exploratoire et visualisations
    - **TP3 - MV** : Analyse multivariée (PCA, Clustering)
    - **TP4 - ML** : Machine Learning baseline
    - **TP5 - ML2** : ML avancé (tuning, explicabilité)
    
    **Auteur** : Skayne  
    **Date** : 10 février 2026
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS (pour permettre les requêtes depuis un frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routers
app.include_router(dataset.router, prefix="/dataset", tags=["Dataset Generation"])
app.include_router(clean.router, prefix="/clean", tags=["TP1 - Clean"])
app.include_router(eda.router, prefix="/eda", tags=["TP2 - EDA"])
app.include_router(mv.router, prefix="/mv", tags=["TP3 - Multivarié"])
app.include_router(ml.router, prefix="/ml", tags=["TP4 - ML Baseline"])
app.include_router(ml2.router, prefix="/ml2", tags=["TP5 - ML Avancé"])


@app.get("/", tags=["Root"])
def root():
    """
    Endpoint racine - Informations sur l'API
    """
    return {
        "message": "Bienvenue sur l'API FastAPI Data Science !",
        "version": "1.0.0",
        "documentation": "/docs",
        "phases": {
            "TP1": "Clean - Nettoyage des données",
            "TP2": "EDA - Analyse exploratoire",
            "TP3": "MV - Analyse multivariée",
            "TP4": "ML - Machine Learning baseline",
            "TP5": "ML2 - ML avancé"
        },
        "endpoints": {
            "dataset": "/dataset/*",
            "clean": "/clean/*",
            "eda": "/eda/*",
            "mv": "/mv/*",
            "ml": "/ml/*",
            "ml2": "/ml2/*"
        }
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "fastapi-ds-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
