"""
Base Agent Class
모든 에이전트의 기본 클래스 (LangGraph 호환)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from typing_extensions import TypedDict, Annotated
import logging
import asyncio
from datetime import datetime

# 메모리 시스템
from backend.memory.agent_memory import AgentMemoryManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """
    LangGraph 워크플로우에서 사용되는 에이전트 상태
    """
    user_query: str
    user_id: str
    session_id: str
    context: Dict[str, Any]
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    current_plan: Optional[Dict[str, Any]]
    selected_main_agent: Optional[str]  # "data_consulting" or "marketing"
    selected_specialized_agents: List[str]
    agent_results: Dict[str, Any]
    final_report: Optional[Dict[str, Any]]
    quality_score: float
    iteration_count: int
    max_iterations: int
    # 메모리 관련 필드
    memory_insights: Dict[str, Any]
    # 자가 평가 및 루프 관련 필드
    self_evaluation_score: float
    self_evaluation_feedback: str
    should_loop: bool


class BaseAgent(ABC):
    """
    모든 에이전트의 기본 클래스 (LangGraph 호환)
    """
    
    def __init__(self, agent_name: str, model: str = "gpt-4-turbo-preview", temperature: float = 0.7):
        """
        기본 에이전트 초기화
        
        Args:
            agent_name: 에이전트 이름
            model: OpenAI 모델명
            temperature: LLM 생성 온도
        """
        self.agent_name = agent_name
        self.model = model
        self.temperature = temperature
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        
        # 메모리 시스템 초기화
        self.memory_manager = None
        self._init_memory_manager()
        
        logger.info(f"{agent_name} 기본 에이전트 초기화 완료")
    
    def _init_memory_manager(self):
        """메모리 관리자 초기화"""
        try:
            self.memory_manager = AgentMemoryManager()
            logger.info(f"{self.agent_name} 메모리 시스템 초기화 완료")
        except ImportError as e:
            logger.warning(f"{self.agent_name} 메모리 시스템 초기화 실패: {e}")
            self.memory_manager = None
    
    async def load_user_memory(self, user_id: str, query: str) -> Dict[str, Any]:
        """
        사용자 메모리 로드
        
        Args:
            user_id: 사용자 ID
            query: 현재 쿼리
            
        Returns:
            메모리 기반 인사이트
        """
        if not self.memory_manager:
            return {"memory_available": False, "reason": "memory_manager_not_available"}
        
        try:
            return await self.memory_manager.load_user_memory(user_id, query)
        except Exception as e:
            logger.error(f"{self.agent_name} 메모리 로드 에러: {e}")
            return {"memory_available": False, "error": str(e)}
    
    async def save_to_memory(
        self, 
        user_id: str, 
        session_id: str, 
        analysis_result: Dict[str, Any], 
        evaluation_scores: Dict[str, float]
    ):
        """
        분석 결과를 메모리에 저장
        
        Args:
            user_id: 사용자 ID
            session_id: 세션 ID
            analysis_result: 분석 결과
            evaluation_scores: 평가 점수
        """
        if not self.memory_manager:
            logger.warning(f"{self.agent_name} 메모리 저장 건너뜀 - 메모리 관리자 없음")
            return
        
        try:
            await self.memory_manager.save_analysis_result(
                user_id, session_id, analysis_result, evaluation_scores
            )
            logger.info(f"{self.agent_name} 메모리 저장 완료")
        except Exception as e:
            logger.error(f"{self.agent_name} 메모리 저장 에러: {e}")
    
    @abstractmethod
    async def execute_analysis_with_self_evaluation(self, state: AgentState) -> Dict[str, Any]:
        """
        LangGraph 노드에서 호출되는 메인 분석 메서드
        자가 평가와 품질 점수 포함
        
        Args:
            state: LangGraph 워크플로우의 현재 상태
            
        Returns:
            분석 결과, 자가 평가, 품질 점수를 포함한 딕셔너리
        """
        pass
    
    def create_prompt(self, template: str, variables: Dict[str, Any]) -> ChatPromptTemplate:
        """
        변수가 포함된 프롬프트 템플릿 생성
        
        Args:
            template: 프롬프트 템플릿 문자열
            variables: 주입할 변수들
            
        Returns:
            ChatPromptTemplate 인스턴스
        """
        return ChatPromptTemplate.from_template(template).format(**variables)
    
    def invoke_llm(self, prompt: str) -> str:
        """
        LLM 호출
        
        Args:
            prompt: 프롬프트 문자열
            
        Returns:
            LLM 응답 문자열
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"{self.agent_name} LLM 호출 실패: {e}")
            raise
    
    def format_output(self, **kwargs) -> Dict[str, Any]:
        """
        표준화된 출력 구조로 포맷팅
        
        Returns:
            표준화된 출력 딕셔너리
        """
        return {
            "agent_name": self.agent_name,
            "status": "success",
            "results": kwargs,
            "metadata": {
                "model": self.model,
                "temperature": self.temperature,
                "timestamp": str(datetime.now())
            }
        }
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        에러 처리 및 에러 출력 반환
        
        Args:
            error: 발생한 예외
            
        Returns:
            에러 출력 딕셔너리
        """
        logger.error(f"{self.agent_name} 에러 발생: {error}")
        return {
            "agent_name": self.agent_name,
            "status": "error",
            "error": str(error),
            "results": {},
            "metadata": {
                "model": self.model,
                "temperature": self.temperature,
                "timestamp": str(datetime.now())
            }
        }
    
    def get_memory_status(self) -> Dict[str, Any]:
        """메모리 시스템 상태 반환"""
        return {
            "agent_name": self.agent_name,
            "memory_enabled": self.memory_manager is not None,
            "memory_type": "장단기 메모리 시스템"
        }
