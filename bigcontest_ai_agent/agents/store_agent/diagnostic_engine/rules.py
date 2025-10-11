"""
경고/임계값 조건
"""
from typing import Dict, Any, List
from pydantic import BaseModel


class DiagnosticRule(BaseModel):
    """진단 규칙"""
    rule_name: str
    metric_name: str
    condition: str  # 'below', 'above', 'between'
    threshold: float
    threshold_max: float = None
    severity: str  # 'critical', 'warning', 'info'
    message: str


# 진단 규칙 정의
DIAGNOSTIC_RULES = [
    DiagnosticRule(
        rule_name="low_cvi",
        metric_name="cvi",
        condition="below",
        threshold=60.0,
        severity="warning",
        message="상권 활성도가 낮습니다"
    ),
    DiagnosticRule(
        rule_name="critical_cvi",
        metric_name="cvi",
        condition="below",
        threshold=40.0,
        severity="critical",
        message="상권 활성도가 매우 낮습니다"
    ),
    DiagnosticRule(
        rule_name="low_asi",
        metric_name="asi",
        condition="below",
        threshold=60.0,
        severity="warning",
        message="접근성이 낮습니다"
    ),
    DiagnosticRule(
        rule_name="low_sci",
        metric_name="sci",
        condition="below",
        threshold=60.0,
        severity="warning",
        message="점포 경쟁력이 낮습니다"
    )
]


class RuleEngine:
    """규칙 엔진"""
    
    def __init__(self):
        self.rules = DIAGNOSTIC_RULES
    
    def evaluate(self, metrics: Dict[str, Any]) -> List[DiagnosticRule]:
        """규칙 평가"""
        triggered_rules = []
        
        for rule in self.rules:
            metric_data = metrics.get(rule.metric_name, {})
            value = metric_data.get("value", 0)
            
            if self._check_condition(value, rule):
                triggered_rules.append(rule)
        
        return triggered_rules
    
    def _check_condition(self, value: float, rule: DiagnosticRule) -> bool:
        """조건 체크"""
        if rule.condition == "below":
            return value < rule.threshold
        elif rule.condition == "above":
            return value > rule.threshold
        elif rule.condition == "between":
            return rule.threshold <= value <= rule.threshold_max
        return False

