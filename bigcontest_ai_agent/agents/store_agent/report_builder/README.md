# Store Agent Module

매장 분석 전문 에이전트 모듈 - LangGraph 완벽 호환 ✨

## 🎯 개요

`StoreAgentModule`은 개별 매장에 대한 종합적인 분석을 수행하고, 실행 가능한 권고사항을 제공하는 모듈입니다. LangGraph 프레임워크와 완벽하게 호환되도록 설계되었습니다.

## ✨ 주요 기능

### 📊 분석 기능
- **점포 개요**: 매장 기본 정보, 운영 기간, 업종, 상권 정보
- **매출 분석**: 매출금액, 매출건수, 고객수, 객단가 트렌드
- **고객층 분석**: 성별/연령대 분포, 신규/재방문 고객 비율
- **상권 분석**: 동일 상권 내 경쟁 환경, 상권 건강도
- **업종 분석**: 동일 업종 내 경쟁력, 업종 트렌드
- **자가 평가**: 분석 품질, 완성도, 정확성, 실행가능성

### 📈 시각화
- 매출 트렌드 차트 (추세선 포함)
- 성별/연령대 분포 파이차트
- 순위 변화 그래프
- 고객층별 시계열 트렌드
- 신규/재방문 고객 트렌드

### 💡 권고사항 생성
- 마케팅 전략 (타겟 고객층 기반)
- 운영 개선 (취소율, 배달 서비스)
- 경쟁력 강화 (순위 개선)
- 상권/업종 대응 전략

## 🚀 빠른 시작

### 설치

```bash
# 필요한 패키지 설치
pip install pandas numpy matplotlib seaborn langgraph
```

### 기본 사용법

```python
import asyncio
from report_builder.store_agent_module import StoreAgentModule, StoreAgentState

async def main():
    # 1. 모듈 초기화
    agent = StoreAgentModule()
    
    # 2. State 준비
    state: StoreAgentState = {
        "user_query": "000F03E44A 매장 분석해줘",
        "user_id": "user123",
        "session_id": "session456",
        "context": {},
        "store_analysis": None,
        "error": None
    }
    
    # 3. 분석 실행
    result = await agent.execute_analysis_with_self_evaluation(state)
    
    # 4. 결과 확인
    if result["error"]:
        print(f"에러: {result['error']}")
    else:
        analysis = result["store_analysis"]
        print(f"리포트: {analysis['output_file_path']}")

asyncio.run(main())
```

### LangGraph 통합

```python
from langgraph.graph import StateGraph
from report_builder.store_agent_module import StoreAgentModule, StoreAgentState

# 노드 함수
store_agent = StoreAgentModule()

async def store_analysis_node(state: StoreAgentState) -> StoreAgentState:
    return await store_agent.execute_analysis_with_self_evaluation(state)

# 그래프 구성
workflow = StateGraph(StoreAgentState)
workflow.add_node("store_analysis", store_analysis_node)
workflow.set_entry_point("store_analysis")
workflow.set_finish_point("store_analysis")

app = workflow.compile()
result = await app.ainvoke(state)
```

## 📖 문서

- **[USAGE_EXAMPLE.md](./USAGE_EXAMPLE.md)**: 상세한 사용 가이드 및 예제
- **[CHANGELOG.md](./CHANGELOG.md)**: 변경 이력 및 마이그레이션 가이드
- **[test_store_agent.py](./test_store_agent.py)**: 실행 가능한 테스트 스크립트

## 🧪 테스트

```bash
# 테스트 실행
cd report_builder
python test_store_agent.py
```

## 📁 프로젝트 구조

```
store_agent/
├── report_builder/
│   ├── store_agent_module.py     # 메인 모듈
│   ├── test_store_agent.py       # 테스트 스크립트
│   ├── USAGE_EXAMPLE.md          # 사용 가이드
│   ├── CHANGELOG.md              # 변경 이력
│   └── README.md                 # 이 파일
├── store_data/
│   └── final_merged_data.csv     # 분석 데이터
└── outputs/
    ├── charts/                   # 생성된 차트
    └── reports/                  # 생성된 리포트
```

