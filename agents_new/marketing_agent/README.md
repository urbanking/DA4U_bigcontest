# 마케팅 에이전트 (Marketing Agent)

## 📋 개요

마케팅 에이전트는 매장 데이터를 분석하여 맞춤형 마케팅 전략을 생성하는 AI 에이전트입니다. 동적 페르소나 생성, 위험 분석, 핵심 인사이트 제공, SNS 콘텐츠 생성 등의 기능을 제공합니다.

## 🏗️ 구조

```
marketing_agent/
├── __init__.py
├── marketing_agent.py          # 메인 에이전트 클래스
├── persona_engine.py           # 페르소나 분석 엔진
├── dynamic_persona_generator.py # 동적 페르소나 생성기
├── risk_analyzer.py            # 위험 분석기
├── strategy_generator.py       # 전략 생성기
├── openai_agent_wrapper.py    # OpenAI Agents SDK 래퍼
└── README.md                   # 이 파일
```

## 🚀 핵심 기능

### 1. 동적 페르소나 생성
- 미리 정의된 템플릿 대신 AI가 매장 특성을 분석하여 고유한 페르소나 생성
- 매장 데이터, 상권 정보, 고객 특성을 종합 분석

### 2. 핵심 인사이트 제공
- **페르소나 테이블**: 매장의 핵심 특성을 구조화된 테이블로 제공
- **위험 진단 테이블**: 감지된 위험 요소들을 분석하여 대응 방안 제시

### 3. SNS 마케팅 콘텐츠 생성
- Instagram 포스트 (피드, 스토리, 릴스)
- Facebook 포스트
- 프로모션 문구 (배너, 팝업, SMS, 이메일)

### 4. 맞춤형 마케팅 전략
- 페르소나 기반 전략 생성
- 위험 요소 고려한 대응 전략
- 실행 가능한 구체적 전술 제시

## 🚀 빠른 시작 (독립 실행)

다른 팀원이 `marketing_agent` 폴더만으로도 실행할 수 있도록 독립 실행 스크립트를 제공합니다.

### 1. 독립 실행 방법
```bash
# marketing_agent 폴더에서 실행
python run_marketing_agent.py
```

이 스크립트는 샘플 데이터로 마케팅 분석을 실행하고 결과를 JSON 파일로 저장합니다.

### 2. 외부 데이터로 실행
```python
from marketing_agent import MarketingAgent

# 매장 데이터와 진단 데이터 준비
store_report = {
    "store_code": "YOUR_STORE_CODE",
    "industry": "한식",
    "metrics": {
        "revisit_rate": 65.5,
        "delivery_ratio": 30.0,
        "new_customer_trend": 5.2,
        "cancellation_rate": 8.3
    }
}

diagnostic = {
    "diagnostic_results": {
        "sales_slump_days": 3,
        "short_term_sales_drop": 5.2
    }
}

# 마케팅 에이전트 실행
agent = MarketingAgent(store_code="YOUR_STORE_CODE")
result = await agent.run_marketing(store_report, diagnostic)
```

## 📦 의존성

### 필수 패키지
```bash
pip install openai
pip install python-dotenv
pip install pandas
pip install streamlit
```

### 환경 변수
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

## 🔧 사용 방법

### 1. 기본 사용법

```python
import asyncio
from marketing_agent import MarketingAgent

async def main():
    # 마케팅 에이전트 생성
    agent = MarketingAgent("STORE001")
    
    # 매장 데이터 준비
    store_report = {
        "store_code": "STORE001",
        "address": "서울특별시 강남구 테헤란로 123",
        "industry": "외식업",
        "store_name": "테스트 매장"
    }
    
    # 진단 데이터 준비
    diagnostic = {
        "overall_risk_level": "LOW",
        "detected_risks": [],
        "analysis_summary": "기본 분석"
    }
    
    # 마케팅 분석 실행
    result = await agent.run_marketing(store_report, diagnostic)
    
    # 결과 확인
    print(f"페르소나 유형: {result['persona_analysis']['persona_type']}")
    print(f"마케팅 전략 수: {len(result['marketing_strategies'])}")
    print(f"SNS 포스트 수: {len(result['social_content']['instagram_posts'])}")

# 실행
asyncio.run(main())
```

### 2. 결과 구조

