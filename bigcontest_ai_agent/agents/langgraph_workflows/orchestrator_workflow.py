"""
전체 파이프라인 (Store → Marketing) 오케스트레이터
"""
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from operator import add


class OrchestratorState(TypedDict):
    """오케스트레이터 상태"""
    store_code: str
    store_workflow_result: dict
    marketing_workflow_result: dict
    final_result: dict
    errors: Annotated[list, add]


def create_orchestrator_workflow() -> StateGraph:
    """오케스트레이터 워크플로우 생성"""
    workflow = StateGraph(OrchestratorState)
    
    # 노드 추가
    workflow.add_node("run_store_workflow", run_store_workflow_node)
    workflow.add_node("run_marketing_workflow", run_marketing_workflow_node)
    workflow.add_node("finalize", finalize_node)
    
    # 엣지 설정
    workflow.set_entry_point("run_store_workflow")
    workflow.add_edge("run_store_workflow", "run_marketing_workflow")
    workflow.add_edge("run_marketing_workflow", "finalize")
    workflow.add_edge("finalize", END)
    
    return workflow.compile()


def run_store_workflow_node(state: OrchestratorState) -> OrchestratorState:
    """Store 워크플로우 실행 노드"""
    # TODO: Store 워크플로우 실행
    state["store_workflow_result"] = {"status": "completed"}
    return state


def run_marketing_workflow_node(state: OrchestratorState) -> OrchestratorState:
    """Marketing 워크플로우 실행 노드"""
    # TODO: Marketing 워크플로우 실행
    state["marketing_workflow_result"] = {"status": "completed"}
    return state


def finalize_node(state: OrchestratorState) -> OrchestratorState:
    """최종 결과 취합 노드"""
    state["final_result"] = {
        "store": state["store_workflow_result"],
        "marketing": state["marketing_workflow_result"]
    }
    return state

