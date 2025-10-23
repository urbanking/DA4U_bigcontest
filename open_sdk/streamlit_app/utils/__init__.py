"""
Streamlit 앱의 유틸리티 모듈
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 모듈 임포트
try:
    from .store_search_processor import StoreSearchProcessor
    __all__ = ['StoreSearchProcessor']
except ImportError as e:
    print(f"Warning: Could not import StoreSearchProcessor: {e}")
    __all__ = []
