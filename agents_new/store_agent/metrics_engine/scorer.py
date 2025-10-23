"""
표준화, 백분위, 등급 계산
"""
from typing import Dict, Any
import numpy as np


class MetricsScorer:
    """지표 점수화 및 등급화"""
    
    def __init__(self):
        pass
    
    def normalize(self, value: float, min_val: float, max_val: float) -> float:
        """표준화 (0-100)"""
        if max_val == min_val:
            return 50.0
        return ((value - min_val) / (max_val - min_val)) * 100
    
    def get_percentile(self, value: float, distribution: list) -> float:
        """백분위 계산"""
        if not distribution:
            return 50.0
        return np.percentile(distribution, value)
    
    def get_grade(self, score: float) -> str:
        """등급 계산 (A+, A, B+, B, C+, C, D, F)"""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def score_metrics(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """지표 점수화"""
        scored_metrics = {}
        for metric_name, metric_value in metrics.items():
            scored_metrics[metric_name] = {
                "value": metric_value,
                "score": metric_value,  # 이미 0-100 스케일
                "grade": self.get_grade(metric_value)
            }
        return scored_metrics

