# Open SDK - 통합 분석 파이프라인

## 📋 개요

Store Agent, Marketing Agent, Mobility, Panorama, Marketplace 분석을 모두 연결한 완전 자동화 파이프라인입니다.
**Agent 형식이 아닌 일반 Python 함수**로 구현되어 간단하게 실행 가능합니다.

## 🏗️ 구조

```
open_sdk/
├── run_analysis.py      # ⭐ 메인 파이프라인 실행 스크립트
├── output/              # 📁 모든 분석 결과 저장
│   ├── analysis_result_{store_code}_{timestamp}.json
│   └── charts_{store_code}_{timestamp}/
│       ├── 000F03E44A_sales_trend_XXX.png
│       ├── 000F03E44A_gender_pie_XXX.png
│       └── ... (7개 차트)
├── __init__.py
└── README.md
```

## 🚀 실행 방법

### 기본 실행 (기본 매장 코드: 000F03E44A)
```bash
python open_sdk/run_analysis.py
```

### 특정 매장 코드로 실행
```bash
python open_sdk/run_analysis.py 000F03E44A
```

## 📊 전체 분석 흐름

```
상점 코드 입력 (000F03E44A)
    ↓
┌─────────────────────────────────────────┐
│ Step 1: Store Agent 분석 (필수)          │
│ - 매장 개요, 매출, 고객층 분석            │
│ - 7개 차트 자동 생성 (PNG)               │
│ - JSON 리포트 생성                       │
│ - 품질 점수 자가 평가                    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 2: 데이터 형식 변환 (자동)          │
│ - Store 출력 → Marketing 입력 형식       │
│ - market_fit_score 계산                 │
│ - business_churn_risk 계산              │
│ - revisit_rate, cancellation_rate 추출  │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 3: Marketing Agent 분석 (필수)      │
│ - 페르소나 분석 (동적 생성)               │
│ - 위험 코드 감지 (R1~R9)                 │
│ - 맞춤 마케팅 전략 생성                   │
│ - 캠페인 계획 수립                       │
│ - SNS 콘텐츠 생성                        │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 4: Mobility 분석 (필수)            │
│ - 동명 기반 이동 패턴 분석               │
│ - 시각화 차트 생성                       │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 5: Panorama 분석 (필수)            │
│ - 주소 기반 지역 이미지 분석 (Gemini)    │
│ - 상권 분위기, 청결도 등 평가            │
│ - 300m 반경 5개 이미지 분석              │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 6: Marketplace 분석 (필수)         │
│ - 상권분석서비스_결과 JSON 매칭          │
│ - 키워드 기반 스코어링                   │
│ - JSON 데이터 로드                       │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 7: 결과 통합 및 저장                │
│ - open_sdk/output/ 폴더에 저장           │
│ - 모든 분석을 하나의 JSON으로 통합        │
│ - Store 차트 복사                        │
└─────────────────────────────────────────┘
```

## 📤 출력 결과

### 1. 통합 분석 결과 JSON
**위치**: `open_sdk/output/analysis_result_{store_code}_{timestamp}.json`

**구조**:
```json
{
  "metadata": {
    "store_code": "000F03E44A",
    "analysis_timestamp": "20251022_140000",
    "pipeline_version": "1.0"
  },
  
  "store_analysis": {
    "store_overview": {...},
    "sales_analysis": {...},
    "customer_analysis": {...},
    "commercial_area_analysis": {...},
    "industry_analysis": {...},
    "visualizations": {...}
  },
  
  "marketing_strategy": {
    "persona_analysis": {
      "persona_type": "활기찬_역세권_중식당",
      "components": {...},
      "core_insights": {...}
    },
    "risk_analysis": {
      "overall_risk_level": "MEDIUM",
      "detected_risks": [...]
    },
    "marketing_strategies": [...],
    "campaign_plan": {...},
    "social_content": {...}
  },
  
  "mobility_analysis": {...},
  "panorama_analysis": {...},
  "marketplace_analysis": {...}
}
```

### 2. 시각화 차트 (7개)
**위치**: `open_sdk/output/charts_{store_code}_{timestamp}/`

1. `000F03E44A_sales_trend_XXX.png` - 매출 추세 (4개 지표)
2. `000F03E44A_gender_pie_XXX.png` - 성별 분포
3. `000F03E44A_age_pie_XXX.png` - 연령대 분포
4. `000F03E44A_detailed_pie_XXX.png` - 세부 고객층
5. `000F03E44A_ranking_trend_XXX.png` - 순위 변화
6. `000F03E44A_customer_trends_XXX.png` - 고객층별 트렌드
7. `000F03E44A_new_returning_trends_XXX.png` - 신규/재방문 고객

## 🔗 Store Agent ↔ Marketing Agent 자동 연결

### 완벽한 데이터 매칭

