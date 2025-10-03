"""
FastAPI 백엔드 메인 서버
멀티 에이전트 상권 분석 시스템 API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import logging
from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from workflow.langgraph_workflow import MultiAgentWorkflow
from backend.memory.agent_memory import AgentMemoryManager
from backend.evaluation.evaluation_system import EvaluationSystem
from backend.mcp.sequential_thinking import SequentialThinkingMCP

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-Agent Commercial District Analysis API",
    description="멀티 에이전트 기반 상권 분석 시스템",
    version="2.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서만 사용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 글로벌 컴포넌트 초기화
workflow = MultiAgentWorkflow()
memory_manager = AgentMemoryManager()
evaluation_system = EvaluationSystem()
sequential_thinking = SequentialThinkingMCP()


class AnalysisRequest(BaseModel):
    """분석 요청 모델"""
    user_query: str
    user_id: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class AnalysisResponse(BaseModel):
    """분석 응답 모델"""
    session_id: str
    status: str
    current_step: str
    progress: float
    agent_results: Dict[str, Any]
    final_report: Optional[Dict[str, Any]] = None
    evaluation_scores: Optional[Dict[str, float]] = None
    memory_insights: Optional[Dict[str, Any]] = None


@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "Multi-Agent Commercial District Analysis API",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "components": {
            "workflow": "active",
            "memory": memory_manager.is_healthy(),
            "evaluation": evaluation_system.is_healthy(),
            "sequential_thinking": sequential_thinking.is_healthy()
        }
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_commercial_district(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    상권 분석 실행
    
    Args:
        request: 분석 요청 데이터
        background_tasks: 백그라운드 태스크
        
    Returns:
        분석 결과
    """
    try:
        session_id = request.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"분석 요청 시작 - Session: {session_id}, User: {request.user_id}")
        
        # 1. 이전 분석 결과 로드 (메모리 시스템)
        memory_insights = await memory_manager.load_user_memory(
            request.user_id, 
            request.user_query
        )
        
        # 2. Sequential Thinking을 통한 계획 수립
        thinking_result = await sequential_thinking.plan_analysis(
            request.user_query,
            memory_insights
        )
        
        # 3. LangGraph 워크플로우 실행
        workflow_result = workflow.run(
            request.user_query,
            request.user_id
        )
        
        # 4. 결과 평가
        evaluation_scores = await evaluation_system.evaluate_results(
            workflow_result,
            request.user_query
        )
        
        # 5. 메모리에 결과 저장 (백그라운드)
        background_tasks.add_task(
            memory_manager.save_analysis_result,
            request.user_id,
            session_id,
            workflow_result,
            evaluation_scores
        )
        
        # 6. 응답 구성
        response = AnalysisResponse(
            session_id=session_id,
            status="completed",
            current_step=workflow_result.get("current_step", "unknown"),
            progress=100.0,
            agent_results=workflow_result.get("agent_results", {}),
            final_report=workflow_result.get("final_report"),
            evaluation_scores=evaluation_scores,
            memory_insights=memory_insights
        )
        
        logger.info(f"분석 완료 - Session: {session_id}")
        return response
        
    except Exception as e:
        logger.error(f"분석 실행 중 에러: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analysis/{session_id}")
async def get_analysis_result(session_id: str):
    """분석 결과 조회"""
    try:
        result = await memory_manager.get_analysis_result(session_id)
        if not result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return result
    except Exception as e:
        logger.error(f"분석 결과 조회 에러: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user/{user_id}/history")
async def get_user_history(user_id: str, limit: int = 10):
    """사용자 분석 히스토리 조회"""
    try:
        history = await memory_manager.get_user_history(user_id, limit)
        return {"user_id": user_id, "history": history}
    except Exception as e:
        logger.error(f"사용자 히스토리 조회 에러: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/status")
async def get_agents_status():
    """에이전트 상태 조회"""
    try:
        status = {
            "workflow_agents": workflow.get_agent_status(),
            "memory_status": memory_manager.get_status(),
            "evaluation_status": evaluation_system.get_status()
        }
        return status
    except Exception as e:
        logger.error(f"에이전트 상태 조회 에러: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluation/feedback")
async def submit_evaluation_feedback(
    session_id: str,
    feedback: Dict[str, Any]
):
    """평가 피드백 제출"""
    try:
        result = await evaluation_system.submit_feedback(
            session_id, 
            feedback
        )
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"피드백 제출 에러: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
