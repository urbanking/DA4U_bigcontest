"""
로깅 설정
"""
import logging
import sys
from backend.core.config import settings

# 로거 설정
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("bigcontest_ai_agent")

