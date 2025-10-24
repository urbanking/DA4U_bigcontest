"""
LangChain Marketing Agent 동기 실행 래퍼
기존 모듈(legacy marketing.py)을 직접 사용하지 않고,
LangChain 러너(marketing_agent_langchain.py)의 run_marketing_langchain_sync를 호출합니다.
agents_new/.env에서 GEMINI_API_KEY를 로드합니다.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env 로드 (agents_new/.env)
ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)
print(f"[Marketing-LangChain] .env loaded from {ENV_PATH} | GEMINI_API_KEY set: {'YES' if os.getenv('GEMINI_API_KEY') else 'NO'}")

# 새 LangChain 러너 사용 (legacy로 위임하지 않음)
try:
    from .marketing_agent_langchain import run_marketing_langchain_sync as _run_runner
except ImportError:
    from marketing_agent_langchain import run_marketing_langchain_sync as _run_runner


def run_marketing_sync_langchain(store_code: str, output_dir: str, store_analysis: dict) -> dict:
    """
    LangChain 래퍼 진입점 (내부적으로 기존 run_marketing_sync를 그대로 호출)

    Args:
        store_code: 매장 코드
        output_dir: 출력 디렉토리
        store_analysis: Store Agent 분석 결과

    Returns:
        dict: 마케팅 분석 결과 (JSON 2개 저장 포함)
    """
    return _run_runner(store_code, output_dir, store_analysis)
