"""
가게 분석 리포트 시각화
"""
import streamlit as st
from frontend.utils.api_client import APIClient
from frontend.components.cards import metric_card

st.set_page_config(page_title="Store Report", page_icon="🏪", layout="wide")

st.title("🏪 Store Report")

# 가게 코드 확인
store_code = st.session_state.get("store_code", "")

if not store_code:
    st.warning("가게를 선택해주세요. Home 페이지로 이동하여 가게 코드를 입력하세요.")
    if st.button("Home으로 이동"):
        st.switch_page("Home.py")
    st.stop()

st.markdown(f"### 가게 코드: {store_code}")

# API 클라이언트
api_client = APIClient()

# 리포트 로드
with st.spinner("리포트를 불러오는 중..."):
    try:
        report = api_client.get_store_report(store_code)
        
        if report:
            # 탭 구성
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📋 요약",
                "🏢 상권 분석",
                "🏭 업종 분석",
                "🚗 접근성 분석",
                "📍 이동데이터"
            ])
            
            with tab1:
                st.markdown("### 종합 요약")
                st.write(report.get("summary", "요약 정보가 없습니다."))
            
            with tab2:
                st.markdown("### 상권 분석")
                commercial = report.get("commercial", {})
                st.json(commercial)
            
            with tab3:
                st.markdown("### 업종 분석")
                industry = report.get("industry", {})
                st.json(industry)
            
            with tab4:
                st.markdown("### 접근성 분석")
                accessibility = report.get("accessibility", {})
                st.json(accessibility)
            
            with tab5:
                st.markdown("### 이동데이터 분석")
                mobility = report.get("mobility", {})
                st.json(mobility)
        else:
            st.error("리포트를 찾을 수 없습니다.")
            if st.button("리포트 생성"):
                with st.spinner("리포트 생성 중..."):
                    result = api_client.generate_store_report(store_code)
                    if result:
                        st.success("리포트가 생성되었습니다!")
                        st.rerun()
    
    except Exception as e:
        st.error(f"오류 발생: {str(e)}")

