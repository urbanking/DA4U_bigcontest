"""
Store Agent Module 테스트 스크립트
"""

import asyncio
import logging
from store_agent_module import StoreAgentModule, StoreAgentState

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_store_analysis():
    """매장 분석 테스트"""
    print("=" * 60)
    print("Store Agent Module 테스트")
    print("=" * 60)
    
    # 1. 모듈 초기화
    print("\n[1] 모듈 초기화 중...")
    agent = StoreAgentModule()
    print(f"✅ 초기화 완료 - 데이터 경로: {agent.data_path}")
    
    # 2. State 준비 (매장 코드를 실제 데이터에 있는 코드로 변경하세요)
    print("\n[2] 분석 State 준비 중...")
    state: StoreAgentState = {
        "user_query": "000F03E44A 매장 분석해줘",  # 실제 매장 코드로 변경
        "user_id": "test_user",
        "session_id": "test_session_001",
        "context": {},
        "store_analysis": None,
        "error": None
    }
    print("✅ State 준비 완료")
    
    # 3. 분석 실행
    print("\n[3] 매장 분석 실행 중...")
    print("-" * 60)
    result = await agent.execute_analysis_with_self_evaluation(state)
    print("-" * 60)
    
    # 4. 결과 확인
    print("\n[4] 결과 확인")
    if result["error"]:
        print(f"❌ 에러 발생: {result['error']}")
        print("\n💡 해결 방법:")
        print("  1. CSV 파일에서 사용 가능한 매장 코드 확인:")
        print("     import pandas as pd")
        print("     df = pd.read_csv('store_data/final_merged_data.csv')")
        print("     print(df['코드'].unique())")
        print("  2. user_query의 매장 코드를 실제 코드로 변경")
        return
    
    print("✅ 분석 완료!")
    print()
    
    # 분석 결과 출력
    analysis = result["store_analysis"]
    
    print("📊 분석 요약")
    print("-" * 60)
    print(f"  매장 코드: {analysis['store_code']}")
    print(f"  품질 점수: {analysis['evaluation']['quality_score']:.2%}")
    print(f"  완성도: {analysis['evaluation']['completeness']:.2%}")
    print(f"  정확성: {analysis['evaluation']['accuracy']:.2%}")
    print(f"  관련성: {analysis['evaluation']['relevance']:.2%}")
    print(f"  실행가능성: {analysis['evaluation']['actionability']:.2%}")
    print()
    
    # 매장 개요
    overview = analysis['analysis_result']['store_overview']
    print("🏪 매장 개요")
    print("-" * 60)
    print(f"  가맹점명: {overview['name']}")
    print(f"  주소: {overview['address']}")
    print(f"  업종: {overview['industry']}")
    print(f"  브랜드: {overview['brand']}")
    print(f"  상권: {overview['commercial_area']}")
    print(f"  매장 연령: {overview['store_age']}")
    print(f"  운영 개월수: {overview['operating_months']:.1f}개월")
    print()
    
    # 핵심 인사이트
    summary = analysis['analysis_result']['summary']
    print("💡 핵심 인사이트")
    print("-" * 60)
    for idx, insight in enumerate(summary['key_insights'], 1):
        print(f"  {idx}. {insight}")
    print()
    
    # 주요 문제점
    if summary['main_problems']:
        print("⚠️  주요 문제점")
        print("-" * 60)
        for idx, problem in enumerate(summary['main_problems'], 1):
            print(f"  {idx}. {problem}")
        print()
    
    # 권고사항
    recommendations = summary['recommendations']
    if recommendations:
        print("📋 권고사항 (상위 3개)")
        print("-" * 60)
        for idx, rec in enumerate(recommendations[:3], 1):
            print(f"\n  {idx}. [{rec['category']}] {rec['action']}")
            print(f"     우선순위: {rec['priority']}")
            print(f"     대상: {rec['target']}")
            if 'specific_actions' in rec:
                print(f"     세부 실행사항:")
                for action in rec['specific_actions'][:3]:
                    print(f"       - {action}")
        print()
    
    # 생성된 파일
    print("📁 생성된 파일")
    print("-" * 60)
    print(f"  리포트: {analysis['output_file_path']}")
    
    charts = analysis['json_output']['visualizations']['chart_files']
    print(f"  차트 ({len(charts)}개):")
    for chart_name, chart_path in list(charts.items())[:3]:
        print(f"    - {chart_name}: {chart_path}")
    if len(charts) > 3:
        print(f"    ... 외 {len(charts) - 3}개")
    print()
    
    print("=" * 60)
    print("테스트 완료! 🎉")
    print("=" * 60)

async def test_multiple_stores():
    """여러 매장 분석 테스트 (데이터 캐싱 확인)"""
    print("\n\n")
    print("=" * 60)
    print("다중 매장 분석 테스트 (데이터 캐싱)")
    print("=" * 60)
    
    agent = StoreAgentModule()
    
    # 여러 매장 코드 (실제 코드로 변경)
    store_codes = ["000F03E44A", "000F03E44B", "000F03E44C"]
    
    for idx, store_code in enumerate(store_codes, 1):
        print(f"\n[{idx}/{len(store_codes)}] {store_code} 분석 중...")
        
        state: StoreAgentState = {
            "user_query": f"{store_code} 매장 분석",
            "user_id": "test_user",
            "session_id": f"test_session_{idx:03d}",
            "context": {},
            "store_analysis": None,
            "error": None
        }
        
        result = await agent.execute_analysis_with_self_evaluation(state)
        
        if result["error"]:
            print(f"  ❌ 에러: {result['error']}")
        else:
            analysis = result["store_analysis"]
            quality = analysis['evaluation']['quality_score']
            print(f"  ✅ 완료 - 품질: {quality:.2%}")
    
    print("\n" + "=" * 60)
    print("다중 분석 완료!")
    print("=" * 60)

if __name__ == "__main__":
    # 단일 매장 테스트
    asyncio.run(test_store_analysis())
    
    # 다중 매장 테스트 (주석 해제하여 실행)
    # asyncio.run(test_multiple_stores())

