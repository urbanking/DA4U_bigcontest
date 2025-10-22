"""
분석 결과 표시 컴포넌트
6개 탭으로 분석 결과를 표시합니다.
"""
import streamlit as st
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd

def render_analysis_results():
    """분석 결과를 탭으로 표시합니다."""
    
    # 분석 결과 데이터 확인
    json_data = st.session_state.get('json_data', {})
    result_dir = st.session_state.get('analysis_result', '')
    
    if not json_data and not result_dir:
        st.info("분석 결과가 없습니다. 먼저 분석을 실행해주세요.")
        return
    
    # 결과 디렉토리에서 데이터 로드
    if not json_data and result_dir:
        json_data = load_analysis_data(result_dir)
        if json_data:
            st.session_state.json_data = json_data
    
    if not json_data:
        st.error("분석 데이터를 불러올 수 없습니다.")
        return
    
    # 탭 생성
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 개요", 
        "🏪 Store", 
        "🚶 Mobility", 
        "🌆 Panorama", 
        "🏬 Marketplace", 
        "📈 Marketing"
    ])
    
    with tab1:
        render_overview_tab(json_data)
    
    with tab2:
        render_store_tab(json_data, result_dir)
    
    with tab3:
        render_mobility_tab(json_data, result_dir)
    
    with tab4:
        render_panorama_tab(json_data, result_dir)
    
    with tab5:
        render_marketplace_tab(json_data, result_dir)
    
    with tab6:
        render_marketing_tab(json_data, result_dir)

def render_overview_tab(data: Dict[str, Any]):
    """개요 탭을 렌더링합니다."""
    st.markdown("## 📊 분석 개요")
    
    # 기본 정보
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "상점 코드",
            data.get("metadata", {}).get("store_code", "N/A")
        )
    
    with col2:
        st.metric(
            "분석 일시",
            data.get("metadata", {}).get("analysis_timestamp", "N/A")
        )
    
    with col3:
        quality_score = data.get("store_summary", {}).get("quality_score", 0)
        st.metric(
            "품질 점수",
            f"{quality_score:.2f}" if quality_score else "N/A"
        )
    
    # 공간 분석 요약
    st.markdown("### 🗺️ 위치 정보")
    spatial = data.get("spatial_analysis", {})
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**주소**: {spatial.get('address', 'N/A')}")
        st.info(f"**행정동**: {spatial.get('administrative_dong', 'N/A')}")
    
    with col2:
        marketplace = spatial.get('marketplace', {})
        st.info(f"**상권**: {marketplace.get('상권명', 'N/A')}")
        st.info(f"**좌표**: {spatial.get('coordinates', 'N/A')}")
    
    # 매장 요약
    st.markdown("### 🏪 매장 정보")
    store = data.get("store_summary", {})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success(f"**매장명**: {store.get('store_name', 'N/A')}")
    with col2:
        st.success(f"**업종**: {store.get('industry', 'N/A')}")
    with col3:
        st.success(f"**상권**: {store.get('commercial_area', 'N/A')}")

def render_store_tab(data: Dict[str, Any], result_dir: str):
    """Store 분석 탭을 렌더링합니다."""
    st.markdown("## 🏪 Store 분석")
    
    # Store 차트 표시
    if result_dir:
        store_charts = load_visualization_files(result_dir, "store")
        if store_charts:
            st.markdown("### 📊 Store 분석 차트")
            cols = st.columns(2)
            
            for i, chart_path in enumerate(store_charts[:6]):
                col_idx = i % 2
                with cols[col_idx]:
                    if Path(chart_path).exists():
                        st.image(chart_path, caption=f"Store Chart {i+1}", use_column_width=True)
    
    # Store 데이터 표시
    st.markdown("### 📈 Store 메트릭")
    
    # JSON 데이터에서 Store 관련 정보 추출
    store_data = data.get("store_summary", {})
    
    if store_data:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("매장명", store_data.get("store_name", "N/A"))
            st.metric("업종", store_data.get("industry", "N/A"))
        
        with col2:
            st.metric("상권", store_data.get("commercial_area", "N/A"))
            st.metric("품질 점수", f"{store_data.get('quality_score', 0):.2f}")
        
        with col3:
            st.metric("분석 상태", "완료")
    
    else:
        st.info("Store 분석 데이터가 없습니다.")

def render_mobility_tab(data: Dict[str, Any], result_dir: str):
    """Mobility 분석 탭을 렌더링합니다."""
    st.markdown("## 🚶 Mobility 분석")
    
    # Mobility 차트 표시
    if result_dir:
        mobility_charts = load_visualization_files(result_dir, "mobility")
        if mobility_charts:
            st.markdown("### 📊 Mobility 분석 차트")
            cols = st.columns(2)
            
            for i, chart_path in enumerate(mobility_charts[:6]):
                col_idx = i % 2
                with cols[col_idx]:
                    if Path(chart_path).exists():
                        st.image(chart_path, caption=f"Mobility Chart {i+1}", use_column_width=True)
    
    # Mobility 데이터 표시
    mobility_data = data.get("mobility_summary", {})
    
    if mobility_data:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("분석 기간", mobility_data.get("analysis_period", "N/A"))
        
        with col2:
            st.metric("생성된 차트", f"{mobility_data.get('total_charts', 0)}개")
    
    else:
        st.info("Mobility 분석 데이터가 없습니다.")

