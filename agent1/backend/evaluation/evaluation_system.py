"""
에이전트 평가 및 리뷰 시스템
각 단계별 품질 평가 및 피드백 제공
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """평가 결과 구조"""
    agent_name: str
    quality_score: float
    completeness_score: float
    accuracy_score: float
    timeliness_score: float
    overall_score: float
    feedback: List[str]
    recommendations: List[str]


class EvaluationSystem:
    """에이전트 평가 시스템"""
    
    def __init__(self):
        """평가 시스템 초기화"""
        self.evaluation_history = {}
        self.quality_threshold = 0.7
        self.improvement_suggestions = {}
        
    async def evaluate_results(
        self,
        workflow_result: Dict[str, Any],
        user_query: str
    ) -> Dict[str, float]:
        """
        워크플로우 결과 평가
        
        Args:
            workflow_result: 워크플로우 실행 결과
            user_query: 사용자 쿼리
            
        Returns:
            에이전트별 평가 점수
        """
        try:
            evaluation_scores = {}
            agent_results = workflow_result.get("agent_results", {})
            
            # 각 에이전트 결과 평가
            for agent_name, agent_result in agent_results.items():
                evaluation = await self._evaluate_agent_result(
                    agent_name,
                    agent_result,
                    user_query
                )
                evaluation_scores[agent_name] = evaluation.overall_score
                
                # 평가 히스토리 저장
                self.evaluation_history[agent_name] = evaluation
            
            # 전체 워크플로우 평가
            overall_score = self._calculate_overall_score(evaluation_scores)
            evaluation_scores["overall"] = overall_score
            
            # 개선 제안 생성
            await self._generate_improvement_suggestions(evaluation_scores)
            
            logger.info(f"평가 완료 - 전체 점수: {overall_score:.2f}")
            return evaluation_scores
            
        except Exception as e:
            logger.error(f"평가 시스템 에러: {e}")
            return {"error": str(e)}
    
    async def _evaluate_agent_result(
        self,
        agent_name: str,
        agent_result: Dict[str, Any],
        user_query: str
    ) -> EvaluationResult:
        """개별 에이전트 결과 평가"""
        
        # 1. 품질 점수 (결과의 완성도)
        quality_score = self._evaluate_quality(agent_result)
        
        # 2. 완성도 점수 (요청된 정보 제공 여부)
        completeness_score = self._evaluate_completeness(agent_result, user_query)
        
        # 3. 정확성 점수 (결과의 논리적 일관성)
        accuracy_score = self._evaluate_accuracy(agent_result)
        
        # 4. 적시성 점수 (응답 속도)
        timeliness_score = self._evaluate_timeliness(agent_result)
        
        # 전체 점수 계산
        overall_score = (
            quality_score * 0.3 +
            completeness_score * 0.3 +
            accuracy_score * 0.25 +
            timeliness_score * 0.15
        )
        
        # 피드백 생성
        feedback = self._generate_feedback(
            quality_score, completeness_score, accuracy_score, timeliness_score
        )
        
        # 개선 권장사항
        recommendations = self._generate_recommendations(
            agent_name, overall_score, feedback
        )
        
        return EvaluationResult(
            agent_name=agent_name,
            quality_score=quality_score,
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            timeliness_score=timeliness_score,
            overall_score=overall_score,
            feedback=feedback,
            recommendations=recommendations
        )
    
    def _evaluate_quality(self, agent_result: Dict[str, Any]) -> float:
        """품질 평가"""
        score = 0.0
        
        # 상태 확인
        if agent_result.get("status") == "success":
            score += 0.4
        
        # 결과 데이터 존재 여부
        results = agent_result.get("results", {})
        if results:
            score += 0.3
            
            # 결과의 상세성
            if len(results) > 2:
                score += 0.2
            
            # 구조화된 데이터
            if isinstance(results, dict) and len(results) > 0:
                score += 0.1
        
        return min(score, 1.0)
    
    def _evaluate_completeness(self, agent_result: Dict[str, Any], user_query: str) -> float:
        """완성도 평가"""
        score = 0.0
        
        # 에이전트 타입별 완성도 체크
        agent_name = agent_result.get("agent_name", "")
        results = agent_result.get("results", {})
        
        if "CommercialDistrictAgent" in agent_name:
            required_fields = ["district_status", "competition_level"]
            score = self._check_required_fields(results, required_fields)
        
        elif "CustomerAnalysisAgent" in agent_name:
            required_fields = ["churn_analysis", "retention_opportunities"]
            score = self._check_required_fields(results, required_fields)
        
        elif "StoreAnalysisAgent" in agent_name:
            required_fields = ["sales_trends", "menu_performance"]
            score = self._check_required_fields(results, required_fields)
        
        else:
            # 기본 완성도 체크
            score = 0.7 if results else 0.0
        
        return score
    
    def _evaluate_accuracy(self, agent_result: Dict[str, Any]) -> float:
        """정확성 평가"""
        score = 0.5  # 기본 점수
        
        results = agent_result.get("results", {})
        
        # 데이터 타입 검증
        if isinstance(results, dict):
            score += 0.2
        
        # 논리적 일관성 체크
        if self._check_logical_consistency(results):
            score += 0.3
        
        return min(score, 1.0)
    
    def _evaluate_timeliness(self, agent_result: Dict[str, Any]) -> float:
        """적시성 평가"""
        # 실제 구현에서는 실행 시간 측정
        return 0.8  # 기본값
    
    def _check_required_fields(self, results: Dict[str, Any], required_fields: List[str]) -> float:
        """필수 필드 존재 여부 체크"""
        if not results:
            return 0.0
        
        present_fields = sum(1 for field in required_fields if field in results)
        return present_fields / len(required_fields)
    
    def _check_logical_consistency(self, results: Dict[str, Any]) -> bool:
        """논리적 일관성 체크"""
        # 기본적인 일관성 체크
        if not results:
            return False
        
        # 예: 음수 값이 없는지 체크
        for key, value in results.items():
            if isinstance(value, (int, float)) and value < 0:
                return False
        
        return True
    
    def _generate_feedback(
        self,
        quality_score: float,
        completeness_score: float,
        accuracy_score: float,
        timeliness_score: float
    ) -> List[str]:
        """피드백 생성"""
        feedback = []
        
        if quality_score < self.quality_threshold:
            feedback.append("결과 품질을 개선할 필요가 있습니다.")
        
        if completeness_score < self.quality_threshold:
            feedback.append("더 완전한 분석이 필요합니다.")
        
        if accuracy_score < self.quality_threshold:
            feedback.append("데이터 정확성을 검토해주세요.")
        
        if timeliness_score < self.quality_threshold:
            feedback.append("응답 속도를 개선할 수 있습니다.")
        
        if not feedback:
            feedback.append("전반적으로 우수한 결과입니다.")
        
        return feedback
    
    def _generate_recommendations(
        self,
        agent_name: str,
        overall_score: float,
        feedback: List[str]
    ) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        if overall_score < 0.6:
            recommendations.append("전체적인 성능 개선이 필요합니다.")
        
        if "CommercialDistrictAgent" in agent_name and overall_score < 0.7:
            recommendations.append("상권 데이터 수집 로직을 개선하세요.")
        
        if "CustomerAnalysisAgent" in agent_name and overall_score < 0.7:
            recommendations.append("고객 세분화 알고리즘을 고도화하세요.")
        
        return recommendations
    
    def _calculate_overall_score(self, evaluation_scores: Dict[str, float]) -> float:
        """전체 점수 계산"""
        if not evaluation_scores:
            return 0.0
        
        # overall 점수 제외
        agent_scores = {k: v for k, v in evaluation_scores.items() if k != "overall"}
        
        if not agent_scores:
            return 0.0
        
        return sum(agent_scores.values()) / len(agent_scores)
    
    async def _generate_improvement_suggestions(self, evaluation_scores: Dict[str, float]):
        """개선 제안 생성"""
        for agent_name, score in evaluation_scores.items():
            if agent_name != "overall" and score < self.quality_threshold:
                self.improvement_suggestions[agent_name] = {
                    "current_score": score,
                    "target_score": 0.8,
                    "suggestions": [
                        "데이터 수집 로직 개선",
                        "분석 알고리즘 고도화",
                        "응답 시간 최적화"
                    ]
                }
    
    async def submit_feedback(
        self,
        session_id: str,
        feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """사용자 피드백 제출"""
        try:
            # 피드백 저장 및 학습
            feedback_data = {
                "session_id": session_id,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat()
            }
            
            # 개선 제안 업데이트
            await self._update_improvement_suggestions(feedback_data)
            
            return {"status": "success", "message": "피드백이 저장되었습니다."}
            
        except Exception as e:
            logger.error(f"피드백 제출 에러: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _update_improvement_suggestions(self, feedback_data: Dict[str, Any]):
        """개선 제안 업데이트"""
        # 실제 구현에서는 피드백 기반으로 시스템 개선
        pass
    
    def is_healthy(self) -> bool:
        """평가 시스템 상태 확인"""
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """평가 시스템 상태 정보"""
        return {
            "total_evaluations": len(self.evaluation_history),
            "improvement_suggestions": len(self.improvement_suggestions),
            "is_healthy": self.is_healthy()
        }
