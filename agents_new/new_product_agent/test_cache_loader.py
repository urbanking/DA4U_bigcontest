"""캐시 로더 테스트 - 현재 디렉토리에서 실행"""

import sys
from pathlib import Path

# 상위 디렉토리를 모듈 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents_new.new_product_agent.io.keyword_cache_loader import KeywordCacheLoader

print("캐시 로더 생성 중...")
loader = KeywordCacheLoader()

# 테스트 케이스
test_cases = [
    {"gender": "남성", "ages": ["10대"], "categories": ["농산물", "음료", "과자/베이커리"]},
    {"gender": "여성", "ages": ["20대"], "categories": ["농산물", "음료"]},
]

print("=" * 60)
print("캐시 로더 테스트")
print("=" * 60)

for i, test_case in enumerate(test_cases, 1):
    print(f"\n[테스트 {i}]")
    print(f"  성별: {test_case['gender']}")
    print(f"  연령: {test_case['ages']}")
    print(f"  카테고리: {test_case['categories']}")
    
    keywords = loader.get_keywords(
        gender=test_case['gender'],
        ages=test_case['ages'],
        categories=test_case['categories']
    )
    
    print(f"  결과: {len(keywords)}개 키워드")
    if keywords:
        print(f"  상위 3개:")
        for kw in keywords[:3]:
            print(f"    {kw}")
    print()

print("=" * 60)
print("테스트 완료!")
