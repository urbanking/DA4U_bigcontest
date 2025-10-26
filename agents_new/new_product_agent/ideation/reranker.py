"""
Reranker - 최소 검증 (필수 슬롯만 확인)
가격/채널 등은 스키마에 없으므로 검증 대상 아님
"""
from typing import List, Dict, Any


def validate_minimal(proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    LLM이 생성한 제안 리스트를 최소 검증
    
    검증 항목:
    1. 필수 슬롯 존재 여부 (menu_name, category, target, evidence, template_ko)
    2. 중복 메뉴명 제거
    3. 최대 Top5만 유지
    
    Args:
        proposals: LLM이 생성한 제안 리스트
        
    Returns:
        검증된 제안 리스트 (최대 5개)
    """
    ok = []
    seen = set()
    must_have = ["menu_name", "category", "target", "evidence", "template_ko"]
    
    for p in proposals:
        # 1) dict 타입 확인
        if not isinstance(p, dict):
            continue
        
        # 2) 필수 슬롯 확인
        if not all(k in p for k in must_have):
            continue
        
        # 3) 중복 제거 (메뉴명 기준)
        key = p["menu_name"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        
        ok.append(p)
    
    # 4) 최대 5개만 반환
    return ok[:5]