## 📥 입력

### StoreAgentState
```python
{
    "user_query": str,              # "000F03E44A 매장 분석"
    "user_id": str,                 # 사용자 ID
    "session_id": str,              # 세션 ID
    "context": Dict[str, Any],      # 추가 컨텍스트
    "store_analysis": None,         # 출력 (초기값 None)
    "error": None                   # 에러 (초기값 None)
}
```

### 매장 코드 지정
- user_query에 포함: `"000F03E44A 매장 분석"`
- JSON 파일: `context = {"json_file_path": "path/to/file.json"}`
- JSON 문자열: `user_query = '{"store_code": "000F03E44A"}'`

## 📤 출력

### StoreAgentState (업데이트됨)
```python
{
    "user_query": "...",
    "user_id": "...",
    "session_id": "...",
    "context": {...},
    "store_analysis": {
        "store_code": "000F03E44A",
        "analysis_result": {...},
        "evaluation": {...},
        "json_output": {...},
        "output_file_path": "path/to/report.json"
    },
    "error": None
}
```

### 생성 파일
- **JSON 리포트**: `outputs/reports/store_analysis_report_{code}_{timestamp}.json`
- **시각화 차트**: `outputs/charts/{code}_{chart_name}_{timestamp}.png`

## 🎨 생성되는 차트

1. `sales_trend`: 매출 추세 (매출금액, 매출건수, 고객수, 객단가)
2. `gender_pie`: 성별 분포
3. `age_pie`: 연령대 분포
4. `detailed_pie`: 세부 고객층 분포
5. `ranking_trend`: 순위 변화
6. `customer_trends`: 고객층별 트렌드 (상위 5개)
7. `new_returning_trends`: 신규/재방문 고객

## ⚡ 성능 최적화

- **데이터 캐싱**: 동일 인스턴스 재사용 시 데이터 재로딩 방지
- **비동기 처리**: async/await 패턴 사용
- **메모리 효율**: 불필요한 의존성 제거

## ⚠️ 주의사항

1. **데이터 파일**: `store_data/final_merged_data.csv` 필수
2. **매장 코드**: 10자리 영숫자 형식 (예: `000F03E44A`)
3. **비동기 함수**: `async`/`await` 사용 필수
4. **메모리**: 이미지 생성으로 인한 메모리 사용

## 🔧 설정

### 커스텀 데이터 경로
```python
agent = StoreAgentModule(data_path="/custom/path/to/data.csv")
```

### 출력 디렉토리
기본 경로: `store_agent/outputs/`
- 차트: `outputs/charts/`
- 리포트: `outputs/reports/`

## 🐛 트러블슈팅

### "데이터 로드 실패"
```python
# 해결: 경로 확인 또는 명시적 지정
agent = StoreAgentModule(data_path="./store_data/final_merged_data.csv")
```

### "매장 코드를 찾을 수 없습니다"
```python
# 해결: 10자리 매장 코드 포함
user_query = "000F03E44A 매장 분석해줘"  # ✅
```

### "매장 데이터를 찾을 수 없습니다"
```python
# 해결: CSV 파일의 매장 코드 확인
import pandas as pd
df = pd.read_csv("store_data/final_merged_data.csv")
print(df['코드'].unique())
```

## 📊 분석 품질 지표

- **완성도**: 필수 분석 섹션 완료 여부 (0-1)
- **정확성**: 데이터 활용도 (0-1)
- **관련성**: 쿼리와의 관련성 (0-1)
- **실행가능성**: 권고사항의 실행 가능성 (0-1)
- **종합 품질**: 위 지표의 가중 평균

## 🤝 기여

개선 사항이나 버그 리포트는 언제든 환영합니다!

## 📄 라이선스

이 프로젝트는 내부용 모듈입니다.

## 🔗 관련 모듈

- `commercial_agent.py`: 상권 분석
- `industry_agent.py`: 업종 분석
- `mobility_agent.py`: 유동인구 분석

---

**Version**: 2.0.0  
**Last Updated**: 2025-10-12  
**Framework**: LangGraph Compatible ✅

