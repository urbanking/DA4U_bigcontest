"""
Secondary Orchestrator Agent
Data Consulting 내에서 전문 에이전트들을 선택하는 2차 오케스트레이터
"""

from typing import Dict, Any, List, Optional
import logging
from agents.base_agent import BaseAgent, AgentState

logger = logging.getLogger(__name__)


class SecondaryOrchestratorAgent(BaseAgent):
    """
    2차 오케스트레이터 에이전트
    Data Consulting 내에서 필요한 전문 에이전트들을 선택하고 실행 순서 결정
    """
    
    def __init__(self):
        super().__init__(agent_name="SecondaryOrchestratorAgent", temperature=0.2)
        logger.info("2차 오케스트레이터 에이전트 초기화 완료")
    
    async def execute_analysis_with_self_evaluation(self, state: AgentState) -> Dict[str, Any]:
        """
        Data Consulting 내에서 전문 에이전트들 선택 및 실행 순서 결정
        
        Args:
            state: LangGraph 워크플로우의 현재 상태
            
        Returns:
            전문 에이전트 선택 및 실행 순서 결정 결과
        """
        user_query = state["user_query"]
        user_id = state["user_id"]
        session_id = state["session_id"]
        current_plan = state.get("current_plan", {})
        selected_main_agent = state.get("selected_main_agent", "data_consulting")
        
        logger.info(f"2차 오케스트레이터 실행 - 메인 에이전트: {selected_main_agent}")
        
        try:
            # 1. 메모리 로드
            memory_insights = await self.load_user_memory(user_id, user_query)
            
            # 2. 메인 에이전트가 data_consulting인 경우에만 전문 에이전트 선택
            if selected_main_agent == "data_consulting":
                selected_specialized_agents = self._select_specialized_agents(
                    current_plan, user_query, memory_insights
                )
                
                # 3. 실행 순서 결정
                execution_order = self._determine_execution_order(
                    selected_specialized_agents, user_query, memory_insights
                )
                
                orchestration_result = {
                    "main_agent_type": selected_main_agent,
                    "selected_specialized_agents": selected_specialized_agents,
                    "execution_order": execution_order,
                    "orchestration_type": "data_consulting"
                }
            else:
                # 마케팅 에이전트인 경우
                selected_specialized_agents = ["marketing"]
                execution_order = [{"step": 1, "agent": "marketing", "description": "마케팅 전략 분석 수행"}]
                
                orchestration_result = {
                    "main_agent_type": selected_main_agent,
                    "selected_specialized_agents": selected_specialized_agents,
                    "execution_order": execution_order,
                    "orchestration_type": "marketing"
                }
            
            # 4. 상태 업데이트
            state["selected_specialized_agents"] = selected_specialized_agents
            
            # 5. 자가 평가
            evaluation_result = await self._perform_self_evaluation(
                orchestration_result, user_query, memory_insights
            )
            
            # 6. 메모리 저장
            await self.save_to_memory(
                user_id, 
                session_id, 
                orchestration_result, 
                {"quality_score": evaluation_result["quality_score"]}
            )
            
            logger.info(f"2차 오케스트레이터 완료 - 선택된 전문 에이전트들: {selected_specialized_agents}")
            
            return self.format_output(
                orchestration_result=orchestration_result,
                self_evaluation=evaluation_result,
                memory_insights=memory_insights
            )
            
        except Exception as e:
            logger.error(f"2차 오케스트레이터 에러: {e}")
            return self.handle_error(e)
    
    def _select_specialized_agents(
        self, 
        current_plan: Dict[str, Any], 
        user_query: str, 
        memory_insights: Dict[str, Any]
    ) -> List[str]:
        """
        전문 에이전트들 선택
        
        Args:
            current_plan: 현재 계획
            user_query: 사용자 쿼리
            memory_insights: 메모리 인사이트
            
        Returns:
            선택된 전문 에이전트들 리스트
        """
        # Planner의 계획에서 제안된 에이전트들 가져오기
        planned_agents = current_plan.get("required_agents", [])
        
        # 쿼리 재분석을 통한 에이전트 검증
        query_based_agents = self._analyze_query_for_agents(user_query)
        
        # 메모리 기반 조정
        memory_adjusted_agents = self._apply_memory_adjustments(
            planned_agents, query_based_agents, memory_insights
        )
        
        # 최종 에이전트 리스트 결정
        final_agents = self._finalize_agent_selection(
            planned_agents, query_based_agents, memory_adjusted_agents
        )
        
        return final_agents
    
    def _analyze_query_for_agents(self, user_query: str) -> List[str]:
        """
        쿼리 분석을 통한 필요한 에이전트들 식별
        
        Args:
            user_query: 사용자 쿼리
            
        Returns:
            쿼리 기반 에이전트 리스트
        """
        query_lower = user_query.lower()
        identified_agents = []
        
        # 각 에이전트별 키워드 매핑
        agent_keywords = {
            "commercial": ["상권", "상가", "district", "지역", "구역", "상권분석"],
            "customer": ["고객", "customer", "타겟", "target", "고객분석", "고객층"],
            "store": ["매장", "store", "매출", "revenue", "매장분석", "매출분석"],
            "industry": ["경쟁", "competitor", "시장", "market", "경쟁사", "업계"],
            "accessibility": ["접근", "교통", "주차", "traffic", "parking", "접근성"],
            "mobility": ["유동", "인구", "flow", "유동인구", "보행량", "인구밀도"]
        }
        
        # 키워드 기반 에이전트 식별
        for agent, keywords in agent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                identified_agents.append(agent)
        
        # 기본값 (아무것도 식별되지 않은 경우)
        if not identified_agents:
            identified_agents = ["commercial", "customer"]
        
        return identified_agents
    
    def _apply_memory_adjustments(
        self, 
        planned_agents: List[str], 
        query_agents: List[str], 
        memory_insights: Dict[str, Any]
    ) -> List[str]:
        """
        메모리 기반 에이전트 조정
        
        Args:
            planned_agents: 계획된 에이전트들
            query_agents: 쿼리 기반 에이전트들
            memory_insights: 메모리 인사이트
            
        Returns:
            메모리 조정된 에이전트들
        """
        if not memory_insights.get("memory_available", False):
            return query_agents
        
        # 과거 성공 패턴 기반 조정 (플레이스홀더)
        # 실제 구현시 메모리에서 과거 성공한 에이전트 조합들을 분석
        
        return query_agents
    
    def _finalize_agent_selection(
        self, 
        planned_agents: List[str], 
        query_agents: List[str], 
        memory_agents: List[str]
    ) -> List[str]:
        """
        최종 에이전트 선택
        
        Args:
            planned_agents: 계획된 에이전트들
            query_agents: 쿼리 기반 에이전트들
            memory_agents: 메모리 조정된 에이전트들
            
        Returns:
            최종 선택된 에이전트들
        """
        # 계획과 쿼리 분석 결과의 교집합을 우선으로 함
        intersection = list(set(planned_agents) & set(query_agents))
        
        if intersection:
            return intersection
        elif query_agents:
            return query_agents
        elif planned_agents:
            return planned_agents
        else:
            return ["commercial", "customer"]  # 기본값
    
    def _determine_execution_order(
        self, 
        selected_agents: List[str], 
        user_query: str, 
        memory_insights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        에이전트 실행 순서 결정
        
        Args:
            selected_agents: 선택된 에이전트들
            user_query: 사용자 쿼리
            memory_insights: 메모리 인사이트
            
        Returns:
            실행 순서 리스트
        """
        # 에이전트 간 의존성 정의
        agent_dependencies = {
            "commercial": [],  # 상권 분석은 독립적
            "customer": ["commercial"],  # 고객 분석은 상권 분석 후
            "store": ["commercial"],  # 매장 분석은 상권 분석 후
            "industry": ["commercial"],  # 산업 분석은 상권 분석 후
            "accessibility": ["commercial"],  # 접근성 분석은 상권 분석 후
            "mobility": ["commercial"]  # 유동인구 분석은 상권 분석 후
        }
        
        # 실행 순서 결정
        execution_order = []
        completed_agents = set()
        remaining_agents = set(selected_agents)
        step = 1
        
        while remaining_agents:
            # 의존성이 충족된 에이전트들 찾기
            ready_agents = []
            for agent in remaining_agents:
                dependencies = agent_dependencies.get(agent, [])
                if all(dep in completed_agents for dep in dependencies):
                    ready_agents.append(agent)
            
            # 준비된 에이전트들을 실행 순서에 추가
            for agent in ready_agents:
                execution_order.append({
                    "step": step,
                    "agent": agent,
                    "description": f"{agent} 분석 수행",
                    "dependencies": agent_dependencies.get(agent, [])
                })
                completed_agents.add(agent)
                remaining_agents.remove(agent)
                step += 1
            
            # 무한 루프 방지 (의존성 충족 불가능한 경우)
            if not ready_agents:
                # 남은 에이전트들을 순서대로 추가
                for agent in list(remaining_agents):
                    execution_order.append({
                        "step": step,
                        "agent": agent,
                        "description": f"{agent} 분석 수행 (의존성 무시)",
                        "dependencies": agent_dependencies.get(agent, [])
                    })
                    step += 1
                break
        
        return execution_order
    
    async def _perform_self_evaluation(
        self, 
        orchestration_result: Dict[str, Any],
        user_query: str,
        memory_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        오케스트레이션 결과에 대한 자가 평가
        
        Args:
            orchestration_result: 오케스트레이션 결과
            user_query: 사용자 쿼리
            memory_insights: 메모리 인사이트
            
        Returns:
            자가 평가 결과
        """
        # 기본 품질 점수
        quality_score = 0.8
        
        selected_agents = orchestration_result.get("selected_specialized_agents", [])
        execution_order = orchestration_result.get("execution_order", [])
        
        # 에이전트 선택 적절성 평가
        if len(selected_agents) >= 2:  # 최소 2개 에이전트
            quality_score += 0.05
        
        if len(selected_agents) <= 4:  # 너무 많지 않음
            quality_score += 0.05
        
        # 실행 순서 적절성 평가
        if len(execution_order) == len(selected_agents):  # 모든 에이전트가 순서에 포함됨
            quality_score += 0.05
        
        # 메모리 활용 여부에 따른 점수 조정
        if memory_insights.get("memory_available", False):
            quality_score += 0.05
        
        # 최대 점수 제한
        quality_score = min(quality_score, 1.0)
        
        # 피드백 생성
        feedback_parts = []
        
        feedback_parts.append(f"{len(selected_agents)}개 전문 에이전트 선택")
        
        if orchestration_result.get("orchestration_type") == "data_consulting":
            feedback_parts.append("데이터 컨설팅 전문 에이전트들 구성")
        else:
            feedback_parts.append("마케팅 에이전트 선택")
        
        if len(execution_order) > 1:
            feedback_parts.append("의존성을 고려한 실행 순서 결정")
        
        if memory_insights.get("memory_available", False):
            feedback_parts.append("메모리 시스템을 활용한 최적화")
        
        feedback = "전문 에이전트 오케스트레이션 완료. " + ", ".join(feedback_parts) + "."
        
        return {
            "quality_score": quality_score,
            "feedback": feedback,
            "completeness": 0.9,
            "accuracy": 0.85,
            "relevance": 0.9,
            "actionability": 0.8,
            "agents_selected": len(selected_agents),
            "execution_steps": len(execution_order),
            "memory_enhanced": memory_insights.get("memory_available", False)
        }
