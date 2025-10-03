# 🏪 멀티 에이전트 상권 분석 시스템

## 📋 프로젝트 개요

**2-Tier Orchestrator 구조의 멀티 에이전트 상권 분석 시스템**은 Sequential Thinking MCP를 활용하여 상권 분석, 고객 분석, 매장 분석, 산업 분석, 접근성 분석, 유동인구 분석을 통합하여 종합적인 상권 인사이트와 마케팅 전략을 제공하는 AI 시스템입니다.

### 🎯 핵심 특징

- **2-Tier Orchestrator 구조**: Primary (Data Consulting vs Marketing) → Secondary (Specialized Agents)
- **Sequential Thinking MCP**: 실제 MCP 서버를 활용한 체계적 사고 과정
- **LangGraph 기반 워크플로우**: 노드-엣지 구조로 명확한 실행 흐름
- **모듈화된 프레임워크**: 각 에이전트를 독립적인 모듈로 개발 가능
- **장단기 메모리 시스템**: 사용자별 분석 히스토리 및 패턴 학습
- **자가 평가 및 품질 보장**: 각 에이전트가 품질 임계값 달성까지 자기 루프

## 🏗️ 2-Tier Orchestrator 아키텍처

```
📊 멀티 에이전트 상권 분석 시스템 (2-Tier Orchestrator)
│
├── 🧠 Planner Agent
│   ├── Sequential Thinking MCP 활용
│   ├── 사용자 쿼리 분석 및 계획 수립
│   └── 메인 에이전트 타입 결정 (data_consulting vs marketing)
│
├── 🎯 Primary Orchestrator (1차)
│   ├── Planner의 계획 검증 및 조정
│   ├── Data Consulting vs Marketing 선택
│   └── 쿼리 재분석을 통한 최종 결정
│
├── 🔧 Secondary Orchestrator (2차)
│   ├── Data Consulting 내에서 전문 에이전트들 선택
│   ├── 에이전트 간 의존성 고려한 실행 순서 결정
│   └── 병렬 실행 관리
│
├── 🤖 전문 에이전트 모듈들 (각 팀에서 구현)
│   ├── 상권 분석 모듈 (CommercialAgentModule)
│   ├── 고객 분석 모듈 (CustomerAgentModule)
│   ├── 매장 분석 모듈 (StoreAgentModule)
│   ├── 산업 분석 모듈 (IndustryAgentModule)
│   ├── 접근성 분석 모듈 (AccessibilityAgentModule)
│   ├── 유동인구 분석 모듈 (MobilityAgentModule)
│   └── 마케팅 전략 모듈 (MarketingAgentModule)
│
├── 🔍 각 모듈별 자기 평가 시스템
│   ├── 품질 점수 계산 (완성도, 정확도, 관련성, 실행가능성)
│   ├── 메모리 시스템을 활용한 컨텍스트 고려
│   └── 품질 임계값 달성 시 조기 종료
│
└── 📊 Synthesis & Final Report
    ├── 모든 에이전트 결과 종합
    ├── 메인 에이전트 타입별 최적화된 보고서 생성
    └── 실행 가능한 권장사항 및 마케팅 전략 제안
```

## 🛠️ 기술 스택

### Core Framework
- **LangGraph**: 노드-엣지 기반 워크플로우 관리
- **OpenAI GPT-4**: LLM 추론 엔진
- **Sequential Thinking MCP**: 체계적 사고 과정 (Smithery 서버)

### Backend & Database
- **PostgreSQL**: 3계층 데이터 저장소 (Macro, Meso, Micro)
- **SQLAlchemy**: ORM 및 데이터베이스 관리
- **Agent Memory System**: 장단기 메모리 및 학습 패턴

### Frontend & Visualization
- **Streamlit**: 대시보드 및 UI
- **Plotly**: 데이터 시각화
- **Pandas/NumPy**: 데이터 처리

### Infrastructure
- **Asyncio**: 비동기 처리
- **ThreadPoolExecutor**: 병렬 처리
- **Context7 MCP**: 지식 검색 및 활용 (준비됨)

## 📁 프로젝트 구조

