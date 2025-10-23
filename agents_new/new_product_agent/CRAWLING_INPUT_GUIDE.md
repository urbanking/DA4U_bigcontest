# 네이버 데이터랩 크롤링 입력(Input) 가이드

## 🎯 크롤링 입력 개요

네이버 데이터랩 크롤링은 **StoreAgent 리포트**를 입력으로 받아, 자동으로 타깃 필터를 선정합니다.

---

## 📊 입력 데이터 흐름

```
StoreAgent 리포트 (JSON)
    ↓
[Step 1] DTO 변환 (inputs.py)
    ↓
[Step 2] 업종 확인 (화이트리스트)
    ↓
[Step 3] 타깃 선정 (selector.py)
    ├── 성별 선택 (남성/여성/전체)
    ├── 연령 선택 (10대, 20대, 30대, ...)
    └── 카테고리 선택 (농산물, 음료, 과자/베이커리)
    ↓
[Step 4] 크롤링 실행 ✅
    - 입력: categories, gender, ages
    - 출력: 키워드 리스트
```

---

## 1️⃣ 최상위 입력: StoreAgent 리포트

### 전체 구조
```python
store_report = {
    "report_metadata": {
        "store_code": "TEST001",           # ✅ 매장 코드
        "analysis_date": "2025-10-23"      # ✅ 분석 날짜
    },
    "store_overview": {
        "industry": "카페",                # ✅ 업종 (필수!)
        "commercial_area": "성동구 성수동" # 상권명
    },
    "customer_analysis": {
        "gender_distribution": {           # ✅ 매장 성별 분포
            "male_ratio": 45.0,
            "female_ratio": 55.0
        },
        "age_group_distribution": {        # ✅ 매장 연령 분포
            "20대 이하": 35.0,
            "30대": 25.0,
            "40대": 20.0,
            "50대": 15.0,
            "60대 이상": 5.0
        }
    },
    "industry_analysis": {
        "average_customer_segments": {     # ✅ 업종 평균 분포
            "남20대이하": 15.0,
            "남30대": 10.0,
            "남40대": 8.0,
            "남50대": 5.0,
            "남60대이상": 2.0,
            "여20대이하": 20.0,
            "여30대": 15.0,
            "여40대": 12.0,
            "여50대": 10.0,
            "여60대이상": 3.0
        }
    }
}
```

---

## 2️⃣ 크롤링 직접 입력: 3개 파라미터

### `NaverDatalabClient.fetch_keywords()` 메서드

```python
crawler.fetch_keywords(
    categories=["농산물", "음료", "과자/베이커리"],  # ✅ 1. 카테고리
    gender="여성",                                   # ✅ 2. 성별
    ages=["10대", "20대", "30대"]                    # ✅ 3. 연령
)
```

### 파라미터 상세

#### 1) `categories`: List[str]
- **설명**: 네이버 데이터랩 식품 > 하위 카테고리
- **가능한 값**: `["농산물", "음료", "과자/베이커리"]`
- **선정 방법**: 업종에 따라 자동 매핑
  ```python
  # planner/rules.py - CATEGORY_MAP
  "카페" → ["농산물", "음료", "과자/베이커리"]
  "커피전문점" → ["농산물", "음료"]
  ```

#### 2) `gender`: str
- **설명**: 성별 필터
- **가능한 값**: `"남성"`, `"여성"`, `"전체"`
- **선정 방법**: 매장 성별 분포와 업종 평균 비교
  ```python
  # planner/selector.py - choose_gender()
  # 규칙 1: 한 성별이 55% 이상 → 해당 성별
  # 규칙 2: 업종 대비 +5%p 이상 → 해당 성별
  # 규칙 3: 균형형 → "전체"
  ```

#### 3) `ages`: List[str]
- **설명**: 연령 필터 (최대 3개)
- **가능한 값**: `["10대", "20대", "30대", "40대", "50대", "60대 이상"]`
- **선정 방법**: 누적 50% 달성 + 쏠림 보정
  ```python
  # planner/selector.py - choose_ages()
  # 1) 비율 내림차순으로 누적 50% 달성
  # 2) 청년쏠림: 10대+20대 ≥ 40%면 둘 다 포함
  # 3) 장년쏠림: 50대+60대 ≥ 40%면 둘 다 포함
  ```

---

## 3️⃣ 실제 입력 예시

### 시나리오 1: 여성 중심 카페
```python
# StoreAgent 입력
{
    "store_overview": {"industry": "카페"},
    "customer_analysis": {
        "gender_distribution": {"male_ratio": 30.0, "female_ratio": 70.0},
        "age_group_distribution": {"20대 이하": 40.0, "30대": 30.0, ...}
    }
}

# 자동 선정 결과
categories = ["농산물", "음료", "과자/베이커리"]  # 카페 → 3개 카테고리
gender = "여성"                                  # 70% 우세
ages = ["10대", "20대", "30대"]                  # 누적 50% + 청년쏠림

# 크롤링 실행
keywords = crawler.fetch_keywords(
    categories=["농산물", "음료", "과자/베이커리"],
    gender="여성",
    ages=["10대", "20대", "30대"]
)

# 결과
[
    {"category": "음료", "rank": 1, "keyword": "피스타치오"},
    {"category": "음료", "rank": 2, "keyword": "딸기라떼"},
    {"category": "과자/베이커리", "rank": 1, "keyword": "마들렌"},
    ...
]
```

