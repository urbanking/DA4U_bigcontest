"""
Diagnostic Engine 테스트
"""
import pytest
from agents.store_agent.diagnostic_engine.rules import RuleEngine, DiagnosticRule
from agents.store_agent.diagnostic_engine.explanations import ExplanationGenerator
from agents.store_agent.diagnostic_engine.recommender import Recommender
from agents.store_agent.diagnostic_engine.diagnostic_runner import DiagnosticRunner


class TestRuleEngine:
    """RuleEngine 테스트 클래스"""
    
    @pytest.fixture
    def rule_engine(self):
        """RuleEngine 픽스처"""
        return RuleEngine()
    
    def test_evaluate_no_issues(self, rule_engine):
        """문제 없는 경우 테스트"""
        metrics = {
            "cvi": {"value": 80.0},
            "asi": {"value": 85.0},
            "sci": {"value": 75.0},
            "gmi": {"value": 70.0}
        }
        
        result = rule_engine.evaluate(metrics)
        assert isinstance(result, list)
    
    def test_evaluate_with_issues(self, rule_engine):
        """문제 있는 경우 테스트"""
        metrics = {
            "cvi": {"value": 50.0},  # warning
            "asi": {"value": 85.0},
            "sci": {"value": 75.0},
            "gmi": {"value": 70.0}
        }
        
        result = rule_engine.evaluate(metrics)
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_check_condition_below(self, rule_engine):
        """조건 체크 (below) 테스트"""
        rule = DiagnosticRule(
            rule_name="test",
            metric_name="cvi",
            condition="below",
            threshold=60.0,
            severity="warning",
            message="Test message"
        )
        
        assert rule_engine._check_condition(50.0, rule) == True
        assert rule_engine._check_condition(70.0, rule) == False


class TestExplanationGenerator:
    """ExplanationGenerator 테스트 클래스"""
    
    @pytest.fixture
    def generator(self):
        """Generator 픽스처"""
        return ExplanationGenerator()
    
    def test_generate(self, generator):
        """설명 생성 테스트"""
        result = generator.generate("low_cvi", 55.0)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "55" in result or "55.0" in result
    
    def test_generate_causal_explanation(self, generator):
        """인과 설명 생성 테스트"""
        metrics = {
            "cvi": {"value": 50.0},
            "asi": {"value": 60.0}
        }
        
        result = generator.generate_causal_explanation(metrics)
        assert isinstance(result, str)


class TestRecommender:
    """Recommender 테스트 클래스"""
    
    @pytest.fixture
    def recommender(self):
        """Recommender 픽스처"""
        return Recommender()
    
    def test_generate_recommendations(self, recommender):
        """권고사항 생성 테스트"""
        rules = [
            DiagnosticRule(
                rule_name="low_cvi",
                metric_name="cvi",
                condition="below",
                threshold=60.0,
                severity="warning",
                message="Low CVI"
            )
        ]
        
        result = recommender.generate_recommendations(rules)
        
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_prioritize_recommendations(self, recommender):
        """권고사항 우선순위화 테스트"""
        recommendations = ["Action 1", "Action 2"]
        metrics = {"cvi": {"value": 50.0}}
        
        result = recommender.prioritize_recommendations(recommendations, metrics)
        
        assert isinstance(result, list)
        assert len(result) == len(recommendations)


class TestDiagnosticRunner:
    """DiagnosticRunner 테스트 클래스"""
    
    @pytest.fixture
    def runner(self):
        """Runner 픽스처"""
        return DiagnosticRunner()
    
    @pytest.mark.asyncio
    async def test_run(self, runner):
        """진단 실행 테스트"""
        store_code = "TEST_STORE_001"
        metrics = {
            "cvi": {"value": 50.0},
            "asi": {"value": 75.0},
            "sci": {"value": 70.0},
            "gmi": {"value": 65.0}
        }
        
        result = await runner.run(store_code, metrics)
        
        assert result is not None
        assert "store_code" in result
        assert "issues" in result
        assert "recommendations" in result
        assert "overall_health" in result

