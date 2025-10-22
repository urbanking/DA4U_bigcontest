# Streamlit App 개선 가이드

## 현재 문제점
1. ❌ 시각화가 각 탭에 제대로 연결되지 않음
2. ❌ 폰트 문제 (한글 표시 이상)
3. ❌ Query Agent와 Consultation Agent 미구현
4. ❌ OpenAI Agents SDK 미사용

## 해결 방안

### 1. 한글 폰트 문제 해결 ✅
```python
# app.py 상단에 추가
import matplotlib
import matplotlib.pyplot as plt
import platform

system = platform.system()
if system == "Windows":
    plt.rcParams['font.family'] = 'Malgun Gothic'
elif system == "Darwin":
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'NanumGothic'
matplotlib.rcParams['axes.unicode_minus'] = False

# CSS로 웹폰트 적용
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    * {
        font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)
```

### 2. Query Agent 구현 ✅
파일: `open_sdk/streamlit_app/ai_agents/query_agent.py`

```python
from agents import Agent, Runner

query_classifier_agent = Agent(
    name="Query Classifier",
    model="gemini-2.0-flash-exp",
    instructions="...",
    output_type=dict
)

def classify_query_sync(user_input: str) -> Dict[str, Any]:
    result = Runner.run_sync(query_classifier_agent, user_input)
    return result.final_output
```

### 3. Consultation Agent 구현 ✅
파일: `open_sdk/streamlit_app/ai_agents/consultation_agent.py`

```python
from agents import Agent, Runner, SQLiteSession

def create_consultation_agent(store_code, analysis_data, final_md):
    agent = Agent(
        name=f"Store Consultant for {store_code}",
        model="gemini-2.0-flash-exp",
        instructions=f"Context: {analysis_data}...",
        output_type=str
    )
    return agent

def chat_with_consultant_sync(agent, user_message, session):
    result = Runner.run_sync(agent, user_message, session=session)
    return result.final_output
```

### 4. 시각화 연결 🔄
각 display 함수에 시각화 추가:

```python
def display_customer_analysis(analysis_data):
    # 기존 데이터 표시...
    
    # 시각화 추가
    viz = analysis_data.get("visualizations", {})
    store_charts = viz.get("store_charts", [])
    
    customer_charts = [c for c in store_charts 
                      if any(k in c["name"].lower() 
                      for k in ["age", "gender", "customer"])]
    
    for chart in customer_charts:
        st.image(chart["path"], caption=chart["name"])
```

### 5. Consultation 모드 구현 🔄
```python
# 세션 상태 추가
if 'consultation_mode' not in st.session_state:
    st.session_state.consultation_mode = False

# 버튼 추가
if st.button("💬 상담 시작"):
    # 1. 모든 JSON 통합
    merged_data, merged_md = merge_all_analysis_results(output_dir)
    
    # 2. Consultation Agent 생성
    agent = create_consultation_agent(store_code, merged_data, merged_md)
    session = create_consultation_session(store_code)
    
    # 3. 상담 모드로 전환
    st.session_state.consultation_mode = True
    st.session_state.consultation_agent = agent
    st.session_state.consultation_session = session
```

## 다음 단계

### Agent Mode 워크플로우
```
User Input
    ↓
[Query Classifier Agent]
    ├─→ STORE_CODE → run_analysis.py → Display Results
    └─→ GENERAL_QUERY → Show Instructions

After Analysis Complete:
    ↓
[상담 시작 버튼]
    ↓
[Merge all JSONs into one]
    ↓
[Create Consultation Agent with full context]
    ↓
[Chat Interface with SQLiteSession]
```

### 필요한 작업
1. ✅ Query Agent 구현 완료
2. ✅ Consultation Agent 구현 완료
3. 🔄 app.py에 시각화 연결
4. 🔄 app.py에 Consultation 모드 추가
5. ⏸️ 테스트 및 디버깅

## 참고 문서
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [Agents SDK Sessions](https://openai.github.io/openai-agents-python/features/sessions/)

