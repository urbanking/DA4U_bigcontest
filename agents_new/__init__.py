"""Agents module - AI 에이전트"""

import sys
from pathlib import Path

# 현재 디렉토리를 sys.path에 추가
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# google_map_mcp 모듈 경로 추가
google_map_mcp_path = current_dir / "google_map_mcp"
if str(google_map_mcp_path) not in sys.path:
    sys.path.insert(0, str(google_map_mcp_path))

__all__ = []
