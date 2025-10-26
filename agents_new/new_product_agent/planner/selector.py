"""
Selector - 성별/연령 타깃 선정 및 카테고리 선택 로직
"""
from typing import List, Tuple, Optional
from .rules import ALLOWED_INDUSTRIES, CATEGORY_MAP


def should_activate(industry: str) -> bool:
    """
    업종이 화이트리스트에 있는지 확인하여 Agent 활성화 여부 결정
    
    Args:
        industry: 업종명
        
    Returns:
        True if 활성화 대상 업종
    """
    return (industry or "").strip() in ALLOWED_INDUSTRIES


def select_categories(industry: str) -> List[str]:
    """
    업종에 따른 네이버 데이터랩 카테고리 선택
    
    Args:
        industry: 업종명
        
    Returns:
        데이터랩 카테고리 리스트 (예: ["농산물", "음료"])
    """
    key = (industry or "").strip()
    return CATEGORY_MAP.get(key, [])


def choose_gender(
    store_male: float, 
    store_female: float, 
    ind_male: float, 
    ind_female: float
) -> Tuple[str, Optional[str]]:
    """
    성별 타깃 선정 (업종 평균 대비 비교)
    
    규칙:
    1. 우세 성별: 한 성별이 55% 이상이면 해당 성별 선택
    2. 리프트 우세: 업종 대비 +5%p 이상 차이 나는 성별 선택
    3. 균형형: 위 조건 미충족 시 '전체' 선택
    4. 보너스: 주요 성별 반대편이 +10%p 이상이면 추가 고려
    
    Args:
        store_male: 매장 남성 비율 (%)
        store_female: 매장 여성 비율 (%)
        ind_male: 업종 평균 남성 비율 (%)
        ind_female: 업종 평균 여성 비율 (%)
        
    Returns:
        (주요 성별, 보너스 성별 또는 None)
        예: ("남성", None) 또는 ("여성", "남성") 또는 ("전체", None)
    """
    lifts = {
        "male": store_male - ind_male, 
        "female": store_female - ind_female
    }
    
    # 1) 우세 성별 (55% 이상)
    if store_male >= 55 or store_female >= 55:
        gender = "남성" if store_male >= store_female else "여성"
        # 보너스: 반대 성별도 +10%p 이상이면 추가
        bonus = "여성" if (gender == "남성" and lifts["female"] >= 10) else \
                "남성" if (gender == "여성" and lifts["male"] >= 10) else None
        return gender, bonus
    
    # 2) 리프트 우세 (+5%p 이상)
    for g in ("male", "female"):
        if lifts[g] >= 5:
            return ("남성" if g == "male" else "여성"), None
    
    # 3) 균형형
    return "전체", None


def choose_ages(store_age_expanded: dict, ind_age_expanded: dict) -> List[str]:
    """
    연령 타깃 선정 (최대 3칸, 커버리지 ≥ 50%)
    
    규칙:
    1. 비율 내림차순 + 동률 시 lift 큰 순으로 정렬
    2. 상위에서 누적 50% 달성까지 선택 (최대 3칸)
    3. 청년쏠림 보정: 10대+20대 ≥ 40%면 둘 다 포함
    4. 장년쏠림 보정: 50대+60대 이상 ≥ 40%면 둘 다 포함
    
    Args:
        store_age_expanded: 매장 연령 분포 {"10대":x, "20대":y, ...}
        ind_age_expanded: 업종 평균 연령 분포
        
    Returns:
        선택된 연령대 리스트 (최대 3개)
    """
    # Lift 계산
    lifts = {
        k: store_age_expanded.get(k, 0) - ind_age_expanded.get(k, 0) 
        for k in store_age_expanded
    }
    
    # 1) 비율 내림차순, 동률 시 lift 큰 순
    order = sorted(
        store_age_expanded.keys(), 
        key=lambda k: (store_age_expanded[k], lifts[k]), 
        reverse=True
    )
    
    # 2) 상위에서 누적 50% 달성까지 (최대 3칸)
    pick, cum = [], 0.0
    for a in order:
        if len(pick) == 3:
            break
        pick.append(a)
        cum += store_age_expanded[a]
        if cum >= 50.0:
            break
    
    # 3) 청년쏠림 보정
    youth_sum = store_age_expanded.get("10대", 0) + store_age_expanded.get("20대", 0)
    if youth_sum >= 40.0:
        for a in ("10대", "20대"):
            if a not in pick and len(pick) < 3:
                pick.append(a)
    
    # 4) 장년쏠림 보정
    senior_sum = store_age_expanded.get("50대", 0) + store_age_expanded.get("60대 이상", 0)
    if senior_sum >= 40.0:
        for a in ("50대", "60대 이상"):
            if a not in pick and len(pick) < 3:
                pick.append(a)
    
    return pick


def to_datalab_age_checks(selected_ages: List[str]) -> List[str]:
    """
    선택된 연령대를 네이버 데이터랩 체크박스 형식으로 변환
    
    '20대 이하'가 선택되었다면 → '10대' + '20대' 두 칸으로 분해
    
    Args:
        selected_ages: choose_ages에서 반환된 연령 리스트
        
    Returns:
        데이터랩에 체크할 연령 리스트 (최대 3칸)
    """
    checks: List[str] = []
    
    for a in selected_ages:
        if a in ("20대 이하", "10대", "20대"):
            # 20대 이하는 10대+20대로 분해
            for b in ("10대", "20대"):
                if b not in checks and len(checks) < 3:
                    checks.append(b)
        else:
            if a not in checks and len(checks) < 3:
                checks.append(a)
    
    return checks[:3]
