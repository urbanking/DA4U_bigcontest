"""
개선 권고 로직
"""
from typing import List, Dict, Any
from .rules import DiagnosticRule


class Recommender:
    """개선 권고 생성기"""
    
    def __init__(self):
        self.recommendations = {
            "low_cvi": [
                "더 활성화된 상권으로 이전 검토",
                "온라인 마케팅을 통한 고객 유입 증대",
                "인근 오피스/주거지역 대상 프로모션 강화"
            ],
            "critical_cvi": [
                "즉시 입지 재평가 및 이전 검토 필요",
                "배달/온라인 채널로 사업 모델 전환 고려"
            ],
            "low_asi": [
                "주차 공간 확보 또는 주차 제휴 서비스 제공",
                "대중교통 이용 고객 대상 할인 프로모션",
                "배달 서비스 강화로 접근성 한계 극복"
            ],
            "low_sci": [
                "차별화된 메뉴/상품 개발",
                "고객 서비스 품질 개선",
                "브랜드 아이덴티티 강화",
                "가격 경쟁력 재검토"
            ]
        }
    
    def generate_recommendations(self, triggered_rules: List[DiagnosticRule]) -> List[str]:
        """권고사항 생성"""
        all_recommendations = []
        
        for rule in triggered_rules:
            recs = self.recommendations.get(rule.rule_name, [])
            all_recommendations.extend(recs)
        
        # 중복 제거
        return list(set(all_recommendations))
    
    def prioritize_recommendations(self, recommendations: List[str], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """권고사항 우선순위화"""
        # TODO: 지표 기반 권고사항 우선순위 로직 구현
        return [
            {
                "recommendation": rec,
                "priority": "high",
                "impact": "medium"
            }
            for rec in recommendations
        ]

