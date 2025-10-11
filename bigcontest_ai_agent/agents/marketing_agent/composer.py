"""
결과 병합 → marketing_strategy_report.json
"""
from typing import Dict, Any
import json
from pathlib import Path


class MarketingComposer:
    """마케팅 전략 결과 작성"""
    
    def __init__(self, output_dir: str = "outputs/marketing"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def compose(
        self,
        store_code: str,
        insights: Dict[str, Any],
        target_segments: List[Dict[str, Any]],
        strategies: List[Dict[str, Any]],
        kpi_estimates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """마케팅 전략 리포트 작성"""
        result = {
            "store_code": store_code,
            "insights": insights,
            "target_segments": target_segments,
            "strategies": strategies,
            "kpi_estimates": kpi_estimates,
            "recommendations": self._generate_recommendations(strategies, kpi_estimates)
        }
        
        return result
    
    def _generate_recommendations(
        self,
        strategies: List[Dict[str, Any]],
        kpi_estimates: Dict[str, Any]
    ) -> List[str]:
        """권고사항 생성"""
        recommendations = []
        
        # TODO: KPI 기반 권고사항 생성
        
        return recommendations
    
    def save(self, store_code: str, marketing_result: Dict[str, Any]):
        """JSON 파일로 저장"""
        filepath = self.output_dir / f"marketing_strategy_report_{store_code}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(marketing_result, f, ensure_ascii=False, indent=2)

