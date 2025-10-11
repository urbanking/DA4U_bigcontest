"""
Marketing Agent 테스트
"""
import pytest
from agents.marketing_agent.marketing_agent import MarketingAgent
from agents.marketing_agent.insight_extractor import InsightExtractor
from agents.marketing_agent.target_matcher import TargetMatcher
from agents.marketing_agent.strategy_generator import StrategyGenerator
from agents.marketing_agent.kpi_estimator import KPIEstimator


class TestMarketingAgent:
    """MarketingAgent 테스트 클래스"""
    
    @pytest.fixture
    def marketing_agent(self):
        """MarketingAgent 픽스처"""
        return MarketingAgent("TEST_STORE_001")
    
    @pytest.mark.asyncio
    async def test_run_marketing(self, marketing_agent):
        """마케팅 전략 생성 테스트"""
        store_report = {
            "store_code": "TEST_STORE_001",
            "commercial": {},
            "industry": {}
        }
        diagnostic = {
            "store_code": "TEST_STORE_001",
            "issues": [],
            "recommendations": []
        }
        
        result = await marketing_agent.run_marketing(store_report, diagnostic)
        
        assert result is not None
        assert "store_code" in result
        assert "strategies" in result
        assert "target_segments" in result
        assert "kpi_estimates" in result


class TestInsightExtractor:
    """InsightExtractor 테스트 클래스"""
    
    @pytest.fixture
    def extractor(self):
        """Extractor 픽스처"""
        return InsightExtractor()
    
    @pytest.mark.asyncio
    async def test_extract_from_report(self, extractor):
        """리포트 인사이트 추출 테스트"""
        report = {
            "commercial": {},
            "industry": {},
            "accessibility": {}
        }
        
        result = await extractor.extract_from_report(report)
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_extract_from_diagnostic(self, extractor):
        """진단 인사이트 추출 테스트"""
        diagnostic = {
            "issues": [],
            "recommendations": []
        }
        
        result = await extractor.extract_from_diagnostic(diagnostic)
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_synthesize_insights(self, extractor):
        """인사이트 종합 테스트"""
        report_insights = []
        diagnostic_insights = []
        
        result = await extractor.synthesize_insights(report_insights, diagnostic_insights)
        
        assert isinstance(result, dict)
        assert "strengths" in result
        assert "weaknesses" in result
        assert "opportunities" in result
        assert "threats" in result


class TestTargetMatcher:
    """TargetMatcher 테스트 클래스"""
    
    @pytest.fixture
    def matcher(self):
        """Matcher 픽스처"""
        return TargetMatcher()
    
    @pytest.mark.asyncio
    async def test_identify_target_segments(self, matcher):
        """타깃 세그먼트 식별 테스트"""
        insights = {"strengths": [], "opportunities": []}
        customer_data = {}
        
        result = await matcher.identify_target_segments(insights, customer_data)
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_match_customers(self, matcher):
        """고객 매칭 테스트"""
        segments = [{"name": "Segment1"}]
        customer_db = []
        
        result = await matcher.match_customers(segments, customer_db)
        assert isinstance(result, dict)


class TestStrategyGenerator:
    """StrategyGenerator 테스트 클래스"""
    
    @pytest.fixture
    def generator(self):
        """Generator 픽스처"""
        return StrategyGenerator()
    
    @pytest.mark.asyncio
    async def test_generate_strategies(self, generator):
        """전략 생성 테스트"""
        insights = {"opportunities": []}
        target_segments = []
        
        result = await generator.generate_strategies(insights, target_segments)
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_generate_campaign_plan(self, generator):
        """캠페인 계획 생성 테스트"""
        strategies = []
        
        result = await generator.generate_campaign_plan(strategies)
        
        assert isinstance(result, dict)
        assert "campaign_name" in result
        assert "timeline" in result


class TestKPIEstimator:
    """KPIEstimator 테스트 클래스"""
    
    @pytest.fixture
    def estimator(self):
        """Estimator 픽스처"""
        return KPIEstimator()
    
    @pytest.mark.asyncio
    async def test_estimate_reach(self, estimator):
        """도달 범위 예측 테스트"""
        strategy = {"name": "Test Strategy"}
        target_segments = []
        
        result = await estimator.estimate_reach(strategy, target_segments)
        
        assert isinstance(result, dict)
        assert "total_reach" in result
        assert "reach_rate" in result
    
    @pytest.mark.asyncio
    async def test_estimate_roi(self, estimator):
        """ROI 예측 테스트"""
        strategy = {"name": "Test Strategy"}
        budget = 1000000.0
        
        result = await estimator.estimate_roi(strategy, budget)
        
        assert isinstance(result, dict)
        assert "estimated_revenue" in result
        assert "estimated_roi" in result
    
    @pytest.mark.asyncio
    async def test_estimate_all_kpis(self, estimator):
        """전체 KPI 예측 테스트"""
        strategies = [{"name": "Strategy1", "budget": 1000000}]
        context = {"target_segments": [], "historical_data": {}}
        
        result = await estimator.estimate_all_kpis(strategies, context)
        
        assert isinstance(result, dict)

