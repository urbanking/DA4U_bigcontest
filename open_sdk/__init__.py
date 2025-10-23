"""
Open SDK - 통합 분석 파이프라인
Store Agent + Marketing Agent 직접 연결
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

__all__ = []
