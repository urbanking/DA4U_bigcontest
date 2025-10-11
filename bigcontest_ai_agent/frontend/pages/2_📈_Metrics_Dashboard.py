"""
지표/KPI 대시보드
"""
import streamlit as st
from frontend.utils.api_client import APIClient
from frontend.components.cards import metric_card
from frontend.components.charts import create_gauge_chart, create_radar_chart

st.set_page_config(page_title="Metrics Dashboard", page_icon="📈", layout="wide")

st.title("📈 Metrics Dashboard")

# 가게 코드 확인
store_code = st.session_state.get("store_code", "")

if not store_code:
    st.warning("가게를 선택해주세요.")
    st.stop()

st.markdown(f"### 가게 코드: {store_code}")

# API 클라이언트
api_client = APIClient()

# 지표 로드
with st.spinner("지표를 불러오는 중..."):
    try:
        metrics = api_client.get_metrics(store_code)
        
        if metrics:
            metrics_data = metrics.get("metrics", {})
            
            # 주요 지표 카드
            st.markdown("### 주요 지표")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                cvi = metrics_data.get("cvi", {})
                metric_card(
                    "상권 활성도 (CVI)",
                    cvi.get("value", 0),
                    cvi.get("grade", "N/A")
                )
            
            with col2:
                asi = metrics_data.get("asi", {})
                metric_card(
                    "접근성 (ASI)",
                    asi.get("value", 0),
                    asi.get("grade", "N/A")
                )
            
            with col3:
                sci = metrics_data.get("sci", {})
                metric_card(
                    "경쟁력 (SCI)",
                    sci.get("value", 0),
                    sci.get("grade", "N/A")
                )
            
            with col4:
                gmi = metrics_data.get("gmi", {})
                metric_card(
                    "성장성 (GMI)",
                    gmi.get("value", 0),
                    gmi.get("grade", "N/A")
                )
            
            # 시각화
            st.markdown("### 지표 시각화")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 종합 점수")
                overall_score = metrics.get("overall_score", 0)
                st.metric("Overall Score", f"{overall_score:.1f}")
            
            with col2:
                st.markdown("#### 지표 비교")
                # TODO: 레이더 차트 등 추가
                st.info("차트 준비 중...")
        
        else:
            st.error("지표를 찾을 수 없습니다.")
            if st.button("지표 계산"):
                with st.spinner("지표 계산 중..."):
                    result = api_client.calculate_metrics(store_code)
                    if result:
                        st.success("지표가 계산되었습니다!")
                        st.rerun()
    
    except Exception as e:
        st.error(f"오류 발생: {str(e)}")

