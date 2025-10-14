"""
빠른 테스트 스크립트
"""

import asyncio
import logging
import sys
from pathlib import Path

# 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from report_builder.store_agent_module import StoreAgentModule, StoreAgentState

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    print("=" * 60)
    print("Store Agent Module 테스트")
    print("=" * 60)
    
    try:
        # 1. 모듈 초기화
        print("\n[1] 모듈 초기화 중...")
        agent = StoreAgentModule()
        print(f"✅ 초기화 완료 - 데이터 경로: {agent.data_path}")
        
        # 2. State 준비
        print("\n[2] 분석 State 준비 중...")
        state: StoreAgentState = {
            "user_query": "000F03E44A 매장 분석해줘",
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
        
        # 생성된 파일
        print("📁 생성된 파일")
        print("-" * 60)
        print(f"  리포트: {analysis['output_file_path']}")
        
        charts = analysis['json_output']['visualizations']['chart_files']
        print(f"  차트 ({len(charts)}개):")
        for chart_name, chart_path in list(charts.items())[:3]:
            if chart_path:
                print(f"    - {chart_name}: 생성 완료")
        if len(charts) > 3:
            print(f"    ... 외 {len(charts) - 3}개")
        print()
        
        print("=" * 60)
        print("테스트 완료! 🎉")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

