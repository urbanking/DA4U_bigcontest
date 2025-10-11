"""
/api/run/{store_code}
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services import orchestrator_service

router = APIRouter()


@router.post("/{store_code}")
async def run_full_pipeline(
    store_code: str,
    db: Session = Depends(get_db)
):
    """전체 파이프라인 실행 (Store Report → Metrics → Diagnostic → Marketing)"""
    try:
        result = await orchestrator_service.run_full_pipeline(store_code, db)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{store_code}/status")
async def get_pipeline_status(
    store_code: str,
    db: Session = Depends(get_db)
):
    """파이프라인 실행 상태 조회"""
    try:
        result = await orchestrator_service.get_pipeline_status(store_code, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