```
📦 multi-agent-commercial-analysis/
├── 📄 main.py                        # 메인 실행 파일 (2-Tier Orchestrator)
├── 📄 requirements.txt               # 의존성 패키지
├── 📄 SYSTEM_GUIDE.md               # 시스템 가이드
├── 📄 QUICKSTART.md                 # 빠른 시작 가이드
│
├── 📂 agents/                       # 에이전트 모듈
│   ├── base_agent.py                # 기본 에이전트 클래스 (LangGraph 호환)
│   ├── planner_agent.py             # Sequential Thinking MCP 활용 계획 수립
│   ├── primary_orchestrator.py      # 1차 오케스트레이터 (Data Consulting vs Marketing)
│   ├── secondary_orchestrator.py    # 2차 오케스트레이터 (전문 에이전트 선택)
│   └── modules/                     # 전문 에이전트 모듈들 (각 팀에서 구현)
│       ├── commercial_agent_module.py
│       ├── customer_agent_module.py
│       ├── store_agent_module.py
│       ├── industry_agent_module.py
│       ├── accessibility_agent_module.py
│       ├── mobility_agent_module.py
│       └── marketing_agent_module.py
│
├── 📂 backend/                      # 백엔드 시스템
│   ├── api/
│   │   └── main.py                  # FastAPI 서버
│   ├── memory/
│   │   └── agent_memory.py          # 장단기 메모리 시스템
│   ├── mcp/
│   │   └── sequential_thinking_client.py  # Sequential Thinking MCP 클라이언트
│   └── evaluation/
│       └── evaluation_system.py     # 평가 시스템
│
├── 📂 frontend/                     # 프론트엔드
│   └── streamlit_app.py             # Streamlit 대시보드
│
├── 📂 database/                     # 데이터베이스
│   ├── connection.py                # 데이터베이스 연결
│   ├── schema.sql                   # 3계층 데이터 스키마
│   └── memory_tables.sql            # 메모리 테이블 스키마
│
├── 📂 data/                         # 데이터 저장소
└── 📂 crawlers/                     # 데이터 수집 (예정)
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd multi-agent-commercial-analysis

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

```bash
# .env 파일 생성
echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
```

### 3. 시스템 실행

```bash
# 메인 시스템 실행 (2-Tier Orchestrator)
python main.py
```

### 4. 백엔드 서버 실행 (선택사항)

```bash
# FastAPI 백엔드 실행
cd backend/api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 프론트엔드 실행 (선택사항)

```bash
# Streamlit 대시보드 실행
cd frontend
streamlit run streamlit_app.py --server.port 8501
```

## 📊 사용 방법

### 1. 직접 실행 (추천)

```bash
# 시스템 실행
python main.py
```

시스템이 자동으로 테스트 케이스들을 실행하고 결과를 보여줍니다.

### 2. API를 통한 분석 (백엔드 실행 시)

```python
import requests

# 분석 요청
response = requests.post("http://localhost:8000/analyze", json={
    "user_query": "강남 20대 타겟 카페 창업 가능한가?",
    "user_id": "USER_001",
    "context": {"location": "강남구", "business_type": "cafe"}
})

result = response.json()
print(result)
```

### 3. Streamlit 대시보드 사용 (프론트엔드 실행 시)

1. 브라우저에서 http://localhost:8501 접속
2. 분석 질문 입력
3. 실시간 분석 결과 확인
4. 2-Tier Orchestrator 워크플로우 시각화

## 🔧 개발 가이드

### 전문 에이전트 모듈 구현

각 팀에서 담당하는 전문 에이전트 모듈을 구현하세요:

```python
# agents/modules/your_agent_module.py
from agents.base_agent import BaseAgent, AgentState

class YourAgentModule(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="YourAgent")
    
    async def execute_analysis_with_self_evaluation(self, state: AgentState) -> Dict[str, Any]:
        # 1. 메모리 로드
        memory_insights = await self.load_user_memory(user_id, user_query)
        
        # 2. 실제 분석 로직 구현
        analysis_result = await self._perform_your_analysis(...)
        
        # 3. 자가 평가 구현
        evaluation_result = await self._perform_self_evaluation(...)
        
        # 4. 메모리 저장
        await self.save_to_memory(...)
        
        return self.format_output(...)
    
    async def _perform_your_analysis(self, ...):
        # TODO: 각 팀에서 구현
        pass
    
    async def _perform_self_evaluation(self, ...):
        # TODO: 각 팀에서 구현
        pass
```