def render_panorama_tab(data: Dict[str, Any], result_dir: str):
    """Panorama 분석 탭을 렌더링합니다."""
    st.markdown("## 🌆 Panorama 분석")
    
    # Panorama 이미지 표시
    if result_dir:
        panorama_images = load_visualization_files(result_dir, "panorama")
        if panorama_images:
            st.markdown("### 📸 Panorama 이미지")
            cols = st.columns(2)
            
            for i, img_path in enumerate(panorama_images[:4]):
                col_idx = i % 2
                with cols[col_idx]:
                    if Path(img_path).exists():
                        st.image(img_path, caption=f"Panorama Image {i+1}", use_column_width=True)
    
    # Panorama 데이터 표시
    panorama_data = data.get("panorama_summary", {})
    
    if panorama_data:
        st.markdown("### 📊 Panorama 분석 결과")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**지역 특성**: {panorama_data.get('area_characteristics', 'N/A')}")
            st.info(f"**상권 유형**: {panorama_data.get('marketplace_type', 'N/A')}")
        
        with col2:
            scores = panorama_data.get('scores', {})
            if scores:
                st.metric("종합 점수", f"{scores.get('overall', 'N/A')}")
        
        # 강점과 약점
        strengths = panorama_data.get('strengths', [])
        weaknesses = panorama_data.get('weaknesses', [])
        
        if strengths:
            st.markdown("#### ✅ 강점")
            for strength in strengths:
                st.success(f"• {strength}")
        
        if weaknesses:
            st.markdown("#### ⚠️ 약점")
            for weakness in weaknesses:
                st.warning(f"• {weakness}")
    
    else:
        st.info("Panorama 분석 데이터가 없습니다.")

def render_marketplace_tab(data: Dict[str, Any], result_dir: str):
    """Marketplace 분석 탭을 렌더링합니다."""
    st.markdown("## 🏬 Marketplace 분석")
    
    # Marketplace 데이터 표시
    marketplace_data = data.get("marketplace_summary", {})
    
    if marketplace_data:
        st.markdown("### 📊 상권 정보")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("상권명", marketplace_data.get("marketplace_name", "N/A"))
        
        with col2:
            st.metric("점포 수", f"{marketplace_data.get('store_count', 0)}개")
        
        with col3:
            sales_volume = marketplace_data.get("sales_volume", "N/A")
            st.metric("매출액", sales_volume)
    
    else:
        st.info("Marketplace 분석 데이터가 없습니다.")

def render_marketing_tab(data: Dict[str, Any], result_dir: str):
    """Marketing 분석 탭을 렌더링합니다."""
    st.markdown("## 📈 Marketing 분석")
    
    # Marketing 데이터 표시
    marketing_data = data.get("marketing_summary", {})
    
    if marketing_data:
        st.markdown("### 📊 마케팅 전략")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("페르소나 유형", marketing_data.get("persona_type", "N/A"))
        
        with col2:
            st.metric("위험 수준", marketing_data.get("risk_level", "N/A"))
        
        with col3:
            st.metric("전략 수", f"{marketing_data.get('strategy_count', 0)}개")
        
        with col4:
            st.metric("캠페인 수", f"{marketing_data.get('campaign_count', 0)}개")
    
    else:
        st.info("Marketing 분석 데이터가 없습니다.")

def load_analysis_data(result_dir: str) -> Optional[Dict[str, Any]]:
    """분석 결과 디렉토리에서 데이터를 로드합니다."""
    try:
        result_path = Path(result_dir)
        comprehensive_file = result_path / "comprehensive_analysis.json"
        
        if comprehensive_file.exists():
            with open(comprehensive_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
        
    except Exception as e:
        print(f"[ERROR] 분석 데이터 로드 실패: {e}")
        return None

def load_visualization_files(result_dir: str, analysis_type: str) -> List[str]:
    """시각화 파일들을 로드합니다."""
    try:
        result_path = Path(result_dir)
        files = []
        
        # 분석 유형별 파일 패턴
        patterns = {
            "store": ["*store*.png", "*chart*.png"],
            "mobility": ["*mobility*.png", "*movement*.png"],
            "panorama": ["*.jpg", "*.png"],
            "marketplace": ["*marketplace*.png"],
            "marketing": ["*marketing*.png"]
        }
        
        if analysis_type in patterns:
            for pattern in patterns[analysis_type]:
                files.extend(result_path.glob(pattern))
        
        return [str(f) for f in files if f.exists()]
        
    except Exception as e:
        print(f"[ERROR] 시각화 파일 로드 실패: {e}")
        return []
