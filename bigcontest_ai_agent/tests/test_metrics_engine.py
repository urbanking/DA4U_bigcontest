"""
Metrics Engine 테스트
"""
import pytest
from agents.store_agent.metrics_engine.calculators import MetricsCalculator
from agents.store_agent.metrics_engine.scorer import MetricsScorer
from agents.store_agent.metrics_engine.metrics_runner import MetricsRunner


class TestMetricsCalculator:
    """MetricsCalculator 테스트 클래스"""
    
    @pytest.fixture
    def calculator(self):
        """Calculator 픽스처"""
        return MetricsCalculator()
    
    def test_calculate_cvi(self, calculator):
        """CVI 계산 테스트"""
        report = {"commercial": {}, "industry": {}}
        result = calculator.calculate_cvi(report)
        
        assert isinstance(result, float)
        assert 0 <= result <= 100
    
    def test_calculate_asi(self, calculator):
        """ASI 계산 테스트"""
        report = {"accessibility": {}}
        result = calculator.calculate_asi(report)
        
        assert isinstance(result, float)
        assert 0 <= result <= 100
    
    def test_calculate_all(self, calculator):
        """전체 지표 계산 테스트"""
        report = {
            "commercial": {},
            "industry": {},
            "accessibility": {},
            "mobility": {}
        }
        result = calculator.calculate_all(report)
        
        assert isinstance(result, dict)
        assert "cvi" in result
        assert "asi" in result
        assert "sci" in result
        assert "gmi" in result


class TestMetricsScorer:
    """MetricsScorer 테스트 클래스"""
    
    @pytest.fixture
    def scorer(self):
        """Scorer 픽스처"""
        return MetricsScorer()
    
    def test_normalize(self, scorer):
        """표준화 테스트"""
        result = scorer.normalize(50, 0, 100)
        assert result == 50.0
        
        result = scorer.normalize(75, 0, 100)
        assert result == 75.0
    
    def test_get_grade(self, scorer):
        """등급 계산 테스트"""
        assert scorer.get_grade(95) == "A+"
        assert scorer.get_grade(85) == "B+"
        assert scorer.get_grade(75) == "C+"
        assert scorer.get_grade(50) == "F"
    
    def test_score_metrics(self, scorer):
        """지표 점수화 테스트"""
        metrics = {
            "cvi": 75.0,
            "asi": 80.0,
            "sci": 70.0,
            "gmi": 65.0
        }
        result = scorer.score_metrics(metrics)
        
        assert isinstance(result, dict)
        for metric_name, metric_data in result.items():
            assert "value" in metric_data
            assert "score" in metric_data
            assert "grade" in metric_data


class TestMetricsRunner:
    """MetricsRunner 테스트 클래스"""
    
    @pytest.fixture
    def runner(self):
        """Runner 픽스처"""
        return MetricsRunner()
    
    @pytest.mark.asyncio
    async def test_run(self, runner):
        """전체 실행 테스트"""
        store_code = "TEST_STORE_001"
        report = {
            "store_code": store_code,
            "commercial": {},
            "industry": {},
            "accessibility": {},
            "mobility": {}
        }
        
        result = await runner.run(store_code, report)
        
        assert result is not None
        assert "store_code" in result
        assert "metrics" in result
        assert "overall_score" in result

