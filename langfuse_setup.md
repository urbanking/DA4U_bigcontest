# LangGraph + Langfuse 통합 설정 가이드

## 개요
LangGraph와 Langfuse를 통합하여 LLM 에이전트 워크플로우의 완전한 observability를 확보합니다.

## 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```bash
# Langfuse Configuration (LLM Agent Observability)
LANGFUSE_PUBLIC_KEY=pk-lf-24239b84-4356-4b4d-833a-c91af853d7d8
LANGFUSE_SECRET_KEY=sk-lf-f84bd00b-cf18-4d13-aab1-86e186311946
LANGFUSE_HOST=https://cloud.langfuse.com

# Orchestrator Type 설정
ORCHESTRATOR_TYPE=langgraph

# 기타 필요한 API 키들
OPENAI_API_KEY=your_openai_api_key_here
```

## Langfuse 프로젝트 정보

- **Project Name**: bigcontest_agent
- **Project ID**: cmgxp5t1w0088ad07g36l5qeg
- **Organization**: new (ID: cmgxp5aot004ead07ijfe365v)
- **Region**: EU

## LangGraph + Langfuse 통합 방식

### 자동 콜백 기반 추적
- LangGraph의 `CallbackHandler`를 통해 자동으로 모든 노드와 엣지가 추적됩니다
- 수동 span 생성 없이 LangGraph가 자동으로 각 단계를 기록합니다
- 더 정확하고 일관된 observability가 보장됩니다

### 추적되는 데이터

#### 1. 워크플로우 전체 트레이스
- 전체 LangGraph 실행 플로우
- 각 노드별 시작/완료 시간과 상태
- 엣지 간 데이터 흐름

#### 2. LangGraph 노드별 자동 추적
- **Planner**: 의도 분석 및 플랜 결정
- **DataAgent**: 데이터 분석 실행  
- **MarketingAgent**: 마케팅 전략 생성
- **ResultSynthesizer**: 최종 결과 통합

#### 3. 메타데이터 및 상태 정보
- 쿼리 정보 및 실행 모드
- 실행 계획 타입 (data/marketing/hybrid)
- 에러 정보 및 상태 코드
- LangGraph 내부 상태 변화

## Langfuse 대시보드에서 확인할 수 있는 정보

### LangGraph 통합을 통한 향상된 observability:

1. **LangGraph 워크플로우 트레이스**: 전체 실행 플로우의 완전한 시각화
2. **노드별 실행 세부사항**: 각 LangGraph 노드의 시작/완료 시간과 입출력
3. **엣지별 데이터 흐름**: 노드 간 데이터 전달 과정 추적  
4. **성능 메트릭**: LangGraph 전체 및 개별 노드의 실행 시간과 성공률
5. **에러 분석**: 실패한 노드와 에러가 발생한 지점의 상세 정보
6. **상태 변화 추적**: LangGraph State의 시간별 변화 확인

## 사용법

환경 변수 설정 후 시스템을 실행하면 자동으로 Langfuse로 트레이싱이 시작됩니다:

```bash
# LangGraph 오케스트레이터 실행
python run_backend.py

# 통합 테스트 실행 (권장)
python test_langfuse_integration.py

# 또는 직접 테스트
python -c "
import asyncio
from backend.services.langgraph_orchestrator import orchestrator

async def test():
    result = await orchestrator.execute('왕십리역 상권 분석해줘', 'consulting')
    print(result)

asyncio.run(test())
"
```

## 테스트 방법

1. **환경 변수 설정**:
   ```bash
   export LANGFUSE_PUBLIC_KEY="pk-lf-24239b84-4356-4b4d-833a-c91af853d7d8"
   export LANGFUSE_SECRET_KEY="sk-lf-f84bd00b-cf18-4d13-aab1-86e186311946"
   export LANGFUSE_HOST="https://cloud.langfuse.com"
   ```

2. **테스트 실행**:
   ```bash
   python test_langfuse_integration.py
   ```

3. **Langfuse 대시보드 확인**:
   - https://cloud.langfuse.com 에 로그인
   - "bigcontest_agent" 프로젝트 선택
   - 실시간으로 에이전트 실행 상황 모니터링

Langfuse 대시보드에서 실시간으로 에이전트 실행 상황을 모니터링할 수 있습니다.
