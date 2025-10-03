"""
Figma MCP 클라이언트
Figma와 Cursor를 MCP를 통해 연동하는 클라이언트
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from mcp import ClientSession
from mcp.client.stdio import stdio_client
import json
import os

logger = logging.getLogger(__name__)


class FigmaMCPClient:
    """
    Figma MCP 클라이언트
    Figma 디자인 파일과 상호작용을 위한 MCP 클라이언트
    """
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Figma MCP 클라이언트 초기화
        
        Args:
            access_token: Figma Personal Access Token
        """
        self.access_token = access_token or os.getenv('FIGMA_ACCESS_TOKEN')
        self.logger = logging.getLogger(__name__)
        
        if not self.access_token:
            self.logger.warning("FIGMA_ACCESS_TOKEN이 설정되지 않았습니다.")
    
    async def _get_session(self):
        """MCP 세션 생성"""
        try:
            # 환경변수 설정
            env = {}
            if self.access_token:
                env['FIGMA_ACCESS_TOKEN'] = self.access_token
            
            async with stdio_client("npx", "@figma/mcp-server", env=env) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return session
        except Exception as e:
            self.logger.error(f"Figma MCP 세션 생성 실패: {e}")
            raise
    
    async def get_file_info(self, file_key: str) -> Dict[str, Any]:
        """
        Figma 파일 정보 가져오기
        
        Args:
            file_key: Figma 파일 키
            
        Returns:
            파일 정보
        """
        try:
            async with self._get_session() as session:
                result = await session.call_tool(
                    "get_file_info",
                    arguments={"file_key": file_key}
                )
                return {
                    "status": "success",
                    "file_key": file_key,
                    "data": result.content[0].text if result.content else None
                }
        except Exception as e:
            self.logger.error(f"파일 정보 가져오기 실패: {e}")
            return {
                "status": "error",
                "error": str(e),
                "file_key": file_key
            }
    
    async def get_components(self, file_key: str) -> Dict[str, Any]:
        """
        파일의 컴포넌트 목록 가져오기
        
        Args:
            file_key: Figma 파일 키
            
        Returns:
            컴포넌트 목록
        """
        try:
            async with self._get_session() as session:
                result = await session.call_tool(
                    "get_components",
                    arguments={"file_key": file_key}
                )
                return {
                    "status": "success",
                    "file_key": file_key,
                    "components": result.content[0].text if result.content else None
                }
        except Exception as e:
            self.logger.error(f"컴포넌트 목록 가져오기 실패: {e}")
            return {
                "status": "error",
                "error": str(e),
                "file_key": file_key
            }
    
    async def get_design_tokens(self, file_key: str) -> Dict[str, Any]:
        """
        디자인 토큰 추출
        
        Args:
            file_key: Figma 파일 키
            
        Returns:
            디자인 토큰
        """
        try:
            async with self._get_session() as session:
                result = await session.call_tool(
                    "get_design_tokens",
                    arguments={"file_key": file_key}
                )
                return {
                    "status": "success",
                    "file_key": file_key,
                    "tokens": result.content[0].text if result.content else None
                }
        except Exception as e:
            self.logger.error(f"디자인 토큰 추출 실패: {e}")
            return {
                "status": "error",
                "error": str(e),
                "file_key": file_key
            }
    
    async def take_screenshot(self, file_key: str, node_id: str) -> Dict[str, Any]:
        """
        특정 노드의 스크린샷 생성
        
        Args:
            file_key: Figma 파일 키
            node_id: 노드 ID
            
        Returns:
            스크린샷 정보
        """
        try:
            async with self._get_session() as session:
                result = await session.call_tool(
                    "take_screenshot",
                    arguments={
                        "file_key": file_key,
                        "node_id": node_id
                    }
                )
                return {
                    "status": "success",
                    "file_key": file_key,
                    "node_id": node_id,
                    "screenshot": result.content[0].text if result.content else None
                }
        except Exception as e:
            self.logger.error(f"스크린샷 생성 실패: {e}")
            return {
                "status": "error",
                "error": str(e),
                "file_key": file_key,
                "node_id": node_id
            }
    
    async def get_available_tools(self) -> Dict[str, Any]:
        """
        사용 가능한 Figma MCP 도구 목록 가져오기
        
        Returns:
            도구 목록
        """
        try:
            async with self._get_session() as session:
                tools_result = await session.list_tools()
                tools = [tool.name for tool in tools_result.tools]
                return {
                    "status": "success",
                    "tools": tools,
                    "count": len(tools)
                }
        except Exception as e:
            self.logger.error(f"도구 목록 가져오기 실패: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


# 전역 클라이언트 인스턴스
_figma_client = None


def get_figma_client(access_token: Optional[str] = None) -> FigmaMCPClient:
    """
    Figma MCP 클라이언트 싱글톤 인스턴스 반환
    
    Args:
        access_token: Figma Personal Access Token
        
    Returns:
        FigmaMCPClient 인스턴스
    """
    global _figma_client
    if _figma_client is None:
        _figma_client = FigmaMCPClient(access_token)
    return _figma_client


# 편의 함수들
async def get_figma_file_info(file_key: str, access_token: Optional[str] = None) -> Dict[str, Any]:
    """Figma 파일 정보 가져오기"""
    client = get_figma_client(access_token)
    return await client.get_file_info(file_key)


async def get_figma_components(file_key: str, access_token: Optional[str] = None) -> Dict[str, Any]:
    """Figma 컴포넌트 목록 가져오기"""
    client = get_figma_client(access_token)
    return await client.get_components(file_key)


async def get_figma_design_tokens(file_key: str, access_token: Optional[str] = None) -> Dict[str, Any]:
    """Figma 디자인 토큰 추출"""
    client = get_figma_client(access_token)
    return await client.get_design_tokens(file_key)


async def take_figma_screenshot(file_key: str, node_id: str, access_token: Optional[str] = None) -> Dict[str, Any]:
    """Figma 스크린샷 생성"""
    client = get_figma_client(access_token)
    return await client.take_screenshot(file_key, node_id)


if __name__ == "__main__":
    # 테스트
    async def test_figma_mcp():
        """Figma MCP 테스트"""
        
        # 환경변수에서 토큰 가져오기
        access_token = os.getenv('FIGMA_ACCESS_TOKEN')
        if not access_token:
            print("FIGMA_ACCESS_TOKEN 환경변수를 설정해주세요.")
            return
        
        client = FigmaMCPClient(access_token)
        
        # 사용 가능한 도구 확인
        print("=== 사용 가능한 Figma MCP 도구 ===")
        tools_result = await client.get_available_tools()
        print(f"상태: {tools_result['status']}")
        if tools_result['status'] == 'success':
            print(f"도구 목록: {tools_result['tools']}")
        
        # 파일 정보 테스트 (실제 파일 키로 교체 필요)
        test_file_key = "YOUR_FIGMA_FILE_KEY"
        print(f"\n=== 파일 정보 테스트 (파일 키: {test_file_key}) ===")
        file_info = await client.get_file_info(test_file_key)
        print(f"상태: {file_info['status']}")
        if file_info['status'] == 'success':
            print("파일 정보를 성공적으로 가져왔습니다.")
        else:
            print(f"오류: {file_info.get('error', '알 수 없는 오류')}")
    
    asyncio.run(test_figma_mcp())