| Marketing Agent 요구 | Store Agent 출력 | 자동 변환 |
|---------------------|------------------|-----------|
| `store_name` | `store_overview.name` | ✅ 직접 사용 |
| `industry` | `store_overview.industry` | ✅ 직접 사용 |
| `commercial_zone` | `store_overview.commercial_area` | ✅ 필드명 변경 |
| `is_franchise` | `store_overview.brand` | ✅ `!= "브랜드 없음"` |
| `customer_demographics.gender` | `gender_distribution` | ✅ 비율로 판단 |
| `customer_demographics.age_group` | `age_group_distribution` | ✅ 최댓값 추출 |
| `trends.new_customer` | `new_customers.trend` | ✅ "상승"→"증가" 변환 |
| `trends.revisit` | `returning_customers.trend` | ✅ "상승"→"증가" 변환 |
| `customer_type` | `customer_distribution` | ✅ 최댓값 추출 |
| `metrics.revisit_rate` | `returning_customers.ratio` | ✅ 직접 추출 |
| `metrics.cancellation_rate` | `cancellation_analysis.average_grade` | ✅ 등급→비율 변환 |
| `metrics.market_fit_score` | `rankings` | ✅ 순위로 계산 |
| `metrics.business_churn_risk` | `termination_ratio` | ✅ 가중평균 계산 |

**→ 100% 자동 매칭! 수동 작업 불필요**

## ✨ 주요 기능

### 1. 완전 자동화
- 매장 코드만 입력하면 5차원 분석 자동 실행
- Store → Marketing 데이터 자동 변환
- 모든 결과를 하나의 JSON으로 통합

### 2. Store ↔ Marketing 완벽 연결
- Store Agent 출력을 Marketing Agent 입력으로 완벽 매칭
- `market_fit_score`: 순위 기반 자동 계산
- `business_churn_risk`: 해지율 기반 자동 계산
- `revisit_rate`, `cancellation_rate`: Store 데이터에서 추출

### 3. 통합 저장
- 모든 분석 결과를 `open_sdk/output/` 하나로 통합
- Store 차트 자동 복사
- 타임스탬프 기반 파일명

### 4. 에러 핸들링
- 각 단계별 독립적 에러 처리
- 일부 실패해도 나머지 계속 진행
- 상세한 로그 출력

## 🔧 필수 모듈

### agents_new에서 사용하는 모듈:
- `agents_new/store_agent/report_builder/store_agent_module.py` - Store 분석
- `agents_new/marketing_agent/marketing_agent.py` - Marketing 전략
- `agents_new/visualize_mobility.py` - Mobility 시각화
- `agents_new/panorama_img_anal/analyze_area_by_address.py` - Panorama 분석
- `agents_new/data outputs/상권분석서비스_결과/` - Marketplace JSON

## 📝 예상 출력

```
============================================================
통합 분석 파이프라인 시작
============================================================

[INFO] 상점 코드: 000F03E44A
[INFO] 시작 시간: 2025-10-22 14:00:00

============================================================
[Step 1] Store Agent 분석
============================================================
분석 시작: 000F03E44A
[OK] Store Agent 완료 - 품질: 91.00%
   리포트: .../store_analysis_report_000F03E44A_XXX.json
   차트: 7개 생성

============================================================
[Step 2] 데이터 형식 변환 (Store -> Marketing)
============================================================
[OK] 변환 완료
   매장명: 육육**
   주 고객: 남성 20대 이하
   고객 유형: 유동형
   시장 적합도: 84.0
   폐업 위험도: 13.4

============================================================
[Step 3] Marketing Agent 분석
============================================================
마케팅 전략 생성 중: 000F03E44A
[OK] Marketing Agent 완료
   페르소나: 역세권_청년층_중식당
   마케팅 전략: 3개
   위험 요소: 2개

============================================================
[Step 4] Mobility 분석
============================================================
동명: 성수1가1동
이동 패턴 분석 및 시각화 중...
[OK] Mobility 분석 완료
   차트 생성: 7개

============================================================
[Step 5] Panorama 분석
============================================================
주소: 서울 성동구 왕십리로4가길 9
파노라마 이미지 분석 중... (3-5분 소요)
[OK] Panorama 분석 완료
   지역 유형: 상업지역
   상권 분위기: 8/10
   출력 폴더: C:/img_gpt/output/analysis_XXX

============================================================
[Step 6] Marketplace 분석
============================================================
검색 키워드: ['서울숲', '성수1가1동', '성동구']
총 JSON 파일: 50개
[OK] 매칭된 파일: 서울숲역호선별.json (점수: 12)
   상권명: 서울숲역호선별

============================================================
[Step 7] 결과 저장
============================================================
[OK] 통합 결과 저장: analysis_result_000F03E44A_XXX.json
[OK] 차트 복사: 7개 -> charts_000F03E44A_XXX/

============================================================
분석 파이프라인 완료!
============================================================

[SUMMARY] 결과 요약:
   [OK] Store 분석: 완료
   [OK] Marketing 전략: 완료
   [OK] Mobility: success
   [OK] Panorama: success
   [OK] Marketplace: success

[OUTPUT] 출력 파일: C:\ㅈ\DA4U\bigcontest_ai_agent\open_sdk\output\analysis_result_000F03E44A_XXX.json

[INFO] 완료 시간: 2025-10-22 14:10:00

[SUCCESS] 모든 분석이 성공적으로 완료되었습니다!
```

