"""
/api/metrics/{store_code}
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services import metrics_service
from backend.schemas.metrics_schema import MetricsResponse

router = APIRouter()


@router.get("/{store_code}", response_model=MetricsResponse)
async def get_metrics(
    store_code: str,
    db: Session = Depends(get_db)
):
    """지표 조회"""
    try:
        result = await metrics_service.get_metrics(store_code, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{store_code}/calculate")
async def calculate_metrics(
    store_code: str,
    db: Session = Depends(get_db)
):
    """지표 계산"""
    try:
        result = await metrics_service.calculate_metrics(store_code, db)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

