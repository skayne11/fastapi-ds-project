from fastapi import APIRouter, HTTPException
from app.schemas.common import DatasetGenerateRequest, DatasetGenerateResponse, MetaData
from app.services.dataset_generator import DatasetGenerator

router = APIRouter()


def safe_dataframe(df, n=20):
    """
    Convertit un dataframe en JSON-safe dict (max n lignes)
    - remplace NaN par "NA"
    - remplace inf/-inf par 0
    - convertit tout en str
    """
    sample = df.head(n).copy()
    sample = sample.fillna("NA")
    sample = sample.replace([float("inf"), float("-inf")], 0)
    return sample.astype(str).to_dict(orient="records")


@router.post("/generate", response_model=DatasetGenerateResponse)
def generate_dataset(request: DatasetGenerateRequest):
    """
    Génère un dataset pour une phase donnée
    
    - **phase** : Phase du projet (clean, eda, mv, ml, ml2)
    - **seed** : Graine aléatoire pour reproductibilité
    - **n** : Nombre de lignes du dataset
    """
    try:
        # Générer le dataset
        dataset_id, df = DatasetGenerator.generate(
            phase=request.phase,
            seed=request.seed,
            n=request.n
        )
        
        # Préparer la réponse
        meta = MetaData(
            dataset_id=dataset_id,
            schema_version="1.0"
        )
        
        result = {
            "columns": df.columns.tolist(),
            "n_rows": len(df),
            "n_cols": len(df.columns),
            "data_sample": safe_dataframe(df, n=20),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        return DatasetGenerateResponse(
            meta=meta,
            result=result
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
