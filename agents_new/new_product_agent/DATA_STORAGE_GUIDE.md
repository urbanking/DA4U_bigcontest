# 신제품 제안 Agent - 데이터 저장 및 사용 가이드

## 📊 데이터 흐름 개요

```
StoreAgent 리포트
    ↓
NewProductAgent 실행
    ↓
네이버 데이터랩 크롤링 → [메모리] → LLM 생성
    ↓                        ↓
    ↓                    [선택: 파일 저장]
    ↓                        ↓
최종 결과 (JSON)     크롤링 결과 (JSON)
```

---

## 🔄 사용 방식

### 1️⃣ 기본: 메모리만 사용 (파일 저장 안함)

```python
import asyncio
from agents_new.new_product_agent import NewProductAgent

async def main():
    # 파일 저장 안함 (기본값)
    agent = NewProductAgent(headless=True)
    
    result = await agent.run(store_report)
    
    # 크롤링 결과는 result에 포함됨
    keywords = result['keywords_top']
    # [{"category": "음료", "rank": 1, "keyword": "피스타치오"}, ...]
    
    # LLM 제안도 포함됨
    proposals = result['proposals']
    # [{"menu_name": "피스타치오 라떼", ...}, ...]

asyncio.run(main())
```

**장점:**
- ✅ 빠름 (디스크 I/O 없음)
- ✅ 간단함
- ✅ 임시 분석에 적합

**단점:**
- ❌ 재사용 불가 (매번 크롤링 필요)
- ❌ 결과 추적 어려움

---

### 2️⃣ 파일로 저장 (권장)

```python
import asyncio
from agents_new.new_product_agent import NewProductAgent

async def main():
    # 파일 저장 활성화 (기본 위치: open_sdk/output)
    agent = NewProductAgent(
        headless=True,
        save_outputs=True  # ✅ 파일 저장
    )
    
    result = await agent.run(store_report)
    
    # 자동으로 파일 생성:
    # open_sdk/output/naver_datalab_{timestamp}/
    #   ├── {store_code}_keywords.json
    #   └── {store_code}_new_product_result.json

asyncio.run(main())
```

**저장되는 파일:**

#### 폴더 구조
```
open_sdk/output/
├── analysis_{store_code}_{timestamp}/    # 기존: 매장 분석
├── marketplace_{timestamp}/              # 기존: 상권 분석
├── mobility_{timestamp}/                 # 기존: 이동 분석
└── naver_datalab_{timestamp}/            # ✅ NEW: 신제품 제안
    ├── {store_code}_keywords.json
    └── {store_code}_new_product_result.json
```

#### 1) 크롤링 결과 (`{store_code}_keywords.json`)
```json
{
  "store_code": "TEST001",
  "crawled_at": "2025-10-23T15:30:45.123456",
  "metadata": {
    "industry": "카페",
    "commercial_area": "성동구 성수동",
    "target_gender": "여성",
    "target_ages": ["10대", "20대", "30대"],
    "categories": ["농산물", "음료", "과자/베이커리"]
  },
  "keywords": [
    {"category": "음료", "rank": 1, "keyword": "피스타치오"},
    {"category": "음료", "rank": 2, "keyword": "딸기라떼"},
    ...
  ],
  "total_count": 30
}
```

#### 2) 최종 결과 (`{store_code}_new_product_result.json`)
```json
{
  "store_code": "TEST001",
  "activated": true,
  "audience_filters": {...},
  "used_categories": ["농산물", "음료", "과자/베이커리"],
  "keywords_top": [...],
  "insight": {...},
  "proposals": [...]
}
```

**장점:**
- ✅ 재사용 가능 (크롤링 결과 캐싱)
- ✅ 추적 가능 (언제, 어떤 키워드가 수집되었는지)
- ✅ 분석 가능 (시간별 트렌드 변화)
- ✅ 디버깅 용이

---

### 3️⃣ 저장된 크롤링 결과 재사용

```python
from agents_new.new_product_agent.io import CrawlerOutputManager

# 1) 최신 크롤링 결과 로드
manager = CrawlerOutputManager()
data = manager.get_latest_keywords("TEST001")

if data:
    print(f"매장: {data['store_code']}")
    print(f"크롤링 시각: {data['crawled_at']}")
    print(f"키워드: {data['keywords']}")

# 2) 특정 파일 로드
specific_data = manager.load_keywords(
    "agents_new/data outputs/naver_datalab/TEST001_keywords_20251023_153045.json"
)

# 3) 크롤링 없이 LLM만 재실행 가능 (향후 기능)
```

---

