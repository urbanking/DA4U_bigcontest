# Store Agent Module 사용 가이드

## 📋 개요

`StoreAgentModule`은 BaseAgent 의존성을 제거하고 LangGraph와 완벽하게 호환되도록 리팩토링되었습니다.

## ✨ 주요 변경사항

### 1. **BaseAgent 상속 제거**
- ❌ `from agents.base_agent import BaseAgent, AgentState`
- ✅ 순수한 분석 모듈로 전환
- ✅ LangGraph `TypedDict` State 사용

### 2. **데이터 경로 자동 설정**
- ❌ 하드코딩된 절대 경로
- ✅ 상대 경로로 자동 탐지: `store_agent/store_data/final_merged_data.csv`

### 3. **출력 경로 자동 생성**
- 차트: `store_agent/outputs/charts/`
- 리포트: `store_agent/outputs/reports/`

## 🚀 사용 방법

### 방법 1: LangGraph 노드로 사용 (권장)

```python
from langgraph.graph import StateGraph
from report_builder.store_agent_module import StoreAgentModule, StoreAgentState

# 모듈 초기화
store_agent = StoreAgentModule()

# LangGraph 그래프 구성
workflow = StateGraph(StoreAgentState)

# 노드 함수 정의
async def store_analysis_node(state: StoreAgentState) -> StoreAgentState:
    return await store_agent.execute_analysis_with_self_evaluation(state)

# 노드 추가
workflow.add_node("store_analysis", store_analysis_node)
workflow.set_entry_point("store_analysis")
workflow.set_finish_point("store_analysis")

# 실행
app = workflow.compile()
result = await app.ainvoke({
    "user_query": "000F03E44A 매장 분석해줘",
    "user_id": "user123",
    "session_id": "session456",
    "context": {}
})

# 결과 확인
if result["error"]:
    print(f"에러: {result['error']}")
else:
    analysis = result["store_analysis"]
    print(f"리포트 저장: {analysis['output_file_path']}")
```

### 방법 2: 직접 호출

```python
import asyncio
from report_builder.store_agent_module import StoreAgentModule, StoreAgentState

async def main():
    # 모듈 초기화
    agent = StoreAgentModule()
    
    # State 준비
    state: StoreAgentState = {
        "user_query": "000F03E44A 매장 분석해줘",
        "user_id": "user123",
        "session_id": "session456",
        "context": {},
        "store_analysis": None,
        "error": None
    }
    
    # 분석 실행
    result = await agent.execute_analysis_with_self_evaluation(state)
    
    # 결과 처리
    if result["error"]:
        print(f"❌ 에러: {result['error']}")
    else:
        analysis = result["store_analysis"]
        print(f"✅ 분석 완료!")
        print(f"📊 매장 코드: {analysis['store_code']}")
        print(f"📄 리포트: {analysis['output_file_path']}")
        print(f"⭐ 품질 점수: {analysis['evaluation']['quality_score']:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 방법 3: 커스텀 데이터 경로 지정

```python
from report_builder.store_agent_module import StoreAgentModule

# 커스텀 데이터 경로로 초기화
agent = StoreAgentModule(data_path="/path/to/your/data.csv")

# 나머지는 동일
state = {...}
result = await agent.execute_analysis_with_self_evaluation(state)
```

## 📥 입력 형식

### State 구조

```python
class StoreAgentState(TypedDict):
    user_query: str              # 필수: "000F03E44A 매장 분석해줘"
    user_id: str                 # 필수: 사용자 ID
    session_id: str              # 필수: 세션 ID
    context: Dict[str, Any]      # 선택: 추가 컨텍스트
    store_analysis: Optional[Dict[str, Any]]  # 출력
    error: Optional[str]         # 에러 메시지
