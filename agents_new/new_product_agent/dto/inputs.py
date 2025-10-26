"""
DTO Input - StoreAgent 리포트에서 필요한 데이터만 추출
"""
from typing import Dict, Any


def build_new_product_input(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    StoreAgent JSON 리포트에서 NewProductAgent가 필요한 데이터만 추출 및 재구성
    
    Args:
        report: StoreAgent의 전체 JSON 리포트
        
    Returns:
        Dict containing:
            - store_code: 매장 코드
            - analysis_date: 분석 날짜
            - industry: 업종
            - commercial_area: 상권명
            - store_audience: 매장 고객 분포 (성별/연령)
            - industry_avg: 업종 평균 분포 (성별/연령)
            - context: 추가 컨텍스트 (매출 추세, 배달 힌트 등)
    """
    meta = report.get("report_metadata", {})
    ov   = report.get("store_overview", {})
    ca   = report.get("customer_analysis", {})
    ia   = report.get("industry_analysis", {})
    
    # 업종 정보 추출 및 매핑
    industry = ov.get("industry", "")
    
    # StoreAgent에서 소분류로 저장된 업종을 대분류로 매핑
    industry_mapping = {
        "카페": "카페·디저트",
        "디저트": "카페·디저트", 
        "베이커리": "카페·디저트",
        "제과점": "카페·디저트",
        "아이스크림": "카페·디저트"
    }
    
    # 매핑된 업종 사용 (없으면 원본 사용)
    mapped_industry = industry_mapping.get(industry, industry)
    
    # 업종 평균 데이터 집계 (성별/연령)
    seg_ind = ia.get("average_customer_segments", {}) or {}
    
    # 업종 평균 - 성별 집계
    male = sum(seg_ind.get(k, 0) for k in ["남20대이하", "남30대", "남40대", "남50대", "남60대이상"])
    female = sum(seg_ind.get(k, 0) for k in ["여20대이하", "여30대", "여40대", "여50대", "여60대이상"])

    # 업종 평균 - 연령 집계
    ind_age = {
        "20대 이하": seg_ind.get("남20대이하", 0) + seg_ind.get("여20대이하", 0),
        "30대":     seg_ind.get("남30대", 0) + seg_ind.get("여30대", 0),
        "40대":     seg_ind.get("남40대", 0) + seg_ind.get("여40대", 0),
        "50대":     seg_ind.get("남50대", 0) + seg_ind.get("여50대", 0),
        "60대 이상": seg_ind.get("남60대이상", 0) + seg_ind.get("여60대이상", 0),
    }

    # 추가 컨텍스트 (선택적)
    delivery = report.get("sales_analysis", {}).get("delivery_analysis", {}) or {}

    return {
        "store_code": meta.get("store_code"),
        "analysis_date": meta.get("analysis_date"),
        "industry": mapped_industry,
        "commercial_area": ov.get("commercial_area", ""),
        "store_audience": {
            "gender_ratio": {
                "male": ca.get("gender_distribution", {}).get("male_ratio", 0.0),
                "female": ca.get("gender_distribution", {}).get("female_ratio", 0.0),
            },
            "age_groups": ca.get("age_group_distribution", {})
        },
        "industry_avg": {
            "gender_ratio": {"male": round(male, 1), "female": round(female, 1)},
            "age_groups": ind_age
        },
        "context": {
            "sales_trend": report.get("sales_analysis", {}).get("trends", {}).get("sales_amount", {}).get("trend"),
            "delivery_hint": {
                "store_avg": delivery.get("average"), 
                "trend": delivery.get("trend")
            }
        }
    }
