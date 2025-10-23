"""
결과 저장 → store_metrics.json
"""
from typing import Dict, Any
import json
from pathlib import Path


class MetricsComposer:
    """지표 결과 작성"""
    
    def __init__(self, output_dir: str = "outputs/metrics"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def compose(self, store_code: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """지표 결과 작성"""
        result = {
            "store_code": store_code,
            "metrics": metrics,
            "overall_score": self._calculate_overall_score(metrics)
        }
        return result
    
    def _calculate_overall_score(self, metrics: Dict[str, Any]) -> float:
        """종합 점수 계산"""
        scores = [m.get("score", 0) for m in metrics.values()]
        if not scores:
            return 0.0
        return sum(scores) / len(scores)
    
    def save(self, store_code: str, metrics_result: Dict[str, Any]):
        """JSON 파일로 저장"""
        filepath = self.output_dir / f"store_metrics_{store_code}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metrics_result, f, ensure_ascii=False, indent=2)

