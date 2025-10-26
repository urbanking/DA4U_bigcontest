"""
DTO Output - 최종 응답 JSON 구조 조립
"""
from typing import List, Dict, Any, Optional


def assemble_output(
    store_code: str,
    activated: bool,
    audience: Dict[str, Any],
    categories: List[str],
    keywords: List[Dict[str, Any]],
    insight: Optional[Dict[str, Any]] = None,
    proposals: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    NewProductAgent의 최종 응답 JSON 조립
    
    Args:
        store_code: 매장 코드
        activated: Agent 활성화 여부
        audience: 선택된 타깃 정보 (성별/연령)
        categories: 사용된 데이터랩 카테고리
        keywords: 크롤링된 Top10 키워드 리스트
        insight: LLM이 생성한 인사이트 (선택)
        proposals: LLM이 생성한 제안 리스트 (선택)
        
    Returns:
        Dict containing:
            - store_code: 매장 코드
            - activated: Agent 활성화 여부
            - audience_filters: 선택된 타깃 정보
            - used_categories: 사용된 카테고리
            - keywords_top: 크롤링 키워드
            - insight: 인사이트 객체
            - proposals: 제안 리스트
    """
    return {
        "store_code": store_code,
        "activated": activated,
        "audience_filters": audience,      # {"gender":"남성|여성|전체", "ages":[...], "store_age": {...}}
        "used_categories": categories,     # ["농산물","음료",...]
        "keywords_top": keywords,          # [{"category":"음료","rank":1,"keyword":"..."}, ...]
        "insight": insight or {},
        "proposals": proposals or []
    }
