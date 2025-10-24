"""
LangChain 기반 마케팅 에이전트 래퍼
기존 marketing_agent.py를 그대로 사용하되, 동기 실행 함수만 제공
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
print(f"[DEBUG] Loading .env from: {env_path}")
print(f"[DEBUG] GEMINI_API_KEY loaded: {'YES' if os.getenv('GEMINI_API_KEY') else 'NO'}")

# 기존 marketing_agent 사용
try:
    from .marketing_agent import marketingagent
except ImportError:
    from marketing_agent import marketingagent


def run_marketing_langchain_sync(store_code: str, output_dir: str, store_analysis: dict) -> dict:
    """
    동기 실행 래퍼 (기존 marketing_agent 활용)
    
    Args:
        store_code: 매장 코드
        output_dir: 출력 디렉토리  
        store_analysis: Store Agent 분석 결과
    
    Returns:
        dict: 마케팅 분석 결과
    """
    # 기존 marketingagent 사용
    agent = marketingagent(store_code=store_code)
    
    # 기존 run_marketing은 (store_report, diagnostic) 파라미터를 받음
    # store_analysis를 그대로 전달
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            agent.run_marketing(
                store_report=store_analysis,
                diagnostic=store_analysis  # diagnostic도 같은 데이터 사용
            )
        )
        
        # JSON 파일 저장 (기존 로직과 동일)
        import json
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 1. marketing_result.json (전체)
        result_file = output_path / "marketing_result.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"[OK] Saved: {result_file}")
        
        # 2. marketing_strategy.json (전략만)
        strategy_only = {
            "store_code": result.get("store_code"),
            "strategies": result.get("marketing_strategies", []),
            "campaign_plan": result.get("campaign_plan", {}),
            "timestamp": result.get("analysis_timestamp")
        }
        strategy_file = output_path / "marketing_strategy.json"
        with open(strategy_file, "w", encoding="utf-8") as f:
            json.dump(strategy_only, f, ensure_ascii=False, indent=2)
        print(f"[OK] Saved: {strategy_file}")
        
        return result
    finally:
        loop.close()


# 테스트용
if __name__ == "__main__":
    sample_analysis = {
        "store_name": "테스트 카페",
        "industry": "카페",
        "commercial_area": "역세권",
        "sales_trend": "증가",
        "male_ratio": 40,
        "female_ratio": 60,
        "main_age_group": "20대"
    }
    
    result = run_marketing_langchain_sync(
        store_code="TEST001",
        output_dir="./test_output",
        store_analysis=sample_analysis
    )
    
    print("\n[Test Result]")
    print(f"Store Code: {result.get('store_code')}")
    print(f"Persona: {result.get('persona_analysis', {}).get('persona_type')}")
    print(f"Strategies: {len(result.get('marketing_strategies', []))}개")
