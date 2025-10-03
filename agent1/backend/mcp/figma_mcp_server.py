"""
Figma MCP 서버
Figma API와 통신하는 MCP 서버 구현
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
import aiohttp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Figma API 설정
FIGMA_API_BASE = "https://api.figma.com/v1"


class FigmaMCPServer:
    """Figma MCP 서버"""
    
    def __init__(self):
        self.server = Server("figma-mcp-server")
        self.access_token = os.getenv('FIGMA_ACCESS_TOKEN')
        self.session = None
        
        # 도구 등록
        self._register_tools()
    
    def _register_tools(self):
        """MCP 도구들 등록"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """사용 가능한 도구 목록 반환"""
            return [
                Tool(
                    name="get_file_info",
                    description="Figma 파일의 기본 정보를 가져옵니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_key": {
                                "type": "string",
                                "description": "Figma 파일 키"
                            }
                        },
                        "required": ["file_key"]
                    }
                ),
                Tool(
                    name="get_file_nodes",
                    description="Figma 파일의 노드 구조를 가져옵니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_key": {
                                "type": "string",
                                "description": "Figma 파일 키"
                            },
                            "node_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "가져올 노드 ID들 (선택사항)"
                            }
                        },
                        "required": ["file_key"]
                    }
                ),
                Tool(
                    name="get_components",
                    description="Figma 파일의 컴포넌트 목록을 가져옵니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_key": {
                                "type": "string",
                                "description": "Figma 파일 키"
                            }
                        },
                        "required": ["file_key"]
                    }
                ),
                Tool(
                    name="get_styles",
                    description="Figma 파일의 스타일 목록을 가져옵니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_key": {
                                "type": "string",
                                "description": "Figma 파일 키"
                            }
                        },
                        "required": ["file_key"]
                    }
                ),
                Tool(
                    name="get_images",
                    description="Figma 파일의 이미지를 가져옵니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_key": {
                                "type": "string",
                                "description": "Figma 파일 키"
                            },
                            "node_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "이미지를 가져올 노드 ID들"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["jpg", "png", "svg", "pdf"],
                                "description": "이미지 포맷"
                            }
                        },
                        "required": ["file_key", "node_ids"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """도구 호출 처리"""
            try:
                if name == "get_file_info":
                    return await self._get_file_info(arguments)
                elif name == "get_file_nodes":
                    return await self._get_file_nodes(arguments)
                elif name == "get_components":
                    return await self._get_components(arguments)
                elif name == "get_styles":
                    return await self._get_styles(arguments)
                elif name == "get_images":
                    return await self._get_images(arguments)
                else:
                    return [TextContent(type="text", text=f"알 수 없는 도구: {name}")]
            except Exception as e:
                logger.error(f"도구 호출 오류 ({name}): {e}")
                return [TextContent(type="text", text=f"오류: {str(e)}")]
    
    async def _get_session(self):
        """HTTP 세션 생성"""
        if not self.session:
            headers = {}
            if self.access_token:
                headers["X-Figma-Token"] = self.access_token
            
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Figma API 요청"""
        session = await self._get_session()
        url = f"{FIGMA_API_BASE}{endpoint}"
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"API 오류 ({response.status}): {error_text}")
        except Exception as e:
            logger.error(f"API 요청 실패: {e}")
            raise
    
    async def _get_file_info(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """파일 정보 가져오기"""
        file_key = arguments["file_key"]
        
        try:
            data = await self._make_request(f"/files/{file_key}")
            
            result = {
                "name": data.get("name", ""),
                "lastModified": data.get("lastModified", ""),
                "thumbnailUrl": data.get("thumbnailUrl", ""),
                "version": data.get("version", ""),
                "role": data.get("role", ""),
                "editorType": data.get("editorType", ""),
                "linkAccess": data.get("linkAccess", ""),
                "document": {
                    "id": data.get("document", {}).get("id", ""),
                    "name": data.get("document", {}).get("name", ""),
                    "type": data.get("document", {}).get("type", "")
                } if data.get("document") else None
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"파일 정보 가져오기 실패: {str(e)}")]
    
    async def _get_file_nodes(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """파일 노드 구조 가져오기"""
        file_key = arguments["file_key"]
        node_ids = arguments.get("node_ids")
        
        try:
            params = {}
            if node_ids:
                params["ids"] = ",".join(node_ids)
            
            data = await self._make_request(f"/files/{file_key}/nodes", params)
            
            return [TextContent(type="text", text=json.dumps(data, indent=2, ensure_ascii=False))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"노드 구조 가져오기 실패: {str(e)}")]
    
    async def _get_components(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """컴포넌트 목록 가져오기"""
        file_key = arguments["file_key"]
        
        try:
            data = await self._make_request(f"/files/{file_key}/components")
            
            components = []
            for component_id, component_data in data.get("meta", {}).get("components", {}).items():
                components.append({
                    "id": component_id,
                    "name": component_data.get("name", ""),
                    "description": component_data.get("description", ""),
                    "key": component_data.get("key", ""),
                    "remote": component_data.get("remote", False),
                    "thumbnailUrl": component_data.get("thumbnailUrl", "")
                })
            
            return [TextContent(type="text", text=json.dumps(components, indent=2, ensure_ascii=False))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"컴포넌트 목록 가져오기 실패: {str(e)}")]
    
    async def _get_styles(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """스타일 목록 가져오기"""
        file_key = arguments["file_key"]
        
        try:
            data = await self._make_request(f"/files/{file_key}/styles")
            
            styles = []
            for style_id, style_data in data.get("meta", {}).get("styles", {}).items():
                styles.append({
                    "id": style_id,
                    "name": style_data.get("name", ""),
                    "description": style_data.get("description", ""),
                    "key": style_data.get("key", ""),
                    "styleType": style_data.get("styleType", ""),
                    "thumbnailUrl": style_data.get("thumbnailUrl", "")
                })
            
            return [TextContent(type="text", text=json.dumps(styles, indent=2, ensure_ascii=False))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"스타일 목록 가져오기 실패: {str(e)}")]
    
    async def _get_images(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """이미지 가져오기"""
        file_key = arguments["file_key"]
        node_ids = arguments["node_ids"]
        format_type = arguments.get("format", "png")
        
        try:
            params = {
                "ids": ",".join(node_ids),
                "format": format_type
            }
            
            data = await self._make_request(f"/images/{file_key}", params)
            
            return [TextContent(type="text", text=json.dumps(data, indent=2, ensure_ascii=False))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"이미지 가져오기 실패: {str(e)}")]
    
    async def run(self):
        """MCP 서버 실행"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """메인 함수"""
    server = FigmaMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())

