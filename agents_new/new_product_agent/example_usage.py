"""
NewProductAgent 사용 예시 - JSON 캐시 모드

실행 위치: 프로젝트 루트 (bigcontest_ai_agent/)
실행 방법: python agents_new/new_product_agent/example_usage.py
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import asyncio
from agents_new.new_product_agent import NewProductAgent


async def main():
    # 샘플 StoreAgent 리포트
    store_report = {
        "report_metadata": {
            "store_code": "TEST001",
            "analysis_date": "2025-10-26 15:30:00"
        },
        "store_overview": {
            "industry": "카페",
            "commercial_area": "성동구 성수동"
        },
        "customer_analysis": {
            "gender_distribution": {
                "male_ratio": 45.0,
                "female_ratio": 55.0
            },
            "age_group_distribution": {
                "20대 이하": 35.0,
                "30대": 25.0,
                "40대": 20.0,
                "50대": 15.0,
                "60대 이상": 5.0
            }
        },
        "industry_analysis": {
            "average_customer_segments": {
                "남20대이하": 15.0, "남30대": 10.0, "남40대": 8.0, 
                "남50대": 5.0, "남60대이상": 2.0,
                "여20대이하": 20.0, "여30대": 15.0, "여40대": 10.0,
                "여50대": 8.0, "여60대이상": 5.0
            }
        }
    }
    
    print("=" * 60)
    print("NewProductAgent 실행 (JSON 캐시 모드)")
    print("=" * 60)
    
    # Agent 초기화 - use_cache=True가 기본값
    agent = NewProductAgent(
        use_cache=True,  # JSON에서 로드
        save_outputs=False
    )
    
    # 실행
    result = await agent.run(store_report)
    
    # 결과 출력
    print("\n" + "=" * 60)
    print("최종 결과")
    print("=" * 60)
    print(f"매장코드: {result['store_code']}")
    print(f"활성화: {result['activated']}")
    print(f"\n인사이트:")
    print(result.get('insight', {}))
    print(f"\n제안 수: {len(result.get('proposals', []))}")
    
    return result


if __name__ == "__main__":
    asyncio.run(main())

