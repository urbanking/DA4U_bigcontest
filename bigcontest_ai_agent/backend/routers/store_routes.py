"""
/api/store/{store_code}
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services import report_service
from backend.schemas.store_schema import StoreReportResponse

router = APIRouter()


@router.get("/{store_code}", response_model=StoreReportResponse)
async def get_store_report(
    store_code: str,
    db: Session = Depends(get_db)
):
    """가게 리포트 조회"""
    try:
        result = await report_service.get_store_report(store_code, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{store_code}/generate")
async def generate_store_report(
    store_code: str,
    db: Session = Depends(get_db)
):
    """가게 리포트 생성"""
    try:
        result = await report_service.generate_store_report(store_code, db)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