## 🎯 핵심 특징

### ✅ Store Agent → Marketing Agent 완벽 연결
- **100% 자동 매칭**: Store 출력을 Marketing 입력으로 완벽 변환
- **계산 지표**:
  - `market_fit_score` = (업종순위 × 0.6 + 상권순위 × 0.4)
  - `business_churn_risk` = (상권해지율 × 0.4 + 업종해지율 × 0.6)
  - `revisit_rate` = Store의 재방문고객 비율
  - `cancellation_rate` = Store의 취소등급 → 비율 변환

### ✅ 5차원 통합 분석
1. **Store**: 매장 고객 분석 (7개 차트)
2. **Marketing**: 페르소나 기반 전략 (R1~R9 위험 코드)
3. **Mobility**: 이동 패턴 분석
4. **Panorama**: 지역 이미지 분석 (Gemini AI)
5. **Marketplace**: 상권 분석 (JSON)

### ✅ 완전 자동화
- 매장 코드 하나로 모든 분석 자동 실행
- 결과 자동 저장 (`open_sdk/output/`)
- 차트 자동 복사

## 📂 출력 파일 구조

```
open_sdk/output/
├── analysis_result_000F03E44A_20251022_140000.json  # 통합 결과
└── charts_000F03E44A_20251022_140000/               # Store 차트 복사본
    ├── 000F03E44A_sales_trend_XXX.png
    ├── 000F03E44A_gender_pie_XXX.png
    ├── 000F03E44A_age_pie_XXX.png
    ├── 000F03E44A_detailed_pie_XXX.png
    ├── 000F03E44A_ranking_trend_XXX.png
    ├── 000F03E44A_customer_trends_XXX.png
    └── 000F03E44A_new_returning_trends_XXX.png
```

## 🔍 데이터 변환 상세

### Store Agent → Marketing Agent 매칭표

```python
# 완벽 매칭 (100%)
{
    # 기본 정보
    "store_code": store_overview["code"],
    "store_name": store_overview["name"],
    "address": store_overview["address"],
    "industry": store_overview["industry"],
    "commercial_zone": store_overview["commercial_area"],
    "store_age": store_overview["store_age"],
    "is_franchise": (brand != "브랜드 없음"),
    
    # 고객 정보
    "customer_demographics": {
        "gender": "남성" if male_ratio > 50 else "여성",
        "age_group": max(age_distribution)
    },
    "customer_type": max(customer_distribution),  # 유동형/직장형/거주형
    
    # 트렌드
    "trends": {
        "new_customer": "증가|감소|안정",
        "revisit": "증가|감소|안정"
    },
    
    # 지표
    "metrics": {
        "revisit_rate": returning_customers["ratio"],
        "cancellation_rate": (cancel_grade - 1) * 2 + 1,
        "market_fit_score": industry_rank * 0.6 + commercial_rank * 0.4,
        "business_churn_risk": commercial_term * 0.4 + industry_term * 0.6
    }
}
```

## ⚡ 성능

- **Store 분석**: 약 5-10초
- **Marketing 분석**: 약 5-10초 (Gemini API)
- **Mobility 분석**: 약 3-5초
- **Panorama 분석**: 약 3-5분 (Gemini 이미지 분석)
- **Marketplace 분석**: 즉시 (JSON 로드)

**총 소요 시간**: 약 4-6분

## 🐛 문제 해결

### "매장 코드를 찾을 수 없습니다"
```bash
# CSV에서 사용 가능한 매장 코드 확인
python -c "import pandas as pd; df = pd.read_csv('agents_new/store_agent/store_data/final_merged_data.csv', encoding='utf-8-sig', nrows=10); print(df.iloc[:, 0].unique())"
```

### "Marketing Agent 실패"
- Gemini API 키 확인: `env` 파일에 `GEMINI_API_KEY` 설정
- 네트워크 연결 확인

### "Panorama 분석 오류"
- KAKAO_REST_API_KEY 확인
- 이미지 파일 경로 확인

## 📚 참고

- **Store Agent**: `agents_new/store_agent/`
- **Marketing Agent**: `agents_new/marketing_agent/`
- **데이터 소스**: `agents_new/store_agent/store_data/final_merged_data.csv`
- **Marketplace**: `agents_new/data outputs/상권분석서비스_결과/`

---

**버전**: 1.0  
**마지막 업데이트**: 2025-10-22
