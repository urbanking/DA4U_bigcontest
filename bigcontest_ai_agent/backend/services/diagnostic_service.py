"""
DiagnosticEngine 실행
"""
from sqlalchemy.orm import Session
from backend.core.logger import logger


async def get_diagnostic(store_code: str, db: Session):
    """진단 결과 조회"""
    logger.info(f"Getting diagnostic for: {store_code}")
    # TODO: 진단 결과 조회 로직 구현
    return {"store_code": store_code, "diagnostic": {}}


async def run_diagnostic(store_code: str, db: Session):
    """진단 실행"""
    logger.info(f"Running diagnostic for: {store_code}")
    # TODO: 진단 실행 로직 구현
    return {"store_code": store_code, "diagnostic": {}}

