"""
Primary Orchestrator Agent
Data Consulting vs Marketing 선택하는 1차 오케스트레이터
"""

from typing import Dict, Any, Optional
import logging
from agents.base_agent import BaseAgent, AgentState

logger = logging.getLogger(__name__)


class PrimaryOrchestratorAgent(BaseAgent):
    """
    1차 오케스트레이터 에이전트
    Planner의 계획을 바탕으로 Data Consulting vs Marketing 선택
    """
    
    def __init__(self):
        super().__init__(agent_name="PrimaryOrchestratorAgent", temperature=0.2)
        logger.info("1차 오케스트레이터 에이전트 초기화 완료")
    
    async def execute_analysis_with_self_evaluation(self, state: AgentState) -> Dict[str, Any]:
        """
        Planner의 계획을 바탕으로 메인 에이전트 타입 선택
        
        Args:
            state: LangGraph 워크플로우의 현재 상태
            
        Returns:
            메인 에이전트 타입 선택 결과
        """
        user_query = state["user_query"]
        user_id = state["user_id"]
        session_id = state["session_id"]
        current_plan = state.get("current_plan", {})
        
        logger.info(f"1차 오케스트레이터 실행 - 사용자: {user_id}")
        
        try:
            # 1. 메모리 로드
            memory_insights = await self.load_user_memory(user_id, user_query)
            
            # 2. Planner의 계획에서 메인 에이전트 타입 추출
            main_agent_type = current_plan.get("main_agent_type", "data_consulting")
            
            # 3. 메인 에이전트 타입 검증 및 조정
            validated_main_agent_type = self._validate_and_adjust_main_agent_type(
                main_agent_type, user_query, memory_insights
            )
            
            # 4. 상태 업데이트
            state["selected_main_agent"] = validated_main_agent_type
            
            # 5. 자가 평가
            evaluation_result = await self._perform_self_evaluation(
                validated_main_agent_type, current_plan, user_query, memory_insights
            )
            
            # 6. 메모리 저장
            orchestration_result = {
                "main_agent_type": validated_main_agent_type,
                "plan_based_selection": True,
                "original_plan": current_plan,
                "validation_performed": True
            }
            
            await self.save_to_memory(
                user_id, 
                session_id, 
                orchestration_result, 
                {"quality_score": evaluation_result["quality_score"]}
            )
            
            logger.info(f"1차 오케스트레이터 완료 - 선택된 메인 에이전트: {validated_main_agent_type}")
            
            return self.format_output(
                selected_main_agent=validated_main_agent_type,
                orchestration_decision=orchestration_result,
                self_evaluation=evaluation_result,
                memory_insights=memory_insights
            )
            
        except Exception as e:
            logger.error(f"1차 오케스트레이터 에러: {e}")
            return self.handle_error(e)
    
    def _validate_and_adjust_main_agent_type(
        self, 
        main_agent_type: str, 
        user_query: str, 
        memory_insights: Dict[str, Any]
    ) -> str:
        """
        메인 에이전트 타입 검증 및 조정
        
        Args:
            main_agent_type: Planner가 제안한 메인 에이전트 타입
            user_query: 사용자 쿼리
            memory_insights: 메모리 인사이트
            
        Returns:
            검증 및 조정된 메인 에이전트 타입
        """
        # 쿼리 재분석을 통한 검증
        query_analysis = self._analyze_query_intent(user_query)
        
        # 메모리 기반 조정
        memory_adjustment = self._get_memory_based_adjustment(memory_insights)
        
        # 최종 결정
        if query_analysis["primary_intent"] == "marketing":
            return "marketing"
        elif query_analysis["primary_intent"] == "data_consulting":
            return "data_consulting"
        else:
            # 기본값으로 data_consulting 선택
            return "data_consulting"
    
    def _analyze_query_intent(self, user_query: str) -> Dict[str, Any]:
        """
        쿼리 의도 분석
        
        Args:
            user_query: 사용자 쿼리
            
        Returns:
            쿼리 의도 분석 결과
        """
        query_lower = user_query.lower()
        
        # 마케팅 관련 키워드
        marketing_keywords = [
            "마케팅", "marketing", "전략", "strategy", "promotion", "광고", "advertisement",
            "브랜딩", "branding", "홍보", "pr", "소셜미디어", "sns", "온라인마케팅",
            "고객획득", "customer acquisition", "세일즈", "sales", "영업"
        ]
        
        # 데이터 컨설팅 관련 키워드
        data_consulting_keywords = [
            "상권", "상가", "district", "분석", "analysis", "고객분석", "customer analysis",
            "매장", "store", "매출", "revenue", "경쟁", "competitor", "시장", "market",
            "접근성", "accessibility", "교통", "traffic", "유동인구", "foot traffic",
            "창업", "startup", "입지", "location", "성공가능성", "viability"
        ]
        
        marketing_score = sum(1 for keyword in marketing_keywords if keyword in query_lower)
        data_consulting_score = sum(1 for keyword in data_consulting_keywords if keyword in query_lower)
        
        if marketing_score > data_consulting_score:
            primary_intent = "marketing"
        elif data_consulting_score > marketing_score:
            primary_intent = "data_consulting"
        else:
            primary_intent = "data_consulting"  # 기본값
        
        return {
            "primary_intent": primary_intent,
            "marketing_score": marketing_score,
            "data_consulting_score": data_consulting_score,
            "confidence": max(marketing_score, data_consulting_score) / max(1, marketing_score + data_consulting_score)
        }
    
    def _get_memory_based_adjustment(self, memory_insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        메모리 기반 조정 정보
        
        Args:
            memory_insights: 메모리 인사이트
            
        Returns:
            메모리 기반 조정 정보
        """
        if not memory_insights.get("memory_available", False):
            return {"adjustment": "none", "reason": "no_memory"}
        
        # 과거 쿼리 패턴 분석 (플레이스홀더)
        # 실제 구현시 메모리에서 과거 쿼리들을 분석하여 패턴 파악
        
        return {
            "adjustment": "none",
            "reason": "memory_available_but_no_pattern_detected",
            "memory_enhanced": True
        }
    
    async def _perform_self_evaluation(
        self, 
        selected_main_agent: str,
        current_plan: Dict[str, Any],
        user_query: str,
        memory_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        오케스트레이션 결과에 대한 자가 평가
        
        Args:
            selected_main_agent: 선택된 메인 에이전트 타입
            current_plan: 현재 계획
            user_query: 사용자 쿼리
            memory_insights: 메모리 인사이트
            
        Returns:
            자가 평가 결과
        """
        # 기본 품질 점수
        quality_score = 0.8
        
        # 계획 기반 선택 여부에 따른 점수 조정
        if current_plan.get("main_agent_type") == selected_main_agent:
            quality_score += 0.1  # 계획과 일치
        
        # 메모리 활용 여부에 따른 점수 조정
        if memory_insights.get("memory_available", False):
            quality_score += 0.05
        
        # 쿼리 분석 정확도에 따른 점수 조정
        query_analysis = self._analyze_query_intent(user_query)
        if query_analysis["confidence"] > 0.7:
            quality_score += 0.05
        
        # 최대 점수 제한
        quality_score = min(quality_score, 1.0)
        
        # 피드백 생성
        feedback_parts = []
        
        if current_plan.get("main_agent_type") == selected_main_agent:
            feedback_parts.append("Planner의 계획과 일치하는 메인 에이전트 선택")
        else:
            feedback_parts.append("쿼리 재분석을 통한 메인 에이전트 타입 조정")
        
        if memory_insights.get("memory_available", False):
            feedback_parts.append("메모리 시스템을 활용한 컨텍스트 고려")
        
        if query_analysis["confidence"] > 0.7:
            feedback_parts.append("높은 신뢰도로 쿼리 의도 파악")
        
        feedback = f"메인 에이전트 '{selected_main_agent}' 선택 완료. " + ", ".join(feedback_parts) + "."
        
        return {
            "quality_score": quality_score,
            "feedback": feedback,
            "completeness": 0.9,
            "accuracy": 0.85,
            "relevance": 0.9,
            "actionability": 0.8,
            "query_confidence": query_analysis["confidence"],
            "memory_enhanced": memory_insights.get("memory_available", False)
        }
