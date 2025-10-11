"""
진단 결과/처방 시각화
"""
import streamlit as st
from frontend.utils.api_client import APIClient
from frontend.components.alerts import create_issue_alert

st.set_page_config(page_title="Diagnostic Report", page_icon="🩺", layout="wide")

st.title("🩺 Diagnostic Report")

# 가게 코드 확인
store_code = st.session_state.get("store_code", "")

if not store_code:
    st.warning("가게를 선택해주세요.")
    st.stop()

st.markdown(f"### 가게 코드: {store_code}")

# API 클라이언트
api_client = APIClient()

# 진단 결과 로드
with st.spinner("진단 결과를 불러오는 중..."):
    try:
        diagnostic = api_client.get_diagnostic(store_code)
        
        if diagnostic:
            # 전체 건강도
            overall_health = diagnostic.get("overall_health", "unknown")
            
            health_colors = {
                "healthy": "🟢",
                "attention_needed": "🟡",
                "warning": "🟠",
                "critical": "🔴"
            }
            
            health_messages = {
                "healthy": "건강한 상태입니다",
                "attention_needed": "주의가 필요합니다",
                "warning": "경고 상태입니다",
                "critical": "심각한 문제가 있습니다"
            }
            
            st.markdown(f"### {health_colors.get(overall_health, '⚪')} 전체 건강도: {health_messages.get(overall_health, '알 수 없음')}")
            
            # 문제점
            st.markdown("### 🔍 발견된 문제점")
            issues = diagnostic.get("issues", [])
            
            if issues:
                for issue in issues:
                    create_issue_alert(
                        issue.get("severity", "info"),
                        issue.get("issue_type", ""),
                        issue.get("description", "")
                    )
            else:
                st.success("발견된 문제점이 없습니다!")
            
            # 권고사항
            st.markdown("### 💡 개선 권고사항")
            recommendations = diagnostic.get("recommendations", [])
            
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"{i}. **{rec.get('recommendation', '')}**")
                    st.markdown(f"   - 우선순위: {rec.get('priority', 'medium')}")
                    st.markdown(f"   - 예상 효과: {rec.get('impact', 'medium')}")
            else:
                st.info("권고사항이 없습니다.")
        
        else:
            st.error("진단 결과를 찾을 수 없습니다.")
            if st.button("진단 실행"):
                with st.spinner("진단 실행 중..."):
                    result = api_client.run_diagnostic(store_code)
                    if result:
                        st.success("진단이 완료되었습니다!")
                        st.rerun()
    
    except Exception as e:
        st.error(f"오류 발생: {str(e)}")

