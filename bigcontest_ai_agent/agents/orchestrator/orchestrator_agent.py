"""
LangGraph 실행 관리
"""
from typing import Dict, Any
from agents.langgraph_workflows.orchestrator_workflow import create_orchestrator_workflow


class OrchestratorAgent:
    """오케스트레이터 에이전트"""
    
    def __init__(self):
        self.workflow = create_orchestrator_workflow()
    
    async def run(self, store_code: str) -> Dict[str, Any]:
        """전체 파이프라인 실행"""
        initial_state = {
            "store_code": store_code,
            "store_workflow_result": {},
            "marketing_workflow_result": {},
            "final_result": {},
            "errors": []
        }
        
        # LangGraph 워크플로우 실행
        result = await self.workflow.ainvoke(initial_state)
        
        return result
    
    async def run_partial(
        self,
        store_code: str,
        steps: list
    ) -> Dict[str, Any]:
        """부분 실행"""
        # TODO: 특정 스텝만 실행
        return {}

