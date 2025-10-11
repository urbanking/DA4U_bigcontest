"""
Store Report 실행 모듈
"""
from sqlalchemy.orm import Session
from backend.core.logger import logger


async def get_store_report(store_code: str, db: Session):
    """가게 리포트 조회"""
    logger.info(f"Getting store report for: {store_code}")
    # TODO: 가게 리포트 조회 로직 구현
    return {"store_code": store_code, "report": {}}


async def generate_store_report(store_code: str, db: Session):
    """가게 리포트 생성"""
    logger.info(f"Generating store report for: {store_code}")
    # TODO: 가게 리포트 생성 로직 구현
    return {"store_code": store_code, "report": {}}

