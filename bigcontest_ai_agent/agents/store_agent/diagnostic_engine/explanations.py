"""
해석/인과 설명 템플릿
"""
from typing import Dict, Any


class ExplanationGenerator:
    """설명 생성기"""
    
    def __init__(self):
        self.templates = {
            "low_cvi": "상권 활성도(CVI)가 {value:.1f}점으로 낮습니다. 이는 주변 상권의 유동인구나 매출 규모가 작음을 의미합니다.",
            "critical_cvi": "상권 활성도(CVI)가 {value:.1f}점으로 매우 낮습니다. 위치 변경을 고려해야 할 수준입니다.",
            "low_asi": "접근성(ASI)이 {value:.1f}점으로 낮습니다. 대중교통 접근성이나 주차 편의성 개선이 필요합니다.",
            "low_sci": "점포 경쟁력(SCI)이 {value:.1f}점으로 낮습니다. 경쟁업체 대비 차별화 전략이 필요합니다."
        }
    
    def generate(self, rule_name: str, value: float) -> str:
        """설명 생성"""
        template = self.templates.get(rule_name, "지표에 문제가 있습니다.")
        return template.format(value=value)
    
    def generate_causal_explanation(self, metrics: Dict[str, Any]) -> str:
        """인과 설명 생성"""
        # TODO: LLM을 사용한 인과 설명 생성
        return "지표 간 인과관계 분석 결과 placeholder"

