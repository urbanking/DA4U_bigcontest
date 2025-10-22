"""
Simple Store Agent Test - 간단한 테스트 스크립트
"""
import asyncio
import sys
from pathlib import Path

# 경로 추가
sys.path.insert(0, str(Path(__file__).parent / "report_builder"))

from store_agent_module import StoreAgentModule, StoreAgentState

async def test_store_analysis():
    """매장 분석 간단 테스트"""
    print("="*60)
    print("Store Agent Test")
    print("="*60)
    
    # 1. 초기화
    print("\n[1] Initializing...")
    agent = StoreAgentModule()
    print(f"OK - Data path: {agent.data_path}")
    
    # 2. State 준비
    print("\n[2] Preparing state...")
    state: StoreAgentState = {
        "user_query": "000F03E44A store analysis",
        "user_id": "test_user",
        "session_id": "test_001",
        "context": {},
        "store_analysis": None,
        "error": None
    }
    print("OK - State ready")
    
    # 3. 분석 실행
    print("\n[3] Running analysis...")
    print("-"*60)
    result = await agent.execute_analysis_with_self_evaluation(state)
    print("-"*60)
    
    # 4. 결과 확인
    print("\n[4] Results:")
    if result["error"]:
        print(f"ERROR: {result['error']}")
        return
    
    print("SUCCESS!")
    analysis = result["store_analysis"]
    
    print(f"\nStore Code: {analysis['store_code']}")
    print(f"Quality Score: {analysis['evaluation']['quality_score']:.2%}")
    
    # 매장 개요
    overview = analysis['analysis_result']['store_overview']
    print(f"\nStore Name: {overview['name']}")
    print(f"Address: {overview['address']}")
    print(f"Industry: {overview['industry']}")
    print(f"Operating Months: {overview['operating_months']:.1f}")
    
    # 생성된 파일
    print(f"\nOutput File: {analysis['output_file_path']}")
    
    charts = analysis['json_output']['visualizations']['chart_files']
    print(f"Charts Generated: {len(charts)}")
    for chart_name in list(charts.keys())[:3]:
        print(f"  - {chart_name}")
    
    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_store_analysis())

