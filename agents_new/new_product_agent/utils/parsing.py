"""
Parsing utilities - 데이터 전처리 헬퍼 함수
"""
from typing import Dict
from datetime import datetime


def expand_under20(age_groups: Dict[str, float]) -> Dict[str, float]:
    """
    '20대 이하'를 네이버 데이터랩 형식으로 변환
    
    실제 분포 데이터를 유지하며, "20대 이하"는 "20대 이하"로 그대로 유지
    (크롤링 시 to_datalab_age_checks()에서 "10대"+"20대" 체크박스 선택)
    
    Args:
        age_groups: 원본 연령 분포 {"20대 이하": 23.2, "30대": 31.1, ...}
        
    Returns:
        확장된 연령 분포 {"10대": 0.0, "20대": 0.0, "20대 이하": 23.2, "30대": 31.1, ...}
    """
    res = {
        "10대": 0.0,
        "20대": 0.0,
        "20대 이하": 0.0,
        "30대": 0.0,
        "40대": 0.0,
        "50대": 0.0,
        "60대 이상": 0.0
    }
    
    if not age_groups:
        return res
    
    # 20대 이하는 그대로 유지 (실제 데이터 유지)
    under20 = float(age_groups.get("20대 이하", 0.0))
    res["20대 이하"] = under20  # 전체 비율을 20대 이하에 할당
    res["10대"] = 0.0          # 10대는 별도 데이터 없음
    res["20대"] = 0.0          # 20대는 별도 데이터 없음
    
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
