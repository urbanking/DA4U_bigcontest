# 멀티 에이전트 상권 분석 시스템 가이드

## 🎯 시스템 개요

LangGraph 기반 멀티 에이전트 시스템으로 상권 분석을 수행합니다.

## 📁 프로젝트 구조

```
c:\agent1\
├── main.py                          # 🚀 메인 실행 파일
├── agents/
│   ├── modules/                     # 모듈화된 에이전트들
│   │   ├── modular_agent_base.py    # 베이스 클래스
│   │   ├── planner_agent_module.py  # 계획 수립 에이전트
│   │   ├── commercial_agent_module.py # 상권 분석 에이전트
│   │   ├── customer_agent_module.py # 고객 분석 에이전트
│   │   ├── store_agent_module.py    # 매장 분석 에이전트
│   │   ├── industry_agent_module.py # 산업 분석 에이전트
│   │   ├── accessibility_agent_module.py # 접근성 분석 에이전트
│   │   ├── mobility_agent_module.py # 유동인구 분석 에이전트
│   │   └── marketing_agent_module.py # 마케팅 전략 에이전트
│   ├── base_agent.py               # 기존 베이스 클래스 (참고용)
│   ├── langgraph_base_agent.py     # LangGraph 베이스 클래스
│   ├── planner.py                  # 기존 플래너 (참고용)
│   └── orchestrator.py             # 기존 오케스트레이터 (참고용)
├── backend/                        # 백엔드 시스템
├── database/                       # 데이터베이스
└── requirements.txt                # 의존성
```

## 🚀 시스템 실행

### 메인 실행 파일
```bash
python main.py
```

### 실행 흐름
1. **Planner Agent** - 계획 수립
2. **Orchestrator** - 필요한 에이전트 선택
3. **Specialized Agents** - 전문 분석 수행
4. **Synthesis** - 결과 종합
5. **Final Report** - 최종 보고서 생성

## 🔧 에이전트 모듈 개발 가이드

### 각 팀에서 구현해야 할 메서드들

#### 1. `_perform_xxx_analysis` 메서드
```python
async def _perform_commercial_analysis(
    self, 
    user_query: str, 
    context: Dict[str, Any], 
    knowledge: Dict[str, Any]
) -> Dict[str, Any]:
    """
    실제 상권 분석 수행 - 각 팀에서 구현
    
    Args:
        user_query: 사용자 쿼리
        context: 컨텍스트
        knowledge: Context7 MCP 지식
        
    Returns:
        상권 분석 결과
    """
    # TODO: 각 팀에서 구현
    # 실제 분석 로직 구현
```

#### 2. `_perform_self_evaluation` 메서드
```python
async def _perform_self_evaluation(self, analysis_result: Dict[str, Any]) -> Dict[str, float]:
    """
    자가 평가 수행 - 각 팀에서 구현
    
    Args:
        analysis_result: 분석 결과
        
    Returns:
        자가 평가 점수
    """
    # TODO: 각 팀에서 구현
    # 자가 평가 로직 구현
```

### Context7 MCP 활용

#### 플레이스홀더 (현재)
```python
# 현재는 플레이스홀더
knowledge = await self.mcp_interface.search_knowledge(f"상권 분석 {user_query}")
```

#### 실제 구현시
```python
# 실제 구현시 MCP 도구 사용
# mcp_context7_resolve-library-id 호출
# mcp_context7_get-library-docs 호출
```

### Sequential Thinking MCP (PlannerAgentModule)

#### 플레이스홀더 (현재)
```python
# 현재는 플레이스홀더
analysis_result = await self._perform_planning_with_sequential_thinking(
    user_query, context, knowledge
)
```

#### 실제 구현시
```python
# 실제 구현시 Sequential Thinking MCP 사용
# mcp_server-sequential-thinking_sequentialthinking 호출
```

## 📊 테스트 결과

### 테스트 케이스 1: "강남 20대 타겟 카페 창업 가능한가?"
- ✅ Planner Agent 실행
- ✅ Orchestrator 실행 (고객 분석 선택)
- ✅ Customer Agent 실행
- ✅ Synthesis 실행
- ✅ Final Report 생성
- **품질 점수**: {'customer': 0.8}
- **실행된 에이전트**: ['planner', 'customer']

### 테스트 케이스 2: "우리 카페 마케팅 전략 좀 알려주세요"
- ✅ Planner Agent 실행
- ✅ Orchestrator 실행 (마케팅 전략 선택)
- ✅ Marketing Agent 실행
- ✅ Synthesis 실행
- ✅ Final Report 생성
- **품질 점수**: {'marketing': 0.8}
- **실행된 에이전트**: ['planner', 'marketing']

## 🎯 각 에이전트별 특화 정보

### PlannerAgentModule
- **전문분야**: 계획 수립
- **주요 분석**: 사용자 쿼리 분석, 실행 계획 수립, 필요한 에이전트 선택, Sequential Thinking 기반 계획 개선
- **MCP 도구**: Sequential Thinking MCP, Context7 MCP

### CommercialAgentModule
- **전문분야**: 상권 분석
- **주요 분석**: 상권 성숙도 분석, 경쟁 분석, 상권 트렌드 분석, 창업 적합성 평가
- **필요 데이터**: 위치 정보, 업종 정보, 상권 데이터, 경쟁사 정보

### CustomerAgentModule
- **전문분야**: 고객 분석
- **주요 분석**: 고객 세분화 분석, 고객 행동 패턴 분석, 고객 이탈 분석, 타겟 고객 정의
- **필요 데이터**: 고객 데이터, 거래 데이터, 고객 피드백, 행동 로그

### MarketingAgentModule
- **전문분야**: 마케팅 전략
- **주요 분석**: 마케팅 전략 수립, 채널 분석 및 추천, 브랜딩 전략, 고객 획득 전략
- **필요 데이터**: 상권 분석 결과, 고객 분석 결과, 경쟁사 정보, 마케팅 예산

## 🔄 LangGraph 워크플로우

```
Planner → Orchestrator → [Specialized Agents] → Synthesis → Final Report
```

### 노드들
1. **planner** - 계획 수립
2. **orchestrator** - 에이전트 선택
3. **commercial** - 상권 분석
4. **customer** - 고객 분석
5. **store** - 매장 분석
6. **industry** - 산업 분석
7. **accessibility** - 접근성 분석
8. **mobility** - 유동인구 분석
9. **marketing** - 마케팅 전략
10. **synthesis** - 결과 종합
11. **final_report** - 최종 보고서

## 🎉 완성된 시스템 특징

### ✅ 완전한 모듈화
- 각 에이전트가 독립적인 모듈
- 내부 구현은 각 팀에서 개발
- 표준화된 인터페이스 제공

### ✅ LangGraph 완전 지원
- 모든 에이전트가 LangGraph 노드로 동작
- 일관된 상태 관리
- 에러 핸들링 및 복구

### ✅ Context7 MCP 준비 완료
- 플레이스홀더로 인터페이스 제공
- 실제 구현시 MCP 도구로 교체 가능

### ✅ 개발 친화적 구조
- 명확한 구현 가이드
- TODO 주석으로 구현 포인트 표시
- 테스트 코드 제공

## 🚀 다음 단계

1. 각 팀에서 에이전트 모듈의 내부 구현 개발
2. Context7 MCP 플레이스홀더를 실제 MCP 도구로 교체
3. Sequential Thinking MCP 통합
4. 실제 데이터 연동
5. 프론트엔드 연동 (Streamlit)

---

**시스템이 완벽하게 준비되었습니다! 각 팀에서 내부 구현을 개발할 준비가 완료되었습니다!** 🎉