```

### 매장 코드 지정 방법

**방법 1**: user_query에 직접 포함
```python
user_query = "000F03E44A 매장 분석해줘"
```

**방법 2**: JSON 파일 경로 지정
```python
context = {"json_file_path": "/path/to/request.json"}
# request.json: {"store_code": "000F03E44A"}
```

**방법 3**: user_query에 JSON 직접 포함
```python
user_query = '{"store_code": "000F03E44A"}'
```

## 📤 출력 형식

```python
{
    "user_query": "...",
    "user_id": "...",
    "session_id": "...",
    "context": {...},
    "store_analysis": {
        "store_code": "000F03E44A",
        "analysis_result": {
            "store_overview": {...},
            "sales_analysis": {...},
            "customer_analysis": {...},
            "commercial_area_analysis": {...},
            "industry_analysis": {...},
            "visualizations": {...},
            "summary": {...}
        },
        "evaluation": {
            "quality_score": 0.85,
            "completeness": 1.0,
            "accuracy": 0.9,
            "relevance": 0.9,
            "actionability": 0.8,
            "feedback": "..."
        },
        "json_output": {...},
        "output_file_path": "c:/ㅈ/DA4U/.../outputs/reports/store_analysis_report_000F03E44A_20251012_143000.json"
    },
    "error": None
}
```

## 📁 생성되는 파일

### 1. JSON 리포트
- 경로: `outputs/reports/store_analysis_report_{store_code}_{timestamp}.json`
- 내용: 전체 분석 결과, 평가, 권고사항

### 2. 시각화 차트 (PNG)
- 경로: `outputs/charts/{store_code}_{chart_name}_{timestamp}.png`
- 차트 종류:
  - `sales_trend`: 매출 추세 (4개 지표)
  - `gender_pie`: 성별 분포
  - `age_pie`: 연령대 분포
  - `detailed_pie`: 세부 고객층 분포
  - `ranking_trend`: 순위 추세
  - `customer_trends`: 고객층별 트렌드 (상위 5개)
  - `new_returning_trends`: 신규/재방문 고객

## ⚠️ 주의사항

1. **데이터 파일 필수**: `store_data/final_merged_data.csv` 파일이 있어야 합니다.
2. **매장 코드 형식**: 10자리 영숫자 (예: `000F03E44A`)
3. **비동기 함수**: `execute_analysis_with_self_evaluation`는 async 함수입니다.
4. **메모리**: 이미지 생성으로 인해 메모리 사용량이 클 수 있습니다.

## 🔧 트러블슈팅

### 에러: "데이터 로드 실패"
```python
# 해결: 데이터 경로 확인 또는 명시적 지정
agent = StoreAgentModule(data_path="./store_data/final_merged_data.csv")
```

### 에러: "매장 코드를 찾을 수 없습니다"
```python
# 해결: 쿼리에 10자리 매장 코드 포함
user_query = "000F03E44A 매장 분석해줘"  # ✅
user_query = "매장 분석해줘"            # ❌
```

### 에러: "매장 코드에 대한 데이터를 찾을 수 없습니다"
```python
# 해결: CSV 파일에 해당 매장 코드가 있는지 확인
import pandas as pd
df = pd.read_csv("store_data/final_merged_data.csv")
print(df['코드'].unique())  # 사용 가능한 매장 코드 목록
```

## 📊 성능 최적화

```python
# 1. 데이터 캐싱: 동일 인스턴스 재사용
agent = StoreAgentModule()

for store_code in ["000F03E44A", "000F03E44B"]:
    state = {
        "user_query": f"{store_code} 매장 분석",
        "user_id": "user123",
        "session_id": f"session_{store_code}",
        "context": {}
    }
    result = await agent.execute_analysis_with_self_evaluation(state)
    # 데이터는 첫 실행 시에만 로드됨
```

## 🎯 다음 단계

이제 다른 LangGraph 노드들과 연결하여 복잡한 워크플로우를 구성할 수 있습니다:

```python
workflow = StateGraph(StoreAgentState)
workflow.add_node("store_analysis", store_analysis_node)
workflow.add_node("commercial_analysis", commercial_analysis_node)
workflow.add_node("marketing_strategy", marketing_strategy_node)

workflow.add_edge("store_analysis", "commercial_analysis")
workflow.add_edge("commercial_analysis", "marketing_strategy")
# ...
```

