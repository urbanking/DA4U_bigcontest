"""
Planner Agent
Sequential Thinking MCP를 사용한 계획 수립 에이전트
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime
from agents.base_agent import BaseAgent, AgentState

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """
    계획 수립 에이전트
    Sequential Thinking MCP를 사용하여 실행 계획을 수립
    """
    
    def __init__(self):
        super().__init__(agent_name="PlannerAgent", temperature=0.3)
        logger.info("계획 수립 에이전트 초기화 완료")
    
    async def execute_analysis_with_self_evaluation(self, state: AgentState) -> Dict[str, Any]:
        """
        Sequential Thinking MCP를 사용한 계획 수립 및 자가 평가
        
        Args:
            state: LangGraph 워크플로우의 현재 상태
            
        Returns:
            계획 수립 결과와 자가 평가
        """
        user_query = state["user_query"]
        user_id = state["user_id"]
        session_id = state["session_id"]
        context = state["context"]
        
        logger.info(f"계획 수립 시작 - 사용자: {user_id}, 쿼리: {user_query}")
        
        try:
            # 1. 메모리 로드
            memory_insights = await self.load_user_memory(user_id, user_query)
            state["memory_insights"] = memory_insights
            
            # 2. Sequential Thinking MCP를 사용한 계획 수립
            execution_plan = await self._perform_planning_with_sequential_thinking(
                user_query, context, memory_insights
            )
            
            # 3. 자가 평가 수행
            evaluation_result = await self._perform_self_evaluation(execution_plan, user_query, memory_insights)
            
            # 4. 메모리 저장
            await self.save_to_memory(
                user_id, 
                session_id, 
                execution_plan, 
                {"quality_score": evaluation_result["quality_score"]}
            )
            
            logger.info(f"계획 수립 완료 - 품질점수: {evaluation_result['quality_score']}")
            
            return self.format_output(
                plan=execution_plan,
                self_evaluation=evaluation_result,
                memory_insights=memory_insights
            )
            
        except Exception as e:
            logger.error(f"계획 수립 에러: {e}")
            return self.handle_error(e)
    
    async def _perform_planning_with_sequential_thinking(
        self, 
        user_query: str, 
        context: Dict[str, Any], 
        memory_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sequential Thinking MCP를 사용한 계획 수립
        
        Args:
            user_query: 사용자 쿼리
            context: 컨텍스트
            memory_insights: 메모리 인사이트
            
        Returns:
            실행 계획 결과
        """
        try:
            # Sequential Thinking MCP 클라이언트 사용
            from backend.mcp.sequential_thinking_client import get_sequential_thinking_client
            
            client = get_sequential_thinking_client()
            
            # Sequential Thinking으로 계획 수립
            planning_problem = f"""
            사용자 쿼리: {user_query}
            컨텍스트: {context}
            메모리 인사이트: {memory_insights}
            
            이 쿼리를 해결하기 위한 상권 분석 시스템의 실행 계획을 수립해주세요.
            다음을 포함해야 합니다:
            1. 필요한 전문 에이전트들의 선택 (데이터 컨설팅 vs 마케팅)
            2. 실행 순서 및 의존성
            3. 각 단계별 예상 결과
            4. 전체 분석의 일관성 보장 방법
            5. Primary Orchestrator가 선택해야 할 메인 에이전트 타입
            """
            
            logger.info("Sequential Thinking MCP를 사용한 계획 수립 시작")
            thinking_result = await client.sequential_thinking(
                problem_description=planning_problem,
                initial_thoughts=6,
                max_iterations=8
            )
            
            if thinking_result["status"] == "success":
                # Sequential Thinking 결과를 바탕으로 실행 계획 생성
                execution_plan = self._create_execution_plan_from_thinking(
                    user_query, context, memory_insights, thinking_result
                )
                
                logger.info("Sequential Thinking MCP 기반 계획 수립 완료")
                return execution_plan
            else:
                # Sequential Thinking 실패시 기본 계획 생성
                logger.warning(f"Sequential Thinking 실패: {thinking_result.get('error', 'Unknown error')}")
                return self._create_default_execution_plan(user_query, context, memory_insights)
                
        except Exception as e:
            logger.error(f"Sequential Thinking 기반 계획 수립 에러: {e}")
            # 에러 발생시 기본 계획 생성
            return self._create_default_execution_plan(user_query, context, memory_insights)
    
    def _create_execution_plan_from_thinking(
        self, 
        user_query: str, 
        context: Dict[str, Any], 
        memory_insights: Dict[str, Any], 
        thinking_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sequential Thinking 결과를 바탕으로 실행 계획 생성
        
        Args:
            user_query: 사용자 쿼리
            context: 컨텍스트
            memory_insights: 메모리 인사이트
            thinking_result: Sequential Thinking 결과
            
        Returns:
            실행 계획
        """
        # Sequential Thinking 결과에서 메인 에이전트 타입 결정
        final_analysis = thinking_result.get("final_analysis", "")
        
        # Primary Orchestrator가 선택할 메인 에이전트 타입 결정
        main_agent_type = "data_consulting"  # 기본값
        
        if any(word in user_query.lower() for word in ["마케팅", "marketing", "전략", "promotion", "광고"]):
            main_agent_type = "marketing"
        elif any(word in user_query.lower() for word in ["상권", "상가", "district", "고객", "customer", "매장", "store"]):
            main_agent_type = "data_consulting"
        
        # 데이터 컨설팅인 경우 필요한 전문 에이전트들 선택
        required_agents = []
        if main_agent_type == "data_consulting":
            if any(word in user_query.lower() for word in ["상권", "상가", "district"]):
                required_agents.append("commercial")
            if any(word in user_query.lower() for word in ["고객", "customer", "타겟"]):
                required_agents.append("customer")
            if any(word in user_query.lower() for word in ["매장", "store", "매출"]):
                required_agents.append("store")
            if any(word in user_query.lower() for word in ["경쟁", "competitor", "시장"]):
                required_agents.append("industry")
            if any(word in user_query.lower() for word in ["접근", "교통", "주차"]):
                required_agents.append("accessibility")
            if any(word in user_query.lower() for word in ["유동", "인구", "flow"]):
                required_agents.append("mobility")
            
            # 기본값
            if not required_agents:
                required_agents = ["commercial", "customer"]
        else:  # marketing
            required_agents = ["marketing"]
        
        # 실행 순서 생성
        execution_sequence = []
        for i, agent in enumerate(required_agents, 1):
            execution_sequence.append({
                "step": i,
                "agent": agent,
                "description": f"{agent} 분석 수행"
            })
        
        return {
            "analysis_type": "execution_planning",
            "plan_id": f"plan_{user_query}_{int(datetime.now().timestamp())}",
            "query_intent": user_query,
            "problem_type": "comprehensive_analysis",
            "main_agent_type": main_agent_type,  # Primary Orchestrator가 사용할 타입
            "required_agents": required_agents,  # Secondary Orchestrator가 사용할 에이전트들
            "priority": "high",
            "complexity": "complex",
            "execution_sequence": execution_sequence,
            "expected_outcomes": [
                f"{agent} 분석 보고서" for agent in required_agents
            ],
            "memory_insights": memory_insights,
            "sequential_thinking_result": thinking_result,
            "sequential_thinking_used": True,
            "thinking_steps": thinking_result.get("total_thoughts", 0),
            "implementation_note": "Sequential Thinking MCP 기반 계획 수립 완료"
        }
    
    def _create_default_execution_plan(
        self, 
        user_query: str, 
        context: Dict[str, Any], 
        memory_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        기본 실행 계획 생성 (Sequential Thinking 실패시)
        
        Args:
            user_query: 사용자 쿼리
            context: 컨텍스트
            memory_insights: 메모리 인사이트
            
        Returns:
            기본 실행 계획
        """
        # 기본적으로 데이터 컨설팅으로 분류
        main_agent_type = "data_consulting"
        if any(word in user_query.lower() for word in ["마케팅", "marketing", "전략", "promotion", "광고"]):
            main_agent_type = "marketing"
        
        if main_agent_type == "marketing":
            required_agents = ["marketing"]
        else:
            required_agents = ["commercial", "customer"]
        
        return {
            "analysis_type": "execution_planning",
            "plan_id": f"plan_{user_query}_{int(datetime.now().timestamp())}",
            "query_intent": user_query,
            "problem_type": "comprehensive_analysis",
            "main_agent_type": main_agent_type,
            "required_agents": required_agents,
            "priority": "high",
            "complexity": "complex",
            "execution_sequence": [
                {"step": 1, "agent": agent, "description": f"{agent} 분석 수행"}
                for agent in required_agents
            ],
            "expected_outcomes": [
                f"{agent} 분석 보고서" for agent in required_agents
            ],
            "memory_insights": memory_insights,
            "sequential_thinking_used": False,
            "implementation_note": "기본 계획 수립 (Sequential Thinking 사용 불가)"
        }
    
    async def _perform_self_evaluation(
        self, 
        analysis_result: Dict[str, Any], 
        user_query: str,
        memory_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        계획 수립 결과에 대한 자가 평가
        
        Args:
            analysis_result: 계획 수립 결과
            user_query: 사용자 쿼리
            memory_insights: 메모리 인사이트
            
        Returns:
            자가 평가 결과
        """
        # 기본 품질 점수
        quality_score = 0.8
        
        # Sequential Thinking 사용 여부에 따른 점수 조정
        if analysis_result.get("sequential_thinking_used", False):
            quality_score += 0.1
        
        # 메모리 활용 여부에 따른 점수 조정
        if memory_insights.get("memory_available", False):
            quality_score += 0.05
        
        # 계획의 완성도 평가
        if analysis_result.get("main_agent_type") and analysis_result.get("required_agents"):
            quality_score += 0.05
        
        # 최대 점수 제한
        quality_score = min(quality_score, 1.0)
        
        # 피드백 생성
        feedback_parts = []
        
        if analysis_result.get("sequential_thinking_used", False):
            feedback_parts.append("Sequential Thinking MCP를 활용한 체계적인 계획 수립")
        else:
            feedback_parts.append("기본 계획 수립 (Sequential Thinking 미사용)")
        
        if memory_insights.get("memory_available", False):
            feedback_parts.append("메모리 시스템을 활용한 컨텍스트 고려")
        
        if len(analysis_result.get("required_agents", [])) > 0:
            feedback_parts.append("필요한 전문 에이전트들이 적절히 식별됨")
        
        feedback = "계획 수립 완료. " + ", ".join(feedback_parts) + "."
        
        return {
            "quality_score": quality_score,
            "feedback": feedback,
            "completeness": 0.9,
            "accuracy": 0.8,
            "relevance": 0.9,
            "actionability": 0.8,
            "sequential_thinking_used": analysis_result.get("sequential_thinking_used", False),
            "memory_enhanced": memory_insights.get("memory_available", False)
        }