### 시나리오 2: 남녀 균형 커피전문점
```python
# StoreAgent 입력
{
    "store_overview": {"industry": "커피전문점"},
    "customer_analysis": {
        "gender_distribution": {"male_ratio": 48.0, "female_ratio": 52.0},
        "age_group_distribution": {"30대": 35.0, "40대": 30.0, "50대": 20.0}
    }
}

# 자동 선정 결과
categories = ["농산물", "음료"]      # 커피전문점 → 2개 카테고리
gender = "전체"                      # 균형형 (52% < 55%)
ages = ["30대", "40대"]              # 누적 65%

# 크롤링 실행
keywords = crawler.fetch_keywords(
    categories=["농산물", "음료"],
    gender="전체",
    ages=["30대", "40대"]
)
```

---

## 4️⃣ 입력 검증

### 필수 입력 체크
```python
# new_product_agent.py에서 자동 검증

# 1) 업종 확인
if not should_activate(industry):
    return {"activated": False}  # 화이트리스트에 없으면 중단

# 2) 카테고리 확인
categories = select_categories(industry)
if not categories:
    return {"activated": False}  # 매핑 안되면 중단

# 3) 성별/연령 선정 (항상 성공)
gender = choose_gender(...)  # 최소한 "전체" 반환
ages = choose_ages(...)      # 최소한 1개 연령 반환
```

---

## 5️⃣ 직접 크롤링 (수동 입력)

Agent 없이 직접 크롤링도 가능합니다:

```python
from agents_new.new_product_agent.crawler import NaverDatalabClient

# 직접 파라미터 지정
crawler = NaverDatalabClient(headless=True)

keywords = crawler.fetch_keywords(
    categories=["음료"],           # 원하는 카테고리
    gender="여성",                 # 원하는 성별
    ages=["20대", "30대"]          # 원하는 연령 (최대 3개)
)

print(keywords)
# [{"category": "음료", "rank": 1, "keyword": "..."}, ...]

crawler.close()
```

---

## 6️⃣ 입력 커스터마이징

### 방법 1: StoreAgent 리포트 수정
```python
# 특정 타깃으로 강제 설정
store_report["customer_analysis"]["gender_distribution"] = {
    "male_ratio": 10.0,
    "female_ratio": 90.0  # 여성 90%로 강제
}

agent = NewProductAgent()
result = await agent.run(store_report)
# → gender="여성"으로 크롤링됨
```

### 방법 2: 크롤러 직접 사용
```python
from agents_new.new_product_agent.crawler import NaverDatalabClient

crawler = NaverDatalabClient()
keywords = crawler.fetch_keywords(
    categories=["음료", "과자/베이커리"],  # 커스텀
    gender="남성",                         # 커스텀
    ages=["10대"]                          # 커스텀
)
```

---

## 📋 입력 요약표

| 입력 레벨 | 입력 항목 | 타입 | 예시 | 출처 |
|----------|----------|------|------|------|
| **Level 1** (최상위) | `store_report` | Dict | StoreAgent JSON | StoreAgent |
| **Level 2** (DTO) | `industry` | str | "카페" | store_report |
| | `gender_ratio` | dict | {"male": 45, "female": 55} | store_report |
| | `age_groups` | dict | {"20대 이하": 35, ...} | store_report |
| **Level 3** (크롤링) | `categories` | List[str] | ["농산물", "음료"] | 자동 선정 |
| | `gender` | str | "여성" | 자동 선정 |
| | `ages` | List[str] | ["10대", "20대"] | 자동 선정 |

---

## 💡 핵심 정리

### 자동 모드 (권장)
```python
# StoreAgent 리포트만 있으면 자동으로 처리
agent = NewProductAgent()
result = await agent.run(store_report)  # ✅ 모든 파라미터 자동 선정
```

### 수동 모드 (고급)
```python
# 파라미터 직접 지정
crawler = NaverDatalabClient()
keywords = crawler.fetch_keywords(
    categories=["음료"],
    gender="여성",
    ages=["20대"]
)
```

---

## 🔍 디버깅

실행 로그에서 입력값 확인:
```
[Step 3/6] 타깃 선정 (성별/연령)...
  - 선택된 성별: 여성
    (매장: 남 45.0%, 여 55.0% | 업종평균: 남 40.0%, 여 60.0%)
  - 선택된 연령: 10대, 20대, 30대
  - 선택된 카테고리: 농산물, 음료, 과자/베이커리

[Step 4/6] 네이버 데이터랩 크롤링...
  - 필터: 성별=여성, 연령=['10대', '20대', '30대'], 카테고리=['농산물', '음료', '과자/베이커리']
```

---

## ❓ FAQ

**Q: StoreAgent 리포트 없이 크롤링만 할 수 있나요?**
A: 네, `NaverDatalabClient`를 직접 사용하면 됩니다.

**Q: 카테고리를 커스텀할 수 있나요?**
A: 현재는 업종별 자동 매핑만 지원. 직접 크롤러 사용 시 가능.

**Q: 연령을 4개 이상 선택할 수 있나요?**
A: 네이버 데이터랩 제약으로 최대 3개만 가능합니다.

**Q: 입력 검증은 어디서 하나요?**
A: `new_product_agent.py`의 Step 2~3에서 자동 검증됩니다.

---

이제 입력 구조가 명확해졌나요? 🎯
