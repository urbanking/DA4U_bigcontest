"""
/api/marketing/{store_code}
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services import marketing_service
from backend.schemas.marketing_schema import MarketingResponse

router = APIRouter()


@router.get("/{store_code}", response_model=MarketingResponse)
async def get_marketing_strategy(
    store_code: str,
    db: Session = Depends(get_db)
):
    """마케팅 전략 조회"""
    try:
        result = await marketing_service.get_marketing_strategy(store_code, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{store_code}/generate")
async def generate_marketing_strategy(
    store_code: str,
    db: Session = Depends(get_db)
):
    """마케팅 전략 생성"""
    try:
        result = await marketing_service.generate_marketing_strategy(store_code, db)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

