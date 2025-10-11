"""
LangGraph Orchestrator 실행
"""
from sqlalchemy.orm import Session
from backend.core.logger import logger


async def run_full_pipeline(store_code: str, db: Session):
    """전체 파이프라인 실행"""
    logger.info(f"Running full pipeline for store: {store_code}")
    # TODO: LangGraph 오케스트레이터 실행 로직 구현
    return {"store_code": store_code, "status": "completed"}


async def get_pipeline_status(store_code: str, db: Session):
    """파이프라인 상태 조회"""
    logger.info(f"Getting pipeline status for store: {store_code}")
    # TODO: 파이프라인 상태 조회 로직 구현
    return {"store_code": store_code, "status": "idle"}

