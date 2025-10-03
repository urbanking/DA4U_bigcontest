"""
Sequential Thinking MCP 클라이언트
실제 Sequential Thinking MCP 서버와 통신하는 클라이언트
"""

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from urllib.parse import urlencode
import asyncio
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class SequentialThinkingClient:
    """
    Sequential Thinking MCP 클라이언트
    실제 Sequential Thinking MCP 서버와 통신
    """
    
    def __init__(self, api_key: str = "d52a2502-98a5-452f-9ce7-65f507929073", profile: str = "adamant-scooter-KKhQcw"):
        """
        Sequential Thinking MCP 클라이언트 초기화
        
        Args:
            api_key: Smithery API 키
            profile: 프로필 이름
        """
        self.api_key = api_key
        self.profile = profile
        self.base_url = "https://server.smithery.ai/@smithery-ai/server-sequential-thinking/mcp"
        self.logger = logging.getLogger(__name__)
        
        # URL 구성
        params = {"api_key": self.api_key, "profile": self.profile}
        self.url = f"{self.base_url}?{urlencode(params)}"
        
        self.logger.info("Sequential Thinking MCP 클라이언트 초기화 완료")
    
    async def sequential_thinking(
        self,
        problem_description: str,
        initial_thoughts: int = 5,
        max_iterations: int = 10
    ) -> Dict[str, Any]:
        """
        Sequential Thinking을 사용한 문제 해결
        
        Args:
            problem_description: 해결할 문제 설명
            initial_thoughts: 초기 사고 단계 수
            max_iterations: 최대 반복 횟수
            
        Returns:
            Sequential Thinking 결과
        """
        try:
            async with streamablehttp_client(self.url) as (read, write, _):
                async with ClientSession(read, write) as session:
                    # 연결 초기화
                    await session.initialize()
                    
                    # 사용 가능한 도구 확인
                    tools_result = await session.list_tools()
                    self.logger.info(f"Available tools: {', '.join([t.name for t in tools_result.tools])}")
                    
                    # Sequential Thinking 실행
                    thought_history = []
                    current_thought = 1
                    total_thoughts = initial_thoughts
                    next_thought_needed = True
                    iteration_count = 0
                    
                    while next_thought_needed and iteration_count < max_iterations:
                        # 현재 사고 단계 구성
                        if current_thought == 1:
                            thought_content = f"""
                            문제 분석 시작: {problem_description}
                            
                            이 문제를 해결하기 위해 다음과 같이 접근하겠습니다:
                            1. 문제의 핵심 파악
                            2. 관련 요소들 분석
                            3. 가능한 해결책 탐색
                            4. 최적 해결책 선택
                            5. 실행 계획 수립
                            """
                        else:
                            # 이전 사고들을 바탕으로 다음 사고 생성
                            previous_thoughts = "\n".join([f"사고 {i+1}: {thought}" for i, thought in enumerate(thought_history[-3:])])
                            thought_content = f"""
                            이전 사고들을 바탕으로 계속 분석합니다:
                            
                            {previous_thoughts}
                            
                            다음 단계로 진행하면서 추가로 고려해야 할 점들을 분석하겠습니다.
                            """
                        
                        # Sequential Thinking 도구 호출
                        result = await session.call_tool(
                            "sequentialthinking",
                            arguments={
                                "thought": thought_content,
                                "thoughtNumber": current_thought,
                                "totalThoughts": total_thoughts,
                                "nextThoughtNeeded": current_thought < total_thoughts,
                                "isRevision": False,
                                "needsMoreThoughts": current_thought >= total_thoughts and iteration_count < max_iterations - 1
                            }
                        )
                        
                        # 결과 처리
                        if result.content:
                            thought_result = result.content[0].text if result.content else ""
                            thought_history.append(thought_result)
                            
                            self.logger.info(f"사고 단계 {current_thought} 완료")
                            
                            # 다음 사고가 필요한지 확인
                            if current_thought >= total_thoughts:
                                if iteration_count < max_iterations - 1:
                                    # 더 많은 사고가 필요한지 사용자에게 확인
                                    # 여기서는 자동으로 계속 진행
                                    total_thoughts += 2
                                    next_thought_needed = True
                                else:
                                    next_thought_needed = False
                            else:
                                current_thought += 1
                                next_thought_needed = True
                        else:
                            self.logger.warning(f"사고 단계 {current_thought}에서 결과가 없음")
                            next_thought_needed = False
                        
                        iteration_count += 1
                    
                    return {
                        "status": "success",
                        "problem_description": problem_description,
                        "thought_history": thought_history,
                        "total_thoughts": len(thought_history),
                        "iterations": iteration_count,
                        "final_analysis": thought_history[-1] if thought_history else "분석 완료",
                        "mcp_tool_used": "sequentialthinking"
                    }
                    
        except Exception as e:
            self.logger.error(f"Sequential Thinking MCP 에러: {e}")
            return {
                "status": "error",
                "error": str(e),
                "problem_description": problem_description,
                "fallback_result": "Sequential Thinking MCP를 사용할 수 없어 기본 분석을 수행합니다."
            }
    
    async def quick_thinking(
        self,
        problem_description: str,
        thought_count: int = 3
    ) -> Dict[str, Any]:
        """
        빠른 Sequential Thinking (간단한 문제용)
        
        Args:
            problem_description: 해결할 문제 설명
            thought_count: 사고 단계 수
            
        Returns:
            빠른 Sequential Thinking 결과
        """
        return await self.sequential_thinking(
            problem_description=problem_description,
            initial_thoughts=thought_count,
            max_iterations=thought_count
        )
    
    async def deep_thinking(
        self,
        problem_description: str,
        initial_thoughts: int = 8,
        max_iterations: int = 15
    ) -> Dict[str, Any]:
        """
        깊은 Sequential Thinking (복잡한 문제용)
        
        Args:
            problem_description: 해결할 문제 설명
            initial_thoughts: 초기 사고 단계 수
            max_iterations: 최대 반복 횟수
            
        Returns:
            깊은 Sequential Thinking 결과
        """
        return await self.sequential_thinking(
            problem_description=problem_description,
            initial_thoughts=initial_thoughts,
            max_iterations=max_iterations
        )


