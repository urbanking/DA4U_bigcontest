"""
BigContest AI Agent - 프로젝트 루트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

__version__ = "1.0.0"
__all__ = []
