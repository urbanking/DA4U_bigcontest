"""
FastAPI용 파이프라인 컨트롤러
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from .orchestrator_agent import OrchestratorAgent


class PipelineController:
    """파이프라인 컨트롤러"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.orchestrator = OrchestratorAgent()
        self.pipeline_status = {}  # store_code -> status
    
    async def start_pipeline(self, store_code: str) -> Dict[str, Any]:
        """파이프라인 시작"""
        self.pipeline_status[store_code] = "running"
        
        try:
            result = await self.orchestrator.run(store_code)
            self.pipeline_status[store_code] = "completed"
            return result
        except Exception as e:
            self.pipeline_status[store_code] = "failed"
            raise e
    
    def get_status(self, store_code: str) -> str:
        """파이프라인 상태 조회"""
        return self.pipeline_status.get(store_code, "idle")
    
    async def cancel_pipeline(self, store_code: str):
        """파이프라인 취소"""
        self.pipeline_status[store_code] = "cancelled"
        # TODO: 실행 중인 워크플로우 취소 로직

