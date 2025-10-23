"""
Parsing utilities - 데이터 전처리 헬퍼 함수
"""
from typing import Dict
from datetime import datetime


def expand_under20(age_groups: Dict[str, float]) -> Dict[str, float]:
    """
    '20대 이하'를 '10대'와 '20대'로 분해 (균등 분할)
    
    Args:
        age_groups: 원본 연령 분포 {"20대 이하": 40.0, "30대": 30.0, ...}
        
    Returns:
        확장된 연령 분포 {"10대": 20.0, "20대": 20.0, "30대": 30.0, ...}
    """
    res = {
        "10대": 0.0,
        "20대": 0.0,
        "30대": 0.0,
        "40대": 0.0,
        "50대": 0.0,
        "60대 이상": 0.0
    }
    
    if not age_groups:
        return res
    
    # 20대 이하를 10대와 20대로 균등 분할
    under20 = float(age_groups.get("20대 이하", 0.0))
    res["10대"] = round(under20 / 2.0, 4)
    res["20대"] = round(under20 / 2.0, 4)
    
    # 나머지 연령대는 그대로 매핑
    for k in ("30대", "40대", "50대", "60대 이상"):
        res[k] = float(age_groups.get(k, 0.0))
    
    return res


def season_from_date(dt_str: str | None) -> str:
    """
    날짜 문자열에서 계절 추출
    
    Args:
        dt_str: 날짜 문자열 (ISO 형식 또는 "YYYY-MM-DD HH:MM:SS")
        
    Returns:
        계절 문자열 ("봄", "여름", "가을", "겨울", "미상")
    """
    if not dt_str:
        return "미상"
    
    try:
        # 먼저 표준 형식 시도
        m = datetime.strptime(dt_str[:19], "%Y-%m-%d %H:%M:%S").month
    except Exception:
        try:
            # ISO 형식 시도
            m = datetime.fromisoformat(dt_str).month
        except Exception:
            return "미상"
    
    # 계절 매핑
    if m in (12, 1, 2):
        return "겨울"
    if m in (3, 4, 5):
        return "봄"
    if m in (6, 7, 8):
        return "여름"
    return "가을"
