"""
MetricsEngine 실행
"""
from sqlalchemy.orm import Session
from backend.core.logger import logger


async def get_metrics(store_code: str, db: Session):
    """지표 조회"""
    logger.info(f"Getting metrics for: {store_code}")
    # TODO: 지표 조회 로직 구현
    return {"store_code": store_code, "metrics": {}}


async def calculate_metrics(store_code: str, db: Session):
    """지표 계산"""
    logger.info(f"Calculating metrics for: {store_code}")
    # TODO: 지표 계산 로직 구현
    return {"store_code": store_code, "metrics": {}}