```python
{
    "store_code": "STORE001",
    "analysis_timestamp": "2025-10-22T10:55:44.242082",
    "persona_analysis": {
        "persona_type": "강남_동네_미식_생활자",
        "persona_description": "매장 설명...",
        "core_insights": {
            "persona": {
                "summary": "페르소나 요약",
                "table_data": {
                    "업종": "외식업",
                    "상권": "주거형",
                    "프랜차이즈 여부": "N",
                    # ... 더 많은 필드
                }
            },
            "risk_diagnosis": {
                "summary": "위험 진단 요약",
                "table_data": [...],
                "overall_risk_level": "LOW"
            }
        }
    },
    "marketing_strategies": [
        {
            "strategy_id": "strategy_1",
            "name": "전략명",
            "description": "전략 설명",
            "channel": "온라인",
            "tactics": ["전술1", "전술2"],
            "expected_impact": "높음",
            "implementation_time": "1주",
            "budget_estimate": "100만원",
            "success_metrics": ["방문객 증가", "매출 증대"],
            "priority": "높음"
        }
    ],
    "social_content": {
        "instagram_posts": [
            {
                "title": "포스트 제목",
                "content": "포스트 내용 #해시태그",
                "hashtags": ["#해시태그1", "#해시태그2"],
                "post_type": "feed"
            }
        ],
        "facebook_posts": [...],
        "promotion_texts": [...]
    }
}
```

## 🔗 다른 시스템과의 연동

### 1. 백엔드 서비스 연동

```python
# backend/services/marketing_service.py
from agents_new.marketing_agent.marketing_agent import MarketingAgent

async def generate_marketing_analysis_with_agent(
    store_code: str,
    store_report: Dict[str, Any],
    diagnostic: Dict[str, Any],
    query: Optional[str] = None
) -> Dict[str, Any]:
    marketing_agent = MarketingAgent(store_code)
    result = await marketing_agent.run_marketing(store_report, diagnostic)
    return {
        "status": "success",
        "marketing_analysis": result
    }
```

### 2. 프론트엔드 연동

```python
# frontend/components/marketing_strategy.py
def render_marketing_analysis(analysis: Dict[str, Any]):
    marketing_data = analysis.get("marketing_analysis", {})
    
    # 핵심 인사이트 렌더링
    if "persona_analysis" in marketing_data:
        render_persona_analysis(marketing_data["persona_analysis"])
    
    # SNS 콘텐츠 렌더링
    if "social_content" in marketing_data:
        render_social_content(marketing_data["social_content"])
```

## ⚙️ 설정 및 커스터마이징

### 1. 페르소나 템플릿 수정
`persona_engine.py`의 `_load_persona_templates()` 메서드에서 템플릿을 수정할 수 있습니다.

### 2. 위험 코드 추가
`risk_analyzer.py`의 `RISK_DEFINITIONS`에서 새로운 위험 코드를 정의할 수 있습니다.

### 3. SNS 콘텐츠 형식 변경
`marketing_agent.py`의 `_generate_social_content()` 메서드에서 프롬프트를 수정할 수 있습니다.

## 🐛 문제 해결

### 1. API 키 오류
```
ValueError: GEMINI_API_KEY not found
```
→ `env` 파일에 올바른 API 키가 설정되어 있는지 확인

### 2. JSON 파싱 오류
```
JSON 파싱 오류: Expecting ',' delimiter
```
→ LLM 응답이 완전하지 않을 수 있음. 재시도하거나 기본값 사용

### 3. 메모리 부족
→ 대용량 데이터 처리 시 배치 처리 고려

## 📊 성능 최적화

### 1. 캐싱 활용
- 동일한 매장에 대한 반복 분석 시 캐시된 결과 사용
- `DynamicPersonaGenerator`에 내장된 캐싱 메커니즘 활용

### 2. 비동기 처리
- 모든 LLM 호출은 비동기로 처리되어 성능 최적화
- `asyncio`를 사용한 동시 처리

### 3. 오류 처리
- API 할당량 초과 시 기본값 반환
- 네트워크 오류 시 재시도 메커니즘

## 🔄 업데이트 이력

- **v1.0.0**: 기본 마케팅 에이전트 구현
- **v1.1.0**: 동적 페르소나 생성 추가
- **v1.2.0**: 핵심 인사이트 테이블 추가
- **v1.3.0**: SNS 콘텐츠 생성 추가
- **v1.4.0**: 오류 처리 및 기본값 반환 개선

## 📞 지원

문제가 발생하거나 기능 추가가 필요한 경우, 마케팅 에이전트 개발팀에 문의하세요.

---

**주의사항**: 이 에이전트는 Gemini API를 사용하므로 API 할당량을 고려하여 사용하세요. 무료 티어의 경우 일일 250회 요청 제한이 있습니다.
