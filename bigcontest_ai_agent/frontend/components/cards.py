"""
KPI 카드 컴포넌트
"""
import streamlit as st


def metric_card(title: str, value: float, grade: str = ""):
    """지표 카드"""
    st.metric(
        label=title,
        value=f"{value:.1f}",
        delta=f"Grade: {grade}" if grade else None
    )


def info_card(title: str, content: str, icon: str = "ℹ️"):
    """정보 카드"""
    st.markdown(f"""
    <div style="padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6; margin-bottom: 1rem;">
        <h4>{icon} {title}</h4>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)


def status_card(status: str, message: str):
    """상태 카드"""
    colors = {
        "success": "#d4edda",
        "warning": "#fff3cd",
        "error": "#f8d7da",
        "info": "#d1ecf1"
    }
    
    bg_color = colors.get(status, colors["info"])
    
    st.markdown(f"""
    <div style="padding: 1rem; border-radius: 0.5rem; background-color: {bg_color}; margin-bottom: 1rem;">
        <p><strong>{message}</strong></p>
    </div>
    """, unsafe_allow_html=True)

