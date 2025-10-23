"""
store_diagnostic.json 생성
"""
from typing import Dict, Any, List
import json
from pathlib import Path


class DiagnosticComposer:
    """진단 결과 작성"""
    
    def __init__(self, output_dir: str = "outputs/diagnostics"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def compose(
        self,
        store_code: str,
        triggered_rules: List,
        explanations: List[str],
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """진단 결과 작성"""
        issues = []
        for rule, explanation in zip(triggered_rules, explanations):
            issues.append({
                "issue_type": rule.rule_name,
                "severity": rule.severity,
                "description": explanation,
                "metric": rule.metric_name
            })
        
        result = {
            "store_code": store_code,
            "issues": issues,
            "recommendations": recommendations,
            "overall_health": self._calculate_health(triggered_rules)
        }
        
        return result
    
    def _calculate_health(self, triggered_rules: List) -> str:
        """전체 건강도 계산"""
        if not triggered_rules:
            return "healthy"
        
        critical_count = sum(1 for r in triggered_rules if r.severity == "critical")
        warning_count = sum(1 for r in triggered_rules if r.severity == "warning")
        
        if critical_count > 0:
            return "critical"
        elif warning_count > 2:
            return "warning"
        elif warning_count > 0:
            return "attention_needed"
        else:
            return "healthy"
    
    def save(self, store_code: str, diagnostic_result: Dict[str, Any]):
        """JSON 파일로 저장"""
        filepath = self.output_dir / f"store_diagnostic_{store_code}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(diagnostic_result, f, ensure_ascii=False, indent=2)

