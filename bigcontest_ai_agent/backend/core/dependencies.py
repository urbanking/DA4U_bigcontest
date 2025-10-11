"""
공통 의존성 (Session, Path 등)
"""
from typing import Generator
from sqlalchemy.orm import Session
from backend.core.database import get_db
from pathlib import Path
from backend.core.config import settings


def get_output_path(subdir: str) -> Path:
    """출력 경로 반환"""
    path = Path(settings.OUTPUT_DIR) / subdir
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_config_path(filename: str) -> Path:
    """설정 파일 경로 반환"""
    return Path(settings.CONFIG_DIR) / filename

