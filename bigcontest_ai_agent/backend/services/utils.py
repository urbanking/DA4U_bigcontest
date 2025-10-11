"""
공통 유틸 (파일 I/O, 포맷터 등)
"""
import json
from pathlib import Path
from typing import Any, Dict


def save_json(data: Dict[str, Any], filepath: Path):
    """JSON 파일 저장"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(filepath: Path) -> Dict[str, Any]:
    """JSON 파일 로드"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_number(value: float, decimals: int = 2) -> str:
    """숫자 포맷팅"""
    return f"{value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """퍼센트 포맷팅"""
    return f"{value:.{decimals}f}%"

