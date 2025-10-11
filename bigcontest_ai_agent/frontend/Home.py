"""
메인 페이지
"""
import streamlit as st

st.set_page_config(
    page_title="BigContest AI Agent",
    page_icon="🏪",
    layout="wide"
)

st.title("🏪 BigContest AI Agent")
st.markdown("### LangGraph 기반 멀티에이전트 가게 분석 시스템")

st.markdown("""
## 주요 기능

### 🏪 Store Report
가게의 상권, 업종, 접근성, 이동데이터를 종합 분석하여 리포트를 생성합니다.

### 📈 Metrics Dashboard
CVI, ASI, SCI, GMI 등 핵심 지표를 계산하고 시각화합니다.

### 🩺 Diagnostic Report
지표 기반으로 문제점을 진단하고 개선 방안을 제시합니다.

### 💡 Marketing Strategy
진단 결과를 바탕으로 맞춤형 마케팅 전략을 제안합니다.

---

## 시작하기

좌측 사이드바에서 원하는 메뉴를 선택하세요.
""")

# 가게 코드 입력
st.markdown("### 가게 선택")
store_code = st.text_input("가게 코드를 입력하세요", placeholder="STORE_001")

if store_code:
    st.session_state["store_code"] = store_code
    st.success(f"선택된 가게: {store_code}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 전체 분석 실행", use_container_width=True):
            st.info("전체 파이프라인을 실행합니다...")
            # TODO: API 호출
    
    with col2:
        if st.button("📊 리포트 보기", use_container_width=True):
            st.switch_page("pages/1_🏪_Store_Report.py")
    
    with col3:
        if st.button("📈 지표 보기", use_container_width=True):
            st.switch_page("pages/2_📈_Metrics_Dashboard.py")