### Sequential Thinking MCP 활용

Planner 에이전트에서 Sequential Thinking MCP를 활용하여 계획을 수립합니다:

```python
from backend.mcp.sequential_thinking_client import get_sequential_thinking_client

client = get_sequential_thinking_client()
result = await client.sequential_thinking(
    problem_description="사용자 쿼리 분석 및 실행 계획 수립",
    initial_thoughts=6,
    max_iterations=8
)
```

## 📈 시스템 특징

### 2-Tier Orchestrator 구조

1. **Planner Agent**: Sequential Thinking MCP로 체계적 계획 수립
2. **Primary Orchestrator**: Data Consulting vs Marketing 선택
3. **Secondary Orchestrator**: 전문 에이전트들 선택 및 실행 순서 결정
4. **Specialized Agents**: 각 팀에서 독립적으로 구현
5. **Synthesis**: 모든 결과 종합 및 최종 보고서 생성

### Sequential Thinking MCP 통합

- **실제 MCP 서버**: Smithery Sequential Thinking 서버 활용
- **체계적 사고**: 6-8단계 사고 과정을 통한 계획 수립
- **동적 조정**: 사고 과정 중 계획 수정 및 개선

### 메모리 시스템

- **장기 메모리**: 중요도 기반 장기 저장
- **단기 메모리**: 세션 기반 임시 저장
- **학습 패턴**: 사용자별 분석 패턴 학습

### 품질 보장 시스템

- **자가 평가**: 각 에이전트가 결과 품질 자체 평가
- **품질 점수**: 완성도, 정확도, 관련성, 실행가능성 측정
- **자기 루프**: 품질 임계값 달성까지 반복 실행

## 🎯 워크플로우 예시

### 쿼리: "강남 20대 타겟 카페 창업 가능한가?"

1. **Planner Agent**: Sequential Thinking MCP로 계획 수립
   - 메인 에이전트 타입: "data_consulting" 결정
   - 필요한 전문 에이전트들: ["commercial", "customer"] 식별

2. **Primary Orchestrator**: "data_consulting" 선택 확인

3. **Secondary Orchestrator**: 
   - 전문 에이전트들: ["commercial", "customer"] 선택
   - 실행 순서: commercial → customer (의존성 고려)

4. **Specialized Agents**:
   - Commercial Agent: 상권 분석 수행
   - Customer Agent: 고객 분석 수행

5. **Synthesis**: 모든 결과 종합

6. **Final Report**: 종합 분석 보고서 생성

## 📚 문서

- **[시스템 가이드](SYSTEM_GUIDE.md)**: 전체 시스템 구조 및 사용법
- **[빠른 시작 가이드](QUICKSTART.md)**: 시스템 설치 및 실행

## 🤝 기여 방법

1. **각 팀별 전문 에이전트 구현**:
   - `agents/modules/` 폴더의 해당 에이전트 모듈 선택
   - `_perform_xxx_analysis` 메서드에 실제 분석 로직 구현
   - `_perform_self_evaluation` 메서드에 자가 평가 로직 구현

2. **Sequential Thinking MCP 활용**:
   - 필요시 Planner 에이전트의 Sequential Thinking 로직 개선
   - 각 전문 에이전트에서도 Sequential Thinking 활용 가능

3. **메모리 시스템 활용**:
   - 사용자별 분석 히스토리 활용
   - 패턴 학습을 통한 개인화된 분석 제공

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🆘 지원

문제가 발생하거나 질문이 있으시면:

1. **시스템 가이드** 확인
2. **빠른 시작 가이드** 참조
3. **코드 내 TODO 주석** 확인

---

**🏪 멀티 에이전트 상권 분석 시스템 v3.0**  
*Built with LangGraph, Sequential Thinking MCP, and 2-Tier Orchestrator*