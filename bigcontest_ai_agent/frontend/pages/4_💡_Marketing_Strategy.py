"""
마케팅 전략 제안 시각화
"""
import streamlit as st
from frontend.utils.api_client import APIClient

st.set_page_config(page_title="Marketing Strategy", page_icon="💡", layout="wide")

st.title("💡 Marketing Strategy")

# 가게 코드 확인
store_code = st.session_state.get("store_code", "")

if not store_code:
    st.warning("가게를 선택해주세요.")
    st.stop()

st.markdown(f"### 가게 코드: {store_code}")

# API 클라이언트
api_client = APIClient()

# 마케팅 전략 로드
with st.spinner("마케팅 전략을 불러오는 중..."):
    try:
        marketing = api_client.get_marketing_strategy(store_code)
        
        if marketing:
            # 인사이트
            st.markdown("### 🔍 핵심 인사이트")
            insights = marketing.get("insights", {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 강점 (Strengths)")
                for strength in insights.get("strengths", []):
                    st.markdown(f"- {strength}")
                
                st.markdown("#### 기회 (Opportunities)")
                for opp in insights.get("opportunities", []):
                    st.markdown(f"- {opp}")
            
            with col2:
                st.markdown("#### 약점 (Weaknesses)")
                for weakness in insights.get("weaknesses", []):
                    st.markdown(f"- {weakness}")
                
                st.markdown("#### 위협 (Threats)")
                for threat in insights.get("threats", []):
                    st.markdown(f"- {threat}")
            
            # 타깃 세그먼트
            st.markdown("### 🎯 타깃 고객 세그먼트")
            target_segments = marketing.get("target_segments", [])
            
            if target_segments:
                for segment in target_segments:
                    with st.expander(f"📊 {segment.get('name', 'Unknown Segment')}"):
                        st.write(segment)
            else:
                st.info("타깃 세그먼트 정보가 없습니다.")
            
            # 마케팅 전략
            st.markdown("### 📢 추천 마케팅 전략")
            strategies = marketing.get("strategies", [])
            
            if strategies:
                for i, strategy in enumerate(strategies, 1):
                    st.markdown(f"#### 전략 {i}: {strategy.get('strategy_name', 'Unknown')}")
                    st.markdown(f"**설명:** {strategy.get('description', '')}")
                    st.markdown(f"**타깃:** {', '.join(strategy.get('target_segments', []))}")
                    
                    expected_impact = strategy.get("expected_impact", {})
                    if expected_impact:
                        st.markdown("**예상 효과:**")
                        for key, value in expected_impact.items():
                            st.markdown(f"- {key}: {value}")
                    
                    st.divider()
            else:
                st.info("추천 전략이 없습니다.")
            
            # KPI 예측
            st.markdown("### 📊 KPI 예측")
            kpi_estimates = marketing.get("kpi_estimates", {})
            
            if kpi_estimates:
                for strategy_name, kpis in kpi_estimates.items():
                    with st.expander(f"📈 {strategy_name}"):
                        st.json(kpis)
            else:
                st.info("KPI 예측 정보가 없습니다.")
        
        else:
            st.error("마케팅 전략을 찾을 수 없습니다.")
            if st.button("마케팅 전략 생성"):
                with st.spinner("마케팅 전략 생성 중..."):
                    result = api_client.generate_marketing_strategy(store_code)
                    if result:
                        st.success("마케팅 전략이 생성되었습니다!")
                        st.rerun()
    
    except Exception as e:
        st.error(f"오류 발생: {str(e)}")

