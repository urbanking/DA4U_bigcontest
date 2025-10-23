# 신제품 제안 Agent (New Product Agent)

## 개요

StoreAgent 리포트를 기반으로 네이버 데이터랩 키워드 분석과 Gemini 2.5 Flash를 활용하여 신제품 아이디어를 제안하는 AI Agent입니다.

**기술 스택:**
- **LLM**: Gemini 2.5 Flash (OpenAI SDK 사용)
- **크롤링**: Selenium + Chrome WebDriver
- **데이터 소스**: 네이버 데이터랩 쇼핑 인사이트

## 주요 기능

1. **자동 타깃 선정**: 매장 고객 분포와 업종 평균 비교를 통한 성별/연령 타깃 선정
2. **실시간 트렌드 분석**: 네이버 데이터랩 쇼핑 인사이트에서 Top10 키워드 크롤링
5. **AI 기반 제안**: Gemini 2.5 Flash를 활용한 템플릿 제안문 생성 (OpenAI SDK 사용)
6. **데이터 근거 제공**: 선정 룰과 수치를 명확히 제시하는 인사이트 리포트

## 아키텍처

```
NewProductAgent
├── dto/                    # 데이터 전송 객체
│   ├── inputs.py          # StoreAgent 리포트 파싱
│   └── outputs.py         # 최종 응답 조립
├── planner/               # 타깃 선정 로직
│   ├── rules.py          # 업종 화이트리스트 & 카테고리 매핑
│   └── selector.py       # 성별/연령 선택 규칙
├── crawler/               # 데이터 수집
│   └── naver_datalab_client.py  # 네이버 데이터랩 크롤러
├── ideation/              # AI 아이디어 생성
│   ├── prompts.py        # LLM 프롬프트
│   ├── llm_generator.py  # Gemini 2.5 Flash 연동
│   └── reranker.py       # 제안 검증
└── utils/                 # 유틸리티
    └── parsing.py        # 데이터 전처리
```

## 파이프라인

```
StoreAgent 리포트
    ↓
1. 입력 정규화 (DTO)
    ↓
2. 활성화 판정 (업종 화이트리스트)
    ↓
3. 타깃 선정 (성별/연령 + 카테고리)
    │ - 규칙1: 55% 우세
    │ - 규칙2: +5%p 리프트
    │ - 규칙3: 균형형 (전체)
    ↓
4. 네이버 데이터랩 크롤링
    │ - 식품 > 하위 카테고리 (농산물/음료/과자·베이커리)
    │ - Top10 인기 키워드 수집
    ↓
5. LLM 아이디어 생성 (Gemini 2.5 Flash)
    │ - 인사이트: 타깃 선정 근거 (룰 + 수치)
    │ - 제안문: 템플릿 기반 (3~5개)
    ↓
6. 최종 응답 (JSON)
    - insight + proposals
```

## 설치

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

`env` 파일에 Gemini API 키를 추가:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

## 사용 방법

### 1. Python 코드에서 직접 사용

```python
import asyncio
from agents_new.new_product_agent import NewProductAgent

# StoreAgent 리포트 준비
store_report = {
    "report_metadata": {
        "store_code": "TEST001",
        "analysis_date": "2025-10-23 15:30:00"
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
            "남20대이하": 15.0, "남30대": 10.0, ...
            "여20대이하": 20.0, "여30대": 15.0, ...
        }
    }
}

# Agent 실행
async def main():
    agent = NewProductAgent(headless=True)
    result = await agent.run(store_report)
    print(result)

asyncio.run(main())
```

### 2. 테스트 스크립트 실행

```bash
python test_new_product_agent.py
```

## 출력 형식

