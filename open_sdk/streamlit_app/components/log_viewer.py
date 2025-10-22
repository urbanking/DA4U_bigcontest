"""
실시간 로그 뷰어 컴포넌트
사이드바에 분석 진행 상황을 실시간으로 표시합니다.
"""
import streamlit as st
from typing import List
import time

def render_log_viewer():
    """사이드바에 로그 뷰어를 렌더링합니다."""
    st.sidebar.markdown("### 📊 분석 진행 상황")
    
    # 로그 상태 초기화
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    
    # 로그 컨테이너
    log_container = st.sidebar.container()
    
    # 최근 로그 표시 (최대 20개)
    recent_logs = st.session_state.logs[-20:] if st.session_state.logs else []
    
    if recent_logs:
        with log_container:
            for log in recent_logs:
                # 로그 레벨에 따른 색상 적용
                if log.startswith("[ERROR]"):
                    st.sidebar.error(log)
                elif log.startswith("[WARN]"):
                    st.sidebar.warning(log)
                elif log.startswith("[OK]"):
                    st.sidebar.success(log)
                elif log.startswith("[INFO]"):
                    st.sidebar.info(log)
                else:
                    st.sidebar.text(log)
    else:
        st.sidebar.info("분석 로그가 없습니다.")
    
    # 로그 정리 버튼
    if st.sidebar.button("🗑️ 로그 정리"):
        st.session_state.logs = []
        st.rerun()

def add_log(message: str):
    """새로운 로그 메시지를 추가합니다."""
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    
    timestamp = time.strftime("%H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    st.session_state.logs.append(log_message)
    
    # 로그가 너무 많으면 오래된 것 제거
    if len(st.session_state.logs) > 100:
        st.session_state.logs = st.session_state.logs[-50:]

def get_logs() -> List[str]:
    """현재 로그 목록을 반환합니다."""
    return st.session_state.get('logs', [])

def clear_logs():
    """로그를 정리합니다."""
    st.session_state.logs = []

def render_progress_bar():
    """분석 진행률 바를 렌더링합니다."""
    if st.session_state.get('is_analyzing', False):
        st.sidebar.markdown("### ⏳ 분석 진행률")
        
        # 단계별 진행률
        steps = [
            "주소 분석",
            "Store 분석", 
            "Marketing 분석",
            "Mobility 분석",
            "Panorama 분석",
            "Marketplace 분석",
            "결과 통합"
        ]
        
        current_step = st.session_state.get('current_step', 0)
        progress = (current_step + 1) / len(steps)
        
        st.sidebar.progress(progress)
        st.sidebar.text(f"단계 {current_step + 1}/{len(steps)}: {steps[current_step]}")
        
        # 예상 남은 시간
        if current_step > 0:
            estimated_time = (len(steps) - current_step) * 30  # 단계당 30초 가정
            st.sidebar.text(f"예상 남은 시간: {estimated_time}초")

def update_progress(step: int):
    """진행률을 업데이트합니다."""
    st.session_state.current_step = step
    add_log(f"진행 단계: {step + 1}/7")
