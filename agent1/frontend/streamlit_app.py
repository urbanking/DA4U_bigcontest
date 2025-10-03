"""
Streamlit 프론트엔드 애플리케이션
멀티 에이전트 상권 분석 시스템 대시보드
"""

import streamlit as st
import requests
import json
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, Any

# 페이지 설정
st.set_page_config(
    page_title="멀티 에이전트 상권 분석 시스템",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API 설정
API_BASE_URL = "http://localhost:8000"


class StreamlitDashboard:
    """Streamlit 대시보드 클래스"""
    
    def __init__(self):
        """대시보드 초기화"""
        self.api_url = API_BASE_URL
        
    def run(self):
        """메인 대시보드 실행"""
        st.title("🏪 멀티 에이전트 상권 분석 시스템")
        st.markdown("---")
        
        # 사이드바
        self.render_sidebar()
        
        # 메인 컨텐츠
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 실시간 분석", 
            "📈 결과 대시보드", 
            "🧠 메모리 인사이트", 
            "⚙️ 시스템 상태"
        ])
        
        with tab1:
            self.render_analysis_tab()
        
        with tab2:
            self.render_dashboard_tab()
        
        with tab3:
            self.render_memory_tab()
        
        with tab4:
            self.render_system_status_tab()
    
    def render_sidebar(self):
        """사이드바 렌더링"""
        st.sidebar.title("🎛️ 제어판")
        
        # 사용자 정보
        st.sidebar.subheader("👤 사용자 정보")
        user_id = st.sidebar.text_input("사용자 ID", value="USER_001")
        
        # 분석 옵션
        st.sidebar.subheader("🔧 분석 옵션")
        use_memory = st.sidebar.checkbox("메모리 활용", value=True)
        enable_evaluation = st.sidebar.checkbox("평가 시스템 활성화", value=True)
        
        # 세션 관리
        if st.sidebar.button("🔄 새 세션 시작"):
            st.session_state.clear()
            st.success("새 세션이 시작되었습니다!")
        
        return {
            "user_id": user_id,
            "use_memory": use_memory,
            "enable_evaluation": enable_evaluation
        }
    
    def render_analysis_tab(self):
        """분석 탭 렌더링"""
        st.header("📊 실시간 상권 분석")
        
        # 분석 입력
        col1, col2 = st.columns([2, 1])
        
        with col1:
            user_query = st.text_area(
                "분석할 내용을 입력하세요",
                placeholder="예: 왜 20대 고객이 줄어들고 있나요?",
                height=100
            )
        
        with col2:
            st.markdown("### 💡 질문 예시")
            examples = [
                "매출이 감소하는 이유는?",
                "경쟁사와 비교한 우리 강점은?",
                "새로운 메뉴 출시 전략은?",
                "고객 이탈률이 높은 이유는?"
            ]
            
            for example in examples:
                if st.button(example, key=f"example_{example}"):
                    st.session_state.query = example
                    st.rerun()
        
        # 분석 실행
        if st.button("🚀 분석 시작", type="primary"):
            if user_query:
                self.run_analysis(user_query)
            else:
                st.warning("분석할 내용을 입력해주세요!")
    
    def run_analysis(self, query: str):
        """분석 실행"""
        try:
            # 로딩 표시
            with st.spinner("🤖 AI 에이전트들이 분석 중입니다..."):
                # API 호출
                response = requests.post(
                    f"{self.api_url}/analyze",
                    json={
                        "user_query": query,
                        "user_id": st.session_state.get("user_id", "USER_001")
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.analysis_result = result
                    st.success("✅ 분석이 완료되었습니다!")
                    
                    # 결과 표시
                    self.display_analysis_result(result)
                    
                else:
                    st.error(f"❌ 분석 실패: {response.text}")
        
        except requests.exceptions.RequestException as e:
            st.error(f"❌ API 연결 실패: {e}")
        except Exception as e:
            st.error(f"❌ 예상치 못한 에러: {e}")
    
    def display_analysis_result(self, result: Dict[str, Any]):
        """분석 결과 표시"""
        st.markdown("---")
        
        # 요약 정보
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("상태", result.get("status", "Unknown"))
        
        with col2:
            st.metric("진행 단계", result.get("current_step", "Unknown"))
        
        with col3:
            progress = result.get("progress", 0)
            st.metric("진행률", f"{progress:.0f}%")
        
        with col4:
            agent_count = len(result.get("agent_results", {}))
            st.metric("실행된 에이전트", f"{agent_count}개")
        
        # 에이전트 결과
        st.subheader("🤖 에이전트 실행 결과")
        agent_results = result.get("agent_results", {})
        
        for agent_name, agent_result in agent_results.items():
            with st.expander(f"📋 {agent_name}"):
                if agent_result.get("status") == "success":
                    st.success("✅ 성공")
                    results = agent_result.get("results", {})
                    
                    # 주요 결과 표시
                    for key, value in results.items():
                        if isinstance(value, dict):
                            st.json(value)
                        elif isinstance(value, list):
                            st.write(f"**{key}**: {len(value)}개 항목")
                        else:
                            st.write(f"**{key}**: {value}")
                else:
                    st.error("❌ 실패")
                    st.write(agent_result.get("error", "알 수 없는 에러"))
        
        # 평가 점수
        evaluation_scores = result.get("evaluation_scores")
        if evaluation_scores:
            st.subheader("📊 평가 점수")
            
            # 점수 차트
            scores_df = pd.DataFrame([
                {"에이전트": agent, "점수": score}
                for agent, score in evaluation_scores.items()
                if agent != "overall"
            ])
            
            if not scores_df.empty:
                fig = px.bar(
                    scores_df, 
                    x="에이전트", 
                    y="점수",
                    title="에이전트별 평가 점수",
                    color="점수",
                    color_continuous_scale="RdYlGn"
                )
                fig.update_layout(yaxis=dict(range=[0, 1]))
                st.plotly_chart(fig, use_container_width=True)
        
        # 최종 보고서
        final_report = result.get("final_report")
        if final_report:
            st.subheader("📄 최종 상담 보고서")
            
            report_content = final_report.get("results", {}).get("full_report")
            if report_content:
                st.markdown(report_content)
            else:
                st.info("보고서 생성 중...")
    
    def render_dashboard_tab(self):
        """대시보드 탭 렌더링"""
        st.header("📈 분석 결과 대시보드")
        
        # 이전 분석 결과가 있는지 확인
        if "analysis_result" not in st.session_state:
            st.info("먼저 분석을 실행해주세요!")
            return
        
        result = st.session_state.analysis_result
        
        # 시각화 섹션
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 에이전트 성능")
            self.render_agent_performance_chart(result)
        
        with col2:
            st.subheader("📊 분석 품질")
            self.render_quality_metrics(result)
        
        # 상세 분석
        st.subheader("🔍 상세 분석 결과")
        self.render_detailed_analysis(result)
    
    def render_agent_performance_chart(self, result: Dict[str, Any]):
        """에이전트 성능 차트"""
        agent_results = result.get("agent_results", {})
        
        if not agent_results:
            st.info("에이전트 실행 결과가 없습니다.")
            return
        
        # 성공/실패 통계
        success_count = sum(1 for r in agent_results.values() if r.get("status") == "success")
        total_count = len(agent_results)
        
        # 파이 차트
        fig = go.Figure(data=[go.Pie(
            labels=["성공", "실패"],
            values=[success_count, total_count - success_count],
            hole=0.3
        )])
        
        fig.update_layout(title="에이전트 실행 성공률")
        st.plotly_chart(fig, use_container_width=True)
    
    def render_quality_metrics(self, result: Dict[str, Any]):
        """품질 지표 표시"""
        evaluation_scores = result.get("evaluation_scores", {})
        
        if not evaluation_scores:
            st.info("평가 점수가 없습니다.")
            return
        
        # 전체 점수
        overall_score = evaluation_scores.get("overall", 0)
        
        # 게이지 차트
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = overall_score * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "전체 품질 점수"},
            delta = {'reference': 70},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_detailed_analysis(self, result: Dict[str, Any]):
        """상세 분석 결과"""
        agent_results = result.get("agent_results", {})
        
        # 에이전트별 상세 결과 테이블
        if agent_results:
            data = []
            for agent_name, agent_result in agent_results.items():
                data.append({
                    "에이전트": agent_name,
                    "상태": "✅ 성공" if agent_result.get("status") == "success" else "❌ 실패",
                    "결과 개수": len(agent_result.get("results", {})),
                    "에러": agent_result.get("error", "-")
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
    
    def render_memory_tab(self):
        """메모리 탭 렌더링"""
        st.header("🧠 메모리 인사이트")
        
        # 사용자 히스토리
        user_id = st.session_state.get("user_id", "USER_001")
        
        try:
            response = requests.get(f"{self.api_url}/user/{user_id}/history")
            if response.status_code == 200:
                history_data = response.json()
                history = history_data.get("history", [])
                
                if history:
                    st.subheader(f"📚 {user_id}의 분석 히스토리")
                    
                    for i, record in enumerate(history[:10]):  # 최근 10개
                        with st.expander(f"분석 #{i+1} - {record['timestamp'][:19]}"):
                            st.write(f"**질문**: {record['query']}")
                            
                            # 평가 점수
                            scores = record.get("evaluation_scores", {})
                            if scores:
                                st.write("**평가 점수**:")
                                for metric, score in scores.items():
                                    st.metric(metric, f"{score:.2f}")
                else:
                    st.info("아직 분석 히스토리가 없습니다.")
            
            else:
                st.error("히스토리 조회 실패")
        
        except Exception as e:
            st.error(f"히스토리 조회 에러: {e}")
    
    def render_system_status_tab(self):
        """시스템 상태 탭 렌더링"""
        st.header("⚙️ 시스템 상태")
        
        try:
            # 헬스 체크
            response = requests.get(f"{self.api_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                
                st.subheader("🏥 시스템 상태")
                
                components = health_data.get("components", {})
                for component, status in components.items():
                    if status:
                        st.success(f"✅ {component}: 정상")
                    else:
                        st.error(f"❌ {component}: 오류")
                
                # 에이전트 상태
                st.subheader("🤖 에이전트 상태")
                
                agent_response = requests.get(f"{self.api_url}/agents/status")
                if agent_response.status_code == 200:
                    agent_status = agent_response.json()
                    
                    # 워크플로우 에이전트 상태
                    workflow_agents = agent_status.get("workflow_agents", {})
                    if workflow_agents:
                        st.write("**워크플로우 에이전트**:")
                        for agent, status in workflow_agents.items():
                            st.write(f"- {agent}: {status}")
                    
                    # 메모리 시스템 상태
                    memory_status = agent_status.get("memory_status", {})
                    if memory_status:
                        st.write("**메모리 시스템**:")
                        for key, value in memory_status.items():
                            st.write(f"- {key}: {value}")
                
                else:
                    st.error("에이전트 상태 조회 실패")
            
            else:
                st.error("시스템 상태 조회 실패")
        
        except Exception as e:
            st.error(f"시스템 상태 조회 에러: {e}")


def main():
    """메인 함수"""
    dashboard = StreamlitDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
