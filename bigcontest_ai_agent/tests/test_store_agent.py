"""
Store Agent 테스트
"""
import pytest
from agents.store_agent.store_agent import StoreAgent


class TestStoreAgent:
    """StoreAgent 테스트 클래스"""
    
    @pytest.fixture
    def store_agent(self):
        """StoreAgent 픽스처"""
        return StoreAgent("TEST_STORE_001")
    
    @pytest.mark.asyncio
    async def test_run_report(self, store_agent):
        """리포트 생성 테스트"""
        result = await store_agent.run_report()
        
        assert result is not None
        assert "store_code" in result
        assert result["store_code"] == "TEST_STORE_001"
    
    @pytest.mark.asyncio
    async def test_run_metrics(self, store_agent):
        """지표 계산 테스트"""
        report = {"store_code": "TEST_STORE_001", "report": {}}
        result = await store_agent.run_metrics(report)
        
        assert result is not None
        assert "store_code" in result
        assert "metrics" in result
    
    @pytest.mark.asyncio
    async def test_run_diagnostic(self, store_agent):
        """진단 실행 테스트"""
        metrics = {"store_code": "TEST_STORE_001", "metrics": {}}
        result = await store_agent.run_diagnostic(metrics)
        
        assert result is not None
        assert "store_code" in result
        assert "diagnostic" in result
    
    @pytest.mark.asyncio
    async def test_run_all(self, store_agent):
        """전체 실행 테스트"""
        result = await store_agent.run_all()
        
        assert result is not None
        assert "store_code" in result
        assert "report" in result
        assert "metrics" in result
        assert "diagnostic" in result

