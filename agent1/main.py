"""
멀티 에이전트 상권 분석 시스템 - 메인 실행 파일
2-Tier Orchestrator 구조: Primary (Data Consulting vs Marketing) → Secondary (Specialized Agents)
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from typing_extensions import TypedDict, Annotated
from langgraph.graph import StateGraph, END

# Import core agents
from agents.base_agent import BaseAgent, AgentState
from agents.planner_agent import PlannerAgent
from agents.primary_orchestrator import PrimaryOrchestratorAgent
from agents.secondary_orchestrator import SecondaryOrchestratorAgent

# Import modular specialized agents (for team development)
from agents.modules.commercial_agent_module import CommercialAgentModule
from agents.modules.customer_agent_module import CustomerAgentModule
from agents.modules.store_agent_module import StoreAgentModule
from agents.modules.industry_agent_module import IndustryAgentModule
from agents.modules.accessibility_agent_module import AccessibilityAgentModule
from agents.modules.mobility_agent_module import MobilityAgentModule
from agents.modules.marketing_agent_module import MarketingAgentModule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiAgentSystem:
    """
    2-Tier Orchestrator 구조의 멀티 에이전트 시스템
    """
    
    def __init__(self):
        # Core agents
        self.planner_agent = PlannerAgent()
        self.primary_orchestrator = PrimaryOrchestratorAgent()
        self.secondary_orchestrator = SecondaryOrchestratorAgent()
        
        # Specialized agents (for team development)
        self.specialized_agents = {
            "commercial": CommercialAgentModule(),
            "customer": CustomerAgentModule(),
            "store": StoreAgentModule(),
            "industry": IndustryAgentModule(),
            "accessibility": AccessibilityAgentModule(),
            "mobility": MobilityAgentModule(),
            "marketing": MarketingAgentModule()
        }
        
        # LangGraph 워크플로우 구성
        self.workflow = self._build_workflow()
        
        logger.info("2-Tier Orchestrator 멀티 에이전트 시스템 초기화 완료")
    
    def _build_workflow(self) -> StateGraph:
        """2-Tier Orchestrator 구조의 LangGraph 워크플로우 구성"""
        workflow = StateGraph(AgentState)
        
        # Add Nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("primary_orchestrator", self._primary_orchestrator_node)
        workflow.add_node("secondary_orchestrator", self._secondary_orchestrator_node)
        
        # Specialized agent nodes
        for agent_name in self.specialized_agents.keys():
            workflow.add_node(f"{agent_name}_agent", self._specialized_agent_node)
        
        workflow.add_node("synthesis", self._synthesis_node)
        workflow.add_node("final_report", self._final_report_node)
        
        # Set Entry Point
        workflow.set_entry_point("planner")
        
        # Define Edges - 2-Tier Orchestrator Flow
        workflow.add_edge("planner", "primary_orchestrator")
        workflow.add_edge("primary_orchestrator", "secondary_orchestrator")
        
        # Conditional edges from secondary orchestrator to specialized agents
        workflow.add_conditional_edges(
            "secondary_orchestrator",
            self._route_to_specialized_agents,
            {
                "commercial": "commercial_agent",
                "customer": "customer_agent", 
                "store": "store_agent",
                "industry": "industry_agent",
                "accessibility": "accessibility_agent",
                "mobility": "mobility_agent",
                "marketing": "marketing_agent",
                "synthesis": "synthesis"  # If no specialized agents needed
            }
        )
        
        # Edges from specialized agents to synthesis
        for agent_name in self.specialized_agents.keys():
            workflow.add_edge(f"{agent_name}_agent", "synthesis")
        
        workflow.add_edge("synthesis", "final_report")
        workflow.add_edge("final_report", END)
        
        return workflow.compile()
    
    # ==================== Node Methods ====================
    
    async def _planner_node(self, state: AgentState) -> Dict[str, Any]:
        """계획 수립 노드"""
        logger.info("=== Planner Agent 실행 ===")
        planner_result = await self.planner_agent.execute_analysis_with_self_evaluation(state)
        state["current_plan"] = planner_result["results"]["plan"]
        state["messages"].append(AIMessage(content=f"Planner: {planner_result['results']['self_evaluation']['feedback']}"))
        state["agent_results"]["planner"] = planner_result
        return state
    
    async def _primary_orchestrator_node(self, state: AgentState) -> Dict[str, Any]:
        """1차 오케스트레이터 노드 - Data Consulting vs Marketing 선택"""
        logger.info("=== Primary Orchestrator 실행 ===")
        orchestrator_result = await self.primary_orchestrator.execute_analysis_with_self_evaluation(state)
        state["selected_main_agent"] = orchestrator_result["results"]["selected_main_agent"]
        state["messages"].append(AIMessage(content=f"Primary Orchestrator: {orchestrator_result['results']['self_evaluation']['feedback']}"))
        state["agent_results"]["primary_orchestrator"] = orchestrator_result
        return state
    
    async def _secondary_orchestrator_node(self, state: AgentState) -> Dict[str, Any]:
        """2차 오케스트레이터 노드 - 전문 에이전트들 선택"""
        logger.info("=== Secondary Orchestrator 실행 ===")
        orchestrator_result = await self.secondary_orchestrator.execute_analysis_with_self_evaluation(state)
        state["selected_specialized_agents"] = orchestrator_result["results"]["orchestration_result"]["selected_specialized_agents"]
        state["messages"].append(AIMessage(content=f"Secondary Orchestrator: {orchestrator_result['results']['self_evaluation']['feedback']}"))
        state["agent_results"]["secondary_orchestrator"] = orchestrator_result
        return state
    
    def _route_to_specialized_agents(self, state: AgentState) -> str:
        """전문 에이전트들로 라우팅"""
        selected_agents = state.get("selected_specialized_agents", [])
        
        if not selected_agents:
            return "synthesis"
        
        # 첫 번째 에이전트로 라우팅 (실제로는 병렬 실행이 더 좋지만, 여기서는 순차적으로)
        return selected_agents[0]
    
    async def _specialized_agent_node(self, state: AgentState) -> Dict[str, Any]:
        """전문 에이전트 노드"""
        # 현재 실행 중인 에이전트 결정
        selected_agents = state.get("selected_specialized_agents", [])
        if not selected_agents:
            return state
        
        # 첫 번째 에이전트 실행 (실제로는 모든 에이전트를 병렬로 실행해야 함)
        current_agent = selected_agents[0]
        
        if current_agent in self.specialized_agents:
            logger.info(f"=== {current_agent.title()} Agent 실행 ===")
            agent_result = await self.specialized_agents[current_agent].execute_analysis_with_self_evaluation(state)
            state["agent_results"][current_agent] = agent_result
            state["messages"].append(AIMessage(content=f"{current_agent.title()} Agent: {agent_result['results']['self_evaluation']['feedback']}"))
        
        return state
    
    async def _synthesis_node(self, state: AgentState) -> Dict[str, Any]:
        """결과 종합 노드"""
        logger.info("=== Synthesis 실행 ===")
        
        # 모든 에이전트 결과 수집
        all_results = {}
        for agent_name, result in state.get("agent_results", {}).items():
            if result.get("status") == "success":
                all_results[agent_name] = result["results"]
        
        synthesis_result = {
            "synthesis_id": f"synthesis_{state['user_id']}_{int(datetime.now().timestamp())}",
            "user_query": state["user_query"],
            "main_agent_type": state.get("selected_main_agent"),
            "specialized_agents_used": state.get("selected_specialized_agents", []),
            "all_results": all_results,
            "synthesis_timestamp": datetime.now().isoformat()
        }
        
        state["synthesis_result"] = synthesis_result
        state["messages"].append(AIMessage(content="Synthesis: 모든 에이전트 결과 종합 완료"))
        return state
    
    async def _final_report_node(self, state: AgentState) -> Dict[str, Any]:
        """최종 보고서 생성 노드"""
        logger.info("=== Final Report 생성 ===")
        
        # 품질 점수 계산
        quality_scores = {}
        for agent_name, result in state.get("agent_results", {}).items():
            if result.get("status") == "success" and "self_evaluation" in result.get("results", {}):
                quality_scores[agent_name] = result["results"]["self_evaluation"]["quality_score"]
        
        final_report = {
            "report_id": f"report_{state['user_id']}_{int(datetime.now().timestamp())}",
            "user_query": state["user_query"],
            "main_agent_type": state.get("selected_main_agent"),
            "specialized_agents_used": state.get("selected_specialized_agents", []),
            "synthesis_result": state.get("synthesis_result", {}),
            "quality_scores": quality_scores,
            "overall_quality_score": sum(quality_scores.values()) / len(quality_scores) if quality_scores else 0.0,
            "generation_timestamp": datetime.now().isoformat()
        }
        
        state["final_report"] = final_report
        state["messages"].append(AIMessage(content=f"최종 보고서 생성 완료 - ID: {final_report['report_id']}"))
        return state
    
    # ==================== Main Execution Method ====================
    
    async def run_analysis(self, user_query: str, user_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        전체 분석 실행
        
        Args:
            user_query: 사용자 쿼리
            user_id: 사용자 ID
            context: 추가 컨텍스트
            
        Returns:
            분석 결과
        """
        initial_state = AgentState(
            user_query=user_query,
            user_id=user_id,
            session_id=f"session_{user_id}_{int(datetime.now().timestamp())}",
            context=context or {},
            messages=[HumanMessage(content=user_query)],
            current_plan=None,
            selected_main_agent=None,
            selected_specialized_agents=[],
            agent_results={},
            final_report=None,
            quality_score=0.0,
            iteration_count=0,
            max_iterations=3,
            memory_insights={},
            self_evaluation_score=0.0,
            self_evaluation_feedback="",
            should_loop=False
        )
        
        logger.info(f"분석 시작 - User: {user_id}, Query: {user_query}")
        
        try:
            result = await self.workflow.ainvoke(initial_state, config={"recursion_limit": 50})
            logger.info("분석 완료")
            return result
        except Exception as e:
            logger.error(f"분석 에러: {e}")
            return {"error": str(e)}


