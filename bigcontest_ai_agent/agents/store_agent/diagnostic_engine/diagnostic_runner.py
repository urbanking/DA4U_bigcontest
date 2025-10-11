"""
Metrics 입력 → Diagnostic 실행기
"""
from typing import Dict, Any
from .rules import RuleEngine
from .explanations import ExplanationGenerator
from .recommender import Recommender
from .composer import DiagnosticComposer


class DiagnosticRunner:
    """진단 실행기"""
    
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.explanation_generator = ExplanationGenerator()
        self.recommender = Recommender()
        self.composer = DiagnosticComposer()
    
    async def run(self, store_code: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """진단 전체 실행"""
        # 1. 규칙 평가
        triggered_rules = self.rule_engine.evaluate(metrics)
        
        # 2. 설명 생성
        explanations = []
        for rule in triggered_rules:
            metric_data = metrics.get(rule.metric_name, {})
            value = metric_data.get("value", 0)
            explanation = self.explanation_generator.generate(rule.rule_name, value)
            explanations.append(explanation)
        
        # 3. 권고사항 생성
        recommendations = self.recommender.generate_recommendations(triggered_rules)
        prioritized_recs = self.recommender.prioritize_recommendations(recommendations, metrics)
        
        # 4. 결과 작성
        result = self.composer.compose(
            store_code,
            triggered_rules,
            explanations,
            prioritized_recs
        )
        
        # 5. 저장
        self.composer.save(store_code, result)
        
        return result