# 전역 클라이언트 인스턴스
_sequential_thinking_client = None


def get_sequential_thinking_client() -> SequentialThinkingClient:
    """
    Sequential Thinking 클라이언트 싱글톤 인스턴스 반환
    
    Returns:
        SequentialThinkingClient 인스턴스
    """
    global _sequential_thinking_client
    if _sequential_thinking_client is None:
        _sequential_thinking_client = SequentialThinkingClient()
    return _sequential_thinking_client


# 편의 함수들
async def quick_sequential_thinking(problem_description: str) -> Dict[str, Any]:
    """빠른 Sequential Thinking 실행"""
    client = get_sequential_thinking_client()
    return await client.quick_thinking(problem_description)


async def deep_sequential_thinking(problem_description: str) -> Dict[str, Any]:
    """깊은 Sequential Thinking 실행"""
    client = get_sequential_thinking_client()
    return await client.deep_thinking(problem_description)


async def custom_sequential_thinking(
    problem_description: str,
    initial_thoughts: int = 5,
    max_iterations: int = 10
) -> Dict[str, Any]:
    """커스텀 Sequential Thinking 실행"""
    client = get_sequential_thinking_client()
    return await client.sequential_thinking(problem_description, initial_thoughts, max_iterations)


if __name__ == "__main__":
    # 테스트
    async def test_sequential_thinking():
        """Sequential Thinking 테스트"""
        
        client = SequentialThinkingClient()
        
        # 빠른 테스트
        print("=== 빠른 Sequential Thinking 테스트 ===")
        result = await client.quick_thinking("카페 창업을 위한 상권 분석 계획을 수립해주세요")
        print(f"상태: {result['status']}")
        print(f"총 사고 단계: {result['total_thoughts']}")
        print(f"반복 횟수: {result['iterations']}")
        print(f"최종 분석: {result['final_analysis'][:200]}...")
        
        # 깊은 테스트
        print("\n=== 깊은 Sequential Thinking 테스트 ===")
        result = await client.deep_thinking("강남구 20대 타겟 카페 창업의 성공 가능성을 종합적으로 분석해주세요")
        print(f"상태: {result['status']}")
        print(f"총 사고 단계: {result['total_thoughts']}")
        print(f"반복 횟수: {result['iterations']}")
        print(f"최종 분석: {result['final_analysis'][:200]}...")
    
    asyncio.run(test_sequential_thinking())
