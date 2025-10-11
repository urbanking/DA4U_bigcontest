"""
/api/diagnostic/{store_code}
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services import diagnostic_service
from backend.schemas.diagnostic_schema import DiagnosticResponse

router = APIRouter()


@router.get("/{store_code}", response_model=DiagnosticResponse)
async def get_diagnostic(
    store_code: str,
    db: Session = Depends(get_db)
):
    """진단 결과 조회"""
    try:
        result = await diagnostic_service.get_diagnostic(store_code, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{store_code}/diagnose")
async def run_diagnostic(
    store_code: str,
    db: Session = Depends(get_db)
):
    """진단 실행"""
    try:
        result = await diagnostic_service.run_diagnostic(store_code, db)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

