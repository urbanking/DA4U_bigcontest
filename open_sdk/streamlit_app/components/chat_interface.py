"""
채팅 인터페이스 컴포넌트
3단계 인터페이스: input → analyzing → consultation
"""
import streamlit as st
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
import json

from ai_agents.simple_query_classifier import classify_query, extract_store_code
from ai_agents.consultation_agent import create_consultation_session, chat_with_consultant
from utils.analysis_runner import run_analysis_with_logging, check_analysis_status
from components.log_viewer import add_log, update_progress
from components.report_generator import generate_md_report, save_md_report, load_comprehensive_analysis

def render_chat_interface():
    """채팅 인터페이스를 렌더링합니다."""
    
    # 스테이지별 렌더링
    stage = st.session_state.get('stage', 'input')
    
    if stage == 'input':
        render_input_stage()
    elif stage == 'analyzing':
        render_analyzing_stage()
    elif stage == 'consultation':
        render_consultation_stage()

def render_input_stage():
    """입력 단계를 렌더링합니다."""
    st.markdown("### 💬 상점 코드 입력")
    st.markdown("분석할 상점의 10자리 코드를 입력하세요.")
    
    # 입력 폼
    with st.form("store_input_form"):
        store_code = st.text_input(
            "상점 코드",
            placeholder="예: 000F03E44A",
            help="10자리 영숫자 코드를 입력하세요"
        )
        
        submitted = st.form_submit_button("분석 시작", type="primary")
        
        if submitted:
            if store_code and len(store_code.strip()) == 10:
                st.session_state.store_code = store_code.strip()
                st.session_state.stage = 'analyzing'
                st.session_state.is_analyzing = True
                st.session_state.current_step = 0
                st.rerun()
            else:
                st.error("올바른 10자리 상점 코드를 입력해주세요.")

def render_analyzing_stage():
    """분석 중 단계를 렌더링합니다."""
    st.markdown("### 🔄 분석 진행 중")
    
    store_code = st.session_state.get('store_code', '')
    
    if not store_code:
        st.error("상점 코드가 없습니다.")
        st.session_state.stage = 'input'
        st.rerun()
        return
    
    # 진행률 표시
    st.progress(st.session_state.get('current_step', 0) / 7)
    
    # 단계별 표시
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
    st.text(f"현재 단계: {steps[current_step]}")
    
    # 분석 실행
    if st.session_state.get('is_analyzing', False):
        try:
            # 분석 실행 (비동기)
            output_file = run_analysis_with_logging(store_code, add_log)
            
            if output_file:
                # 분석 완료
                st.session_state.is_analyzing = False
                st.session_state.stage = 'consultation'
                st.session_state.analysis_result = output_file
                
                # MD 리포트 생성
                result_dir = Path(output_file).parent
                comprehensive_file = result_dir / "comprehensive_analysis.json"
                
                if comprehensive_file.exists():
                    json_data = load_comprehensive_analysis(str(comprehensive_file))
                    if json_data:
                        md_content = generate_md_report(json_data, store_code)
                        md_file = save_md_report(md_content, store_code, result_dir)
                        st.session_state.md_report = md_file
                        st.session_state.json_data = json_data
                
                add_log("분석 완료! 상담을 시작할 수 있습니다.")
                st.rerun()
            else:
                st.error("분석에 실패했습니다. 다시 시도해주세요.")
                st.session_state.stage = 'input'
                st.session_state.is_analyzing = False
                st.rerun()
                
        except Exception as e:
            st.error(f"분석 중 오류가 발생했습니다: {e}")
            st.session_state.stage = 'input'
            st.session_state.is_analyzing = False
            st.rerun()

def render_consultation_stage():
    """상담 단계를 렌더링합니다."""
    st.markdown("### 💬 AI 상담사와 대화")
    
    store_code = st.session_state.get('store_code', '')
    md_report = st.session_state.get('md_report', '')
    json_data = st.session_state.get('json_data', {})
    
    if not md_report or not json_data:
        st.error("분석 결과를 불러올 수 없습니다.")
        st.session_state.stage = 'input'
        st.rerun()
        return
    
    # 상담 세션 초기화
    if 'agent_session' not in st.session_state:
        try:
            session = create_consultation_session(store_code, md_report, json_data)
            st.session_state.agent_session = session
            st.session_state.messages = []
            
            # 환영 메시지
            welcome_msg = f"안녕하세요! {store_code} 매장 분석이 완료되었습니다. 궁금한 점이 있으시면 언제든 질문해주세요."
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
            
        except Exception as e:
            st.error(f"상담 세션 초기화 실패: {e}")
            return
    
    # 메시지 히스토리 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 새 메시지 입력
    if prompt := st.chat_input("질문을 입력하세요..."):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # AI 응답 생성
        with st.chat_message("assistant"):
            try:
                # 상담사와 대화
                response = asyncio.run(chat_with_consultant(
                    prompt, 
                    st.session_state.agent_session, 
                    store_code
                ))
                
                # 응답 표시
                st.markdown(response)
                
                # 메시지 히스토리에 추가
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # 새 분석 시작 버튼
    if st.button("🔄 새 분석 시작"):
        st.session_state.stage = 'input'
        st.session_state.is_analyzing = False
        st.session_state.current_step = 0
        st.session_state.store_code = ''
        st.session_state.analysis_result = None
        st.session_state.md_report = None
        st.session_state.json_data = None
        st.session_state.agent_session = None
        st.session_state.messages = []
        st.rerun()