## 📁 저장 위치

```
bigcontest_ai_agent/
└── open_sdk/
    └── output/
        ├── analysis_{store_code}_{timestamp}/         # 매장 분석 결과
        ├── marketplace_{timestamp}/                   # 상권 분석 결과
        ├── mobility_{timestamp}/                      # 이동 분석 결과
        └── naver_datalab_{timestamp}/                 # ✅ 신제품 제안 (NEW!)
            ├── {store_code}_keywords.json             # 크롤링 키워드
            └── {store_code}_new_product_result.json   # 최종 결과
```

**통합 출력 폴더 사용의 장점:**
- ✅ 모든 분석 결과가 한 곳에 모임
- ✅ 타임스탬프별 세션 관리 용이
- ✅ 기존 분석 결과와 함께 관리 가능

---

## 🎯 실전 사용 시나리오

### 시나리오 1: 일회성 분석
```python
# 메모리만 사용 (빠름)
agent = NewProductAgent(headless=True, save_outputs=False)
result = await agent.run(store_report)
```

### 시나리오 2: 정기 분석 (일별/주별)
```python
# 파일 저장 (추적 가능)
agent = NewProductAgent(headless=True, save_outputs=True)
results = []
for store_code in store_codes:
    result = await agent.run(get_store_report(store_code))
    results.append(result)

# 나중에 저장된 결과 비교 분석
```

### 시나리오 3: 크롤링 캐시 활용
```python
manager = CrawlerOutputManager()

# 오늘 이미 크롤링했는지 확인
latest = manager.get_latest_keywords("TEST001")
if latest and is_today(latest['crawled_at']):
    # 저장된 키워드 재사용
    keywords = latest['keywords']
else:
    # 새로 크롤링
    agent = NewProductAgent(save_outputs=True)
    result = await agent.run(store_report)
```

---

## 🚀 빠른 시작

### 방법 1: 메모리만 사용
```bash
python test_new_product_agent.py
```

### 방법 2: 파일 저장 포함
```bash
python examples_new_product_agent.py
# 실행 후 선택: 2 (파일로 저장)
```

### 방법 3: 저장된 데이터 확인
```bash
python examples_new_product_agent.py
# 실행 후 선택: 3 (저장된 결과 로드)
```

---

## 💡 팁

### 1. 크롤링 결과 재사용으로 속도 향상
- 동일 매장/날짜는 한 번만 크롤링
- 저장된 키워드로 여러 번 LLM 실험 가능

### 2. 시간별 트렌드 분석
```python
# 같은 매장의 과거 크롤링 결과 비교
files = sorted(output_dir.glob("TEST001_keywords_*.json"))
for f in files:
    data = manager.load_keywords(str(f))
    print(f"{data['crawled_at']}: {data['keywords'][0]['keyword']}")
```

### 3. 배치 처리 시 파일 저장 필수
```python
# 100개 매장 처리 시 - 중간에 오류나도 재시작 가능
agent = NewProductAgent(save_outputs=True)
for store in stores:
    try:
        await agent.run(store_report)
    except Exception as e:
        print(f"실패: {store['code']}")
        continue
```

---

## 📊 저장 파일 활용 예시

### Python으로 분석
```python
import json
from pathlib import Path

# 모든 크롤링 결과 읽기
output_dir = Path("agents_new/data outputs/naver_datalab")
all_keywords = []

for file in output_dir.glob("*_keywords_*.json"):
    with open(file) as f:
        data = json.load(f)
        all_keywords.extend(data['keywords'])

# 가장 많이 등장한 키워드 TOP 10
from collections import Counter
top_keywords = Counter(k['keyword'] for k in all_keywords).most_common(10)
print(top_keywords)
```

### Pandas로 분석
```python
import pandas as pd

# 크롤링 결과를 DataFrame으로
df = pd.DataFrame(all_keywords)
print(df.groupby('keyword').size().sort_values(ascending=False).head(10))
```

---

## ⚠️ 주의사항

1. **저장 공간 관리**
   - 매장×날짜별로 파일 생성됨
   - 주기적으로 오래된 파일 정리 권장

2. **크롤링 속도**
   - 파일 저장 여부와 무관하게 크롤링 시간 동일
   - 저장은 크롤링 후 수행되므로 속도 영향 미미

3. **재사용 시 주의**
   - 트렌드는 시시각각 변하므로 너무 오래된 데이터 재사용 지양
   - 일반적으로 당일 데이터만 재사용 권장

---

## 📞 문의

파일 저장/로드 관련 문제가 있으면 이슈를 등록해주세요!
