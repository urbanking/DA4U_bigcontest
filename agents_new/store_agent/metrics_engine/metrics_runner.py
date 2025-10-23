"""
Report 입력 → Metrics 실행기
"""
from typing import Dict, Any
from .calculators import MetricsCalculator
from .scorer import MetricsScorer
from .composer import MetricsComposer


class MetricsRunner:
    """지표 실행기"""
    
    def __init__(self):
        self.calculator = MetricsCalculator()
        self.scorer = MetricsScorer()
        self.composer = MetricsComposer()
    
    async def run(self, store_code: str, report: Dict[str, Any]) -> Dict[str, Any]:
        """지표 계산 전체 실행"""
        # 1. 지표 계산
        metrics = self.calculator.calculate_all(report)
        
        # 2. 점수화 및 등급화
        scored_metrics = self.scorer.score_metrics(metrics)
        
        # 3. 결과 작성
        result = self.composer.compose(store_code, scored_metrics)
        
        # 4. 저장
        self.composer.save(store_code, result)
        
        return result

