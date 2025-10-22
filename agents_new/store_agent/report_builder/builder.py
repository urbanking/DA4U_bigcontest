"""
통합 리포트 빌더 → store_report.json
"""
from typing import Dict, Any
from .commercial_agent import CommercialAgent
from .industry_agent import IndustryAgent
from .accessibility_agent import AccessibilityAgent
from .mobility_agent import MobilityAgent
from .summarizer import Summarizer


class ReportBuilder:
    """리포트 통합 빌더"""
    
    def __init__(self, store_code: str):
        self.store_code = store_code
        self.commercial_agent = CommercialAgent(store_code)
        self.industry_agent = IndustryAgent(store_code)
        self.accessibility_agent = AccessibilityAgent(store_code)
        self.mobility_agent = MobilityAgent(store_code)
        self.summarizer = Summarizer()
    
    async def build(self) -> Dict[str, Any]:
        """전체 리포트 생성"""
        # 각 에이전트 실행
        commercial = await self.commercial_agent.analyze()
        industry = await self.industry_agent.analyze()
        accessibility = await self.accessibility_agent.analyze()
        mobility = await self.mobility_agent.analyze()
        
        # 리포트 통합
        report_data = {
            "store_code": self.store_code,
            "commercial": commercial,
            "industry": industry,
            "accessibility": accessibility,
            "mobility": mobility
        }
        
        # 자연어 요약 생성
        summary = await self.summarizer.summarize(report_data)
        report_data["summary"] = summary
        
        return report_data

