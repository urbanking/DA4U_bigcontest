"""
경고/진단 배지 UI
"""
import streamlit as st


def create_issue_alert(severity: str, issue_type: str, description: str):
    """이슈 알림 생성"""
    severity_config = {
        "critical": {
            "icon": "🔴",
            "color": "#f8d7da",
            "title": "심각"
        },
        "warning": {
            "icon": "🟠",
            "color": "#fff3cd",
            "title": "경고"
        },
        "info": {
            "icon": "🔵",
            "color": "#d1ecf1",
            "title": "정보"
        }
    }
    
    config = severity_config.get(severity, severity_config["info"])
    
    st.markdown(f"""
    <div style="padding: 1rem; border-radius: 0.5rem; background-color: {config['color']}; margin-bottom: 1rem; border-left: 4px solid #000;">
        <h4>{config['icon']} {config['title']}: {issue_type}</h4>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)


def create_success_badge(text: str):
    """성공 배지"""
    st.markdown(f"""
    <span style="background-color: #d4edda; color: #155724; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-weight: bold;">
        ✓ {text}
    </span>
    """, unsafe_allow_html=True)


def create_warning_badge(text: str):
    """경고 배지"""
    st.markdown(f"""
    <span style="background-color: #fff3cd; color: #856404; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-weight: bold;">
        ⚠ {text}
    </span>
    """, unsafe_allow_html=True)


def create_error_badge(text: str):
    """오류 배지"""
    st.markdown(f"""
    <span style="background-color: #f8d7da; color: #721c24; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-weight: bold;">
        ✗ {text}
    </span>
    """, unsafe_allow_html=True)