```json
{
  "store_code": "TEST001",
  "activated": true,
  "audience_filters": {
    "gender": "여성",
    "ages": ["10대", "20대", "30대"],
    "store_age": {
      "10대": 17.5,
      "20대": 17.5,
      "30대": 25.0,
      "40대": 20.0,
      "50대": 15.0,
      "60대 이상": 5.0
    }
  },
  "used_categories": ["농산물", "음료", "과자/베이커리"],
  "keywords_top": [
    {"category": "음료", "rank": 1, "keyword": "피스타치오"},
    {"category": "음료", "rank": 2, "keyword": "딸기라떼"},
    ...
  ],
  "insight": {
    "store_code": "TEST001",
    "gender_summary": "여성이 55.0%로 높습니다",
    "age_summary": "10·20대와 30대 비중이 큽니다",
    "reasoning": {
      "gender_rule": "55% 우세 규칙 적용",
      "age_rule": "최소 칸(≤3)로 누적 ≥50% 규칙",
      "numbers": {
        "store_gender": {"male": 45.0, "female": 55.0},
        "industry_gender": {"male": 40.0, "female": 60.0},
        "store_age": {...},
        "industry_age": {...}
      }
    }
  },
  "proposals": [
    {
      "menu_name": "피스타치오 라떼",
      "category": "음료",
      "target": {"gender": "여성", "ages": ["10대", "20대", "30대"]},
      "evidence": {"category": "음료", "keyword": "피스타치오", "rank": 1},
      "template_ko": "여성과 10대, 20대, 30대의 사람들은 네이버 쇼핑에서 음료 카테고리에서 '피스타치오' 키워드를 많이 찾았습니다(순위 1). 따라서 이를 결합한 '피스타치오 라떼' 메뉴를 개발해보는 것을 추천드립니다."
    },
    ...
  ]
}
```

## 주요 규칙

### 성별 선정 규칙

1. **우세 성별**: 한 성별이 55% 이상 → 해당 성별 선택
2. **리프트 우세**: 업종 대비 +5%p 이상 → 해당 성별 선택
3. **균형형**: 위 조건 미충족 → "전체" 선택

### 연령 선정 규칙

1. 비율 내림차순 + 동률 시 lift 큰 순 정렬
2. 상위에서 누적 50% 달성까지 선택 (최대 3칸)
3. **청년쏠림 보정**: 10대+20대 ≥ 40% → 둘 다 포함
4. **장년쏠림 보정**: 50대+60대 이상 ≥ 40% → 둘 다 포함

### 허용 업종 (화이트리스트)

- 카페, 디저트, 커피전문점, 베이커리
- 떡/한과 제조, 아이스크림/빙수, 차
- 마카롱, 탕후루, 도너츠, 주스
- 테이크아웃커피, 테마카페, 와플/크로플

## 제약사항

- **가격, 원가율, 채널(인스토어/배달/SNS), 조리시간, 레시피 세부 비율/용량 등은 제시하지 않음**
- 템플릿 제안문 형식으로만 제공
- 최종 의사결정은 사용자가 수행

## 문제 해결

### 1. 크롤링 실패

- Chrome 브라우저 버전 확인
- 네트워크 연결 확인
- 헤드리스 모드 비활성화 시도: `NewProductAgent(headless=False)`

### 2. Gemini API 오류

- `env` 파일의 `GEMINI_API_KEY` 확인
- OpenAI SDK가 Gemini endpoint로 연결됨:
  ```
  base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
  ```
- API 키 유효성 확인
- API 키 없을 경우 더미 응답 모드로 자동 전환

### 3. Selenium 오류

```bash
pip install --upgrade selenium webdriver-manager
```

## 향후 개선 사항

- [ ] 캐싱 시스템 (동일 조건 재사용)
- [ ] 타임아웃 제어
- [ ] 다중 LLM 지원 (OpenAI GPT-4 등)
- [ ] 제안 스코어링 및 랭킹 개선
- [ ] 시즌별 키워드 필터링

## 라이선스

본 프로젝트는 DA4U/BigContest AI Agent의 일부입니다.

## 문의

문제 발생 시 이슈를 등록해주세요.