async def main():
    """메인 실행 함수"""
    print("="*80)
    print("2-Tier Orchestrator 멀티 에이전트 상권 분석 시스템")
    print("="*80)
    
    # 시스템 초기화
    system = MultiAgentSystem()
    
    # 테스트 케이스들
    test_cases = [
        {
            "query": "강남 20대 타겟 카페 창업 가능한가?",
            "user_id": "USER_001",
            "context": {"location": "강남구", "business_type": "cafe", "target_age": "20s"}
        },
        {
            "query": "우리 카페 마케팅 전략 좀 알려주세요",
            "user_id": "USER_002",
            "context": {"location": "홍대", "business_type": "cafe"}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*20} 테스트 케이스 {i} {'='*20}")
        print(f"쿼리: {test_case['query']}")
        print(f"사용자: {test_case['user_id']}")
        
        # 분석 실행
        result = await system.run_analysis(
            user_query=test_case["query"],
            user_id=test_case["user_id"],
            context=test_case["context"]
        )
        
        # 결과 출력
        if "error" in result:
            print(f"에러: {result['error']}")
        else:
            print(f"\n분석 완료!")
            print(f"최종 보고서 ID: {result.get('final_report', {}).get('report_id', 'N/A')}")
            print(f"메인 에이전트 타입: {result.get('selected_main_agent', 'N/A')}")
            print(f"사용된 전문 에이전트들: {result.get('selected_specialized_agents', [])}")
            print(f"품질 점수들: {result.get('final_report', {}).get('quality_scores', {})}")
            print(f"전체 품질 점수: {result.get('final_report', {}).get('overall_quality_score', 0):.2f}")
            
            # 실행된 에이전트들
            executed_agents = list(result.get('agent_results', {}).keys())
            print(f"실행된 에이전트들: {executed_agents}")
            
            # 메시지 히스토리
            messages = result.get("messages", [])
            print(f"\n메시지 히스토리 ({len(messages)}개):")
            for j, msg in enumerate(messages[-3:], 1):  # 마지막 3개만
                print(f"  {j}. {msg.content}")
    
    print(f"\n{'='*80}")
    print("2-Tier Orchestrator 멀티 에이전트 시스템 테스트 완료!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())