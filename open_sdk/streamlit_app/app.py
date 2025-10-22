"""
BigContest AI Agent - 1:1 비밀 상담 서비스
Langchain + Gemini 버전 (OpenAI Agents SDK 제거)
"""
import streamlit as st
from pathlib import Path
import json
import asyncio
import os
import sys
import time
from datetime import datetime
import platform
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# matplotlib import 및 설정 (완전 안전 모드)
MATPLOTLIB_AVAILABLE = False
plt = None
matplotlib = None

# matplotlib을 완전히 선택적으로 로드
def safe_import_matplotlib():
    global MATPLOTLIB_AVAILABLE, plt, matplotlib
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        
        # 한글 폰트 설정
        system = platform.system()
        if system == "Windows":
            plt.rcParams['font.family'] = 'Malgun Gothic'
        elif system == "Darwin":
            plt.rcParams['font.family'] = 'AppleGothic'
        else:
            plt.rcParams['font.family'] = 'NanumGothic'
        matplotlib.rcParams['axes.unicode_minus'] = False
        
        MATPLOTLIB_AVAILABLE = True
        print("[OK] Matplotlib loaded successfully")
        return True
    except ImportError as e:
        print(f"[WARN] Matplotlib not available: {e}")
        return False
    except Exception as e:
        print(f"[WARN] Matplotlib configuration error: {e}")
        return False

# matplotlib 로드 시도 (실제 사용 시점에 로드)
# safe_import_matplotlib()

# run_analysis.py 직접 import
sys.path.insert(0, str(Path(__file__).parent.parent))  # open_sdk 디렉토리 추가
from run_analysis import run_full_analysis_pipeline

# Langchain AI Agents import
AGENTS_AVAILABLE = False
try:
    from ai_agents import (
        classify_query_sync,
        create_consultation_chain,
        chat_with_consultant,
        load_merged_analysis
    )
    AGENTS_AVAILABLE = True
    print("[OK] Langchain AI Agents loaded successfully")
except ImportError as e:
    print(f"[WARN] AI Agents import failed: {e}")
except Exception as e:
    print(f"[ERROR] AI Agents error: {e}")
    import traceback
    traceback.print_exc()

# Gemini 클라이언트 import
try:
    import importlib.util
    gemini_path = Path(__file__).parent.parent.parent / "agents_new" / "utils" / "gemini_client.py"
    spec = importlib.util.spec_from_file_location("gemini_client", gemini_path)
    gemini_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gemini_module)
    GeminiClient = gemini_module.GeminiClient
    GEMINI_AVAILABLE = True
except Exception as e:
    GEMINI_AVAILABLE = False
    print(f"Gemini client not available: {e}")

# 페이지 설정
st.set_page_config(
    page_title="BigContest AI Agent - 1:1 비밀 상담 서비스",
    page_icon="🏪",
    layout="wide"
)

# 커스텀 CSS (한글 폰트 적용)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        
        * {
            font-family: 'Noto Sans KR', 'Malgun Gothic', 'AppleGothic', sans-serif !important;
        }
        
        .stMarkdown, .stText, .stSelectbox, .stTextInput, .stButton, .stMetric, .stExpander {
            font-family: 'Noto Sans KR', 'Malgun Gothic', 'AppleGothic', sans-serif !important;
        }
        
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            font-family: 'Noto Sans KR', 'Malgun Gothic', 'AppleGothic', sans-serif !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            font-family: 'Noto Sans KR', 'Malgun Gothic', 'AppleGothic', sans-serif !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-family: 'Noto Sans KR', 'Malgun Gothic', 'AppleGothic', sans-serif !important;
        }
        
        .stSelectbox label, .stTextInput label {
            font-family: 'Noto Sans KR', 'Malgun Gothic', 'AppleGothic', sans-serif !important;
        }
        
        .stButton > button {
            font-family: 'Noto Sans KR', 'Malgun Gothic', 'AppleGothic', sans-serif !important;
        }
        
        .stMetric [data-testid="metric-container"] {
            font-family: 'Noto Sans KR', 'Malgun Gothic', 'AppleGothic', sans-serif !important;
        }
        
        .stExpander [data-testid="stExpander"] {
            font-family: 'Noto Sans KR', 'Malgun Gothic', 'AppleGothic', sans-serif !important;
        }
    </style>
    """, unsafe_allow_html=True)

# 세션 상태 초기화
if 'store_code' not in st.session_state:
    st.session_state.store_code = None
if 'is_analyzing' not in st.session_state:
    st.session_state.is_analyzing = False
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'consultation_mode' not in st.session_state:
    st.session_state.consultation_mode = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None
if 'final_report_generated' not in st.session_state:
    st.session_state.final_report_generated = False
if 'consultation_chain' not in st.session_state:
    st.session_state.consultation_chain = None
if 'consultation_memory' not in st.session_state:
    st.session_state.consultation_memory = None
if 'merged_data' not in st.session_state:
    st.session_state.merged_data = None
if 'merged_md' not in st.session_state:
    st.session_state.merged_md = None

def generate_final_report_with_gemini(analysis_data):
    """Gemini를 사용해서 최종 리포트 생성"""
    if not GEMINI_AVAILABLE:
        return None, None
    
    try:
        client = GeminiClient()
        
        # 분석 데이터를 JSON 문자열로 변환
        analysis_json = json.dumps(analysis_data, ensure_ascii=False, indent=2)
        
        prompt = f"""
다음은 매장 분석 결과입니다. 이 데이터를 바탕으로 전문적이고 실행 가능한 최종 리포트를 작성해주세요.

분석 데이터:
{analysis_json}

다음 형식으로 답변해주세요:

# 매장 분석 최종 리포트

## 1. 실행 요약
- 핵심 인사이트 3가지
- 주요 문제점 2가지  
- 추천 전략 3가지

## 2. 매장 현황 분석
- 매장 기본 정보
- 매출 및 고객 분석
- 상권 환경 분석

## 3. 마케팅 전략
- 타겟 고객 분석
- 추천 마케팅 전략
- 실행 계획

## 4. 개선 방안
- 즉시 실행 가능한 개선사항
- 중장기 발전 방향
- 위험 요소 및 대응 방안

## 5. 결론 및 권고사항
- 종합 평가
- 최우선 실행 과제
- 성공 지표 설정

JSON 형식으로도 요약해주세요:
{{
  "executive_summary": {{
    "key_insights": ["인사이트1", "인사이트2", "인사이트3"],
    "main_issues": ["문제1", "문제2"],
    "recommended_strategies": ["전략1", "전략2", "전략3"]
  }},
  "store_analysis": {{
    "performance_score": 85,
    "strengths": ["강점1", "강점2"],
    "weaknesses": ["약점1", "약점2"]
  }},
  "marketing_recommendations": {{
    "target_customers": "타겟 고객 설명",
    "primary_strategy": "주요 전략",
    "implementation_priority": "높음/중간/낮음"
  }},
  "action_plan": {{
    "immediate_actions": ["즉시 실행1", "즉시 실행2"],
    "short_term_goals": ["단기 목표1", "단기 목표2"],
    "long_term_vision": "장기 비전"
  }}
}}
"""
        
        response = client.chat_completion([{"role": "user", "content": prompt}])
        
        # MD와 JSON 분리
        md_content = response
        json_content = None
        
        # JSON 부분 추출
        if "```json" in response:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            if json_end > json_start:
                json_str = response[json_start:json_end].strip()
                try:
                    json_content = json.loads(json_str)
                except:
                    json_content = None
        
        return md_content, json_content
        
    except Exception as e:
        print(f"Gemini 리포트 생성 실패: {e}")
        return None, None

def convert_absolute_to_relative_path(absolute_path: str) -> str:
    """절대 경로를 상대 경로로 변환"""
    if not absolute_path:
        return absolute_path
    
    # 프로젝트 루트 기준으로 상대 경로 계산
    project_root = Path(__file__).parent.parent.parent
    
    try:
        abs_path = Path(absolute_path)
        if abs_path.is_absolute():
            # 프로젝트 루트를 기준으로 상대 경로 계산
            relative_path = abs_path.relative_to(project_root)
            return str(relative_path).replace('\\', '/')  # Windows 경로 구분자 통일
        else:
            return absolute_path
    except ValueError:
        # 프로젝트 루트 밖의 경로인 경우 원본 반환
        return absolute_path


def load_analysis_data_from_output(store_code):
    """output 폴더에서 실제 분석 데이터를 로드"""
    try:
        output_dir = Path(__file__).parent.parent / "output"
        print(f"[DEBUG] output_dir: {output_dir}")
        print(f"[DEBUG] output_dir exists: {output_dir.exists()}")
        
        # 가장 최신 분석 폴더 찾기 (analysis_{store_code}_{timestamp} 형식)
        analysis_dirs = list(output_dir.glob(f"analysis_{store_code}_*"))
        print(f"[DEBUG] 찾은 분석 폴더: {analysis_dirs}")
        
        if not analysis_dirs:
            print(f"[ERROR] {store_code}에 대한 분석 폴더를 찾을 수 없습니다")
            return None
        
        # 가장 최신 폴더 선택
        latest_dir = max(analysis_dirs, key=os.path.getctime)
        print(f"[INFO] 기존 분석 데이터 로드: {latest_dir.name}")
        
        # 각 분석 결과 로드
        data = {
            "store_code": store_code,
            "analysis_dir": str(latest_dir),
            "is_existing_analysis": True,  # 기존 분석임을 표시
            "timestamp": latest_dir.name.split("_")[-1]
        }
        
        # 1. 통합 분석 결과 (analysis_result.json)
        analysis_file = latest_dir / "analysis_result.json"
        if analysis_file.exists():
            try:
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    data["analysis_result"] = json.load(f)
                print(f"[OK] analysis_result.json 로드 성공")
            except PermissionError:
                print(f"[WARN] analysis_result.json 권한 오류 - 건너뜀")
            except Exception as e:
                print(f"[WARN] analysis_result.json 로드 실패: {e}")
        
        # 2. 종합 분석 결과 (comprehensive_analysis.json) - 선택적
        comprehensive_file = latest_dir / "comprehensive_analysis.json"
        if comprehensive_file.exists():
            try:
                with open(comprehensive_file, 'r', encoding='utf-8') as f:
                    data["comprehensive_analysis"] = json.load(f)
                print(f"[OK] comprehensive_analysis.json 로드 성공")
            except PermissionError:
                print(f"[WARN] comprehensive_analysis.json 권한 오류 - 건너뜀")
            except Exception as e:
                print(f"[WARN] comprehensive_analysis.json 로드 실패: {e}")
        
        # 3. Store 분석 결과 - 선택적
        store_file = latest_dir / "store_analysis_report.json"
        if store_file.exists():
            try:
                with open(store_file, 'r', encoding='utf-8') as f:
                    data["store_analysis"] = json.load(f)
                print(f"[OK] store_analysis_report.json 로드 성공")
            except PermissionError:
                print(f"[WARN] store_analysis_report.json 권한 오류 - 건너뜀")
            except Exception as e:
                print(f"[WARN] store_analysis_report.json 로드 실패: {e}")
        
        # 4. Marketing 분석 결과 - 선택적
        marketing_file = latest_dir / "marketing_strategy.json"
        if marketing_file.exists():
            try:
                with open(marketing_file, 'r', encoding='utf-8') as f:
                    data["marketing_analysis"] = json.load(f)
                print(f"[OK] marketing_strategy.json 로드 성공")
            except PermissionError:
                print(f"[WARN] marketing_strategy.json 권한 오류 - 건너뜀")
            except Exception as e:
                print(f"[WARN] marketing_strategy.json 로드 실패: {e}")
        
        # 5. Marketplace 분석 결과
        marketplace_file = latest_dir / "marketplace" / "marketplace_data.json"
        if marketplace_file.exists():
            try:
                with open(marketplace_file, 'r', encoding='utf-8') as f:
                    data["marketplace_analysis"] = json.load(f)
                print(f"[OK] marketplace_data.json 로드 성공")
            except PermissionError:
                print(f"[WARN] marketplace_data.json 권한 오류 - 건너뜀")
            except Exception as e:
                print(f"[WARN] marketplace_data.json 로드 실패: {e}")
        
        # 6. Panorama 분석 결과
        panorama_file = latest_dir / "panorama" / "analysis_result.json"
        if panorama_file.exists():
            try:
                with open(panorama_file, 'r', encoding='utf-8') as f:
                    data["panorama_analysis"] = json.load(f)
                print(f"[OK] panorama analysis_result.json 로드 성공")
            except PermissionError:
                print(f"[WARN] panorama analysis_result.json 권한 오류 - 건너뜀")
            except Exception as e:
                print(f"[WARN] panorama analysis_result.json 로드 실패: {e}")
        
        # 7. Mobility 분석 결과 - 선택적
        mobility_file = latest_dir / "mobility_charts" / "mobility_data.json"
        if mobility_file.exists():
            try:
                with open(mobility_file, 'r', encoding='utf-8') as f:
                    data["mobility_analysis"] = json.load(f)
                print(f"[OK] mobility_data.json 로드 성공")
            except PermissionError:
                print(f"[WARN] mobility_data.json 권한 오류 - 건너뜀")
            except Exception as e:
                print(f"[WARN] mobility_data.json 로드 실패: {e}")
        
        # 8. 시각화 파일들 로드
        data["visualizations"] = load_visualization_files(latest_dir)
        
        # 최소한 하나의 분석 데이터라도 있으면 성공으로 간주
        loaded_sections = [k for k, v in data.items() if k not in ["store_code", "analysis_dir", "is_existing_analysis", "timestamp"] and v is not None]
        
        if loaded_sections:
            print(f"[OK] 분석 데이터 로드 완료: {len(loaded_sections)}개 섹션 ({', '.join(loaded_sections)})")
            return data
        else:
            print(f"[ERROR] 로드된 분석 데이터가 없습니다")
            return None
        
    except Exception as e:
        print(f"[ERROR] 분석 데이터 로드 실패: {e}")
        return None

def load_visualization_files(analysis_dir):
    """시각화 파일들을 로드"""
    viz_data = {
        "store_charts": [],
        "mobility_charts": [],
        "panorama_images": [],
        "spatial_files": []
    }
    
    try:
        # Store 차트들
        store_charts_dir = analysis_dir / "store_charts"
        if store_charts_dir.exists():
            for chart_file in store_charts_dir.glob("*.png"):
                viz_data["store_charts"].append({
                    "name": chart_file.stem,
                    "path": convert_absolute_to_relative_path(str(chart_file)),
                    "absolute_path": str(chart_file),
                    "type": "store_chart"
                })
        
        # Mobility 차트들
        mobility_charts_dir = analysis_dir / "mobility_charts"
        if mobility_charts_dir.exists():
            for chart_file in mobility_charts_dir.glob("*.png"):
                viz_data["mobility_charts"].append({
                    "name": chart_file.stem,
                    "path": convert_absolute_to_relative_path(str(chart_file)),
                    "absolute_path": str(chart_file),
                    "type": "mobility_chart"
                })
        
        # Panorama 이미지들
        panorama_images_dir = analysis_dir / "panorama" / "images"
        if panorama_images_dir.exists():
            for img_file in panorama_images_dir.glob("*.jpg"):
                viz_data["panorama_images"].append({
                    "name": img_file.stem,
                    "path": convert_absolute_to_relative_path(str(img_file)),
                    "absolute_path": str(img_file),
                    "type": "panorama_image"
                })
        
        # Spatial 시각화 파일들
        spatial_map = analysis_dir / "spatial_map.html"
        spatial_chart = analysis_dir / "spatial_analysis.png"
        
        if spatial_map.exists():
            viz_data["spatial_files"].append({
                "name": "공간 분석 지도",
                "path": convert_absolute_to_relative_path(str(spatial_map)),
                "absolute_path": str(spatial_map),
                "type": "spatial_map"
            })
        
        if spatial_chart.exists():
            viz_data["spatial_files"].append({
                "name": "공간 분석 차트",
                "path": convert_absolute_to_relative_path(str(spatial_chart)),
                "absolute_path": str(spatial_chart),
                "type": "spatial_chart"
            })
        
        # Panorama 지도
        panorama_map = analysis_dir / "panorama" / "analysis_map.html"
        if panorama_map.exists():
            viz_data["spatial_files"].append({
                "name": "파노라마 분석 지도",
                "path": convert_absolute_to_relative_path(str(panorama_map)),
                "absolute_path": str(panorama_map),
                "type": "panorama_map"
            })
        
        print(f"[OK] 시각화 파일 로드: Store({len(viz_data['store_charts'])}), Mobility({len(viz_data['mobility_charts'])}), Panorama({len(viz_data['panorama_images'])}), Spatial({len(viz_data['spatial_files'])})")
        
    except Exception as e:
        print(f"[ERROR] 시각화 파일 로드 실패: {e}")
    
    return viz_data

def load_analysis_files_from_actual_locations(store_code):
    """실제 저장된 분석 파일들을 로드 (legacy 함수 - 호환성 유지)"""
    return load_analysis_data_from_output(store_code)

# 각 탭별 표시 함수들
def display_basic_info(analysis_data):
    """기본 정보 표시"""
    st.markdown("### 📊 분석 결과 요약")
    
    # Store 분석에서 기본 정보 추출
    store_data = analysis_data.get("store_analysis", {})
    if store_data and "store_overview" in store_data:
        store_info = store_data["store_overview"]
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("매장명", store_info.get("name", "N/A"))
        with col2:
            st.metric("업종", store_info.get("industry", "N/A"))
        with col3:
            st.metric("상권", store_info.get("commercial_area", "N/A"))
    
    # Spatial 분석에서 주소 정보
    comprehensive = analysis_data.get("comprehensive_analysis", {})
    if comprehensive and "spatial_analysis" in comprehensive:
        spatial = comprehensive["spatial_analysis"]
        st.write(f"**주소:** {spatial.get('address', 'N/A')}")
        st.write(f"**행정동:** {spatial.get('administrative_dong', 'N/A')}")

def display_final_report_button(store_code, analysis_data):
    """최종 리포트 생성 버튼 표시"""
    if not st.session_state.final_report_generated:
        if st.button("📋 최종 리포트 생성 (Gemini)", type="primary"):
            with st.spinner("Gemini로 최종 리포트를 생성 중..."):
                md_content, json_content = generate_final_report_with_gemini(analysis_data)
                if md_content:
                    report_dir = save_final_reports(store_code, md_content, json_content)
                    if report_dir:
                        st.success(f"최종 리포트가 생성되었습니다: {report_dir}")
                        st.session_state.final_report_generated = True
                        st.rerun()
                else:
                    st.error("최종 리포트 생성에 실패했습니다.")
    else:
        st.info("✅ 최종 리포트가 이미 생성되었습니다.")

def display_store_overview(analysis_data):
    """매장 개요 탭"""
    st.markdown("### 🏪 매장 개요")
    
    store_data = analysis_data.get("store_analysis", {})
    if not store_data:
        st.info("매장 분석 데이터가 없습니다.")
        return
    
    store_info = store_data.get("store_overview", {})
    sales_data = store_data.get("sales_analysis", {})
    
    # 기본 정보
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**매장명:** {store_info.get('name', 'N/A')}")
        st.write(f"**업종:** {store_info.get('industry', 'N/A')}")
        st.write(f"**브랜드:** {store_info.get('brand', 'N/A')}")
    with col2:
        st.write(f"**상권:** {store_info.get('commercial_area', 'N/A')}")
        st.write(f"**운영 개월:** {store_info.get('operating_months', 'N/A')}개월")
        st.write(f"**매장 연령:** {store_info.get('store_age', 'N/A')}")
    
    # 매출 분석
    if sales_data:
        st.markdown("#### 📈 매출 분석")
        trends = sales_data.get("trends", {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("매출액", trends.get("sales_amount", {}).get("trend", "N/A"))
        with col2:
            st.metric("매출 건수", trends.get("sales_count", {}).get("trend", "N/A"))
        with col3:
            st.metric("고유 고객", trends.get("unique_customers", {}).get("trend", "N/A"))
        with col4:
            st.metric("객단가", trends.get("avg_transaction", {}).get("trend", "N/A"))
        
        # 배달 분석
        delivery = sales_data.get("delivery_analysis", {})
        if delivery:
            st.write(f"**배달 비율:** {delivery.get('average', 'N/A')}% ({delivery.get('trend', 'N/A')})")
        
        # 취소율 분석
        cancellation = sales_data.get("cancellation_analysis", {})
        if cancellation:
            st.write(f"**평균 취소 등급:** {cancellation.get('average_grade', 'N/A')}")
            st.write(f"**권장사항:** {cancellation.get('recommendation', 'N/A')}")

def display_customer_analysis(analysis_data):
    """고객 분석 탭 + 시각화"""
    st.markdown("### 👥 고객 분석")
    
    store_data = analysis_data.get("store_analysis", {})
    if not store_data:
        st.info("매장 분석 데이터가 없습니다.")
        return
    
    customer_data = store_data.get("customer_analysis", {})
    if not customer_data:
        st.info("고객 분석 데이터가 없습니다.")
        return
    
    # 성별 분포
    gender_data = customer_data.get("gender_distribution", {})
    if gender_data:
        st.markdown("#### 성별 분포")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("남성", f"{gender_data.get('male_ratio', 0)}%")
        with col2:
            st.metric("여성", f"{gender_data.get('female_ratio', 0)}%")
    
    # 연령대 분포
    age_data = customer_data.get("age_group_distribution", {})
    if age_data:
        st.markdown("#### 연령대별 고객 분포")
        for age_group, ratio in age_data.items():
            st.write(f"- **{age_group}:** {ratio}%")
    
    # 고객 유형 분석
    customer_type = customer_data.get("customer_type_analysis", {})
    if customer_type:
        st.markdown("#### 고객 유형 분석")
        
        new_customers = customer_type.get("new_customers", {})
        returning_customers = customer_type.get("returning_customers", {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("신규 고객", f"{new_customers.get('ratio', 0)}%", delta=new_customers.get('trend', ''))
        with col2:
            st.metric("재방문 고객", f"{returning_customers.get('ratio', 0)}%", delta=returning_customers.get('trend', ''))
        
        # 고객 분포
        distribution = customer_type.get("customer_distribution", {})
        if distribution:
            st.markdown("#### 고객 분포")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("주거형", f"{distribution.get('residential', 0)}%")
            with col2:
                st.metric("직장형", f"{distribution.get('workplace', 0)}%")
            with col3:
                st.metric("유동형", f"{distribution.get('floating', 0)}%")
    
    # ===== 시각화 추가 =====
    visualizations = analysis_data.get("visualizations", {})
    store_charts = visualizations.get("store_charts", [])
    
    if store_charts:
        st.markdown("---")
        st.markdown("#### 📊 고객 분석 차트")
        
        # 고객 관련 차트 필터링
        customer_charts = [c for c in store_charts if any(keyword in c.get("name", "").lower() 
                          for keyword in ["age", "gender", "customer", "연령", "성별", "고객"])]
        
        if customer_charts:
            cols = st.columns(2)
            for idx, chart_info in enumerate(customer_charts[:6]):  # 최대 6개
                col_idx = idx % 2
                with cols[col_idx]:
                    chart_path = chart_info.get("path")
                    chart_name = chart_info.get("name", f"Chart {idx+1}")
                    
                    if chart_path and Path(chart_path).exists():
                        try:
                            st.image(chart_path, caption=chart_name, use_column_width=True)
                        except Exception as e:
                            st.error(f"차트 로딩 실패: {chart_name}")
        else:
            st.info("고객 관련 차트가 없습니다.")

def display_mobility_analysis(analysis_data):
    """이동 패턴 분석 탭 + 시각화"""
    st.markdown("### 🚶 이동 패턴 분석")
    
    mobility_data = analysis_data.get("mobility_analysis", {})
    if not mobility_data:
        st.info("이동 패턴 분석 데이터가 없습니다.")
        return
    
    analysis = mobility_data.get("analysis", {})
    if not analysis:
        st.info("이동 패턴 분석 결과가 없습니다.")
        return
    
    # 이동 유형
    move_types = analysis.get("part1_move_types", {})
    if move_types:
        st.markdown("#### 이동 유형")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("유입", f"{move_types.get('유입', 0):,}명")
        with col2:
            st.metric("유출", f"{move_types.get('유출', 0):,}명")
        with col3:
            st.metric("내부이동", f"{move_types.get('내부이동', 0):,}명")
    
    # 시간대별 패턴
    time_pattern = analysis.get("part2_time_pattern", {})
    if time_pattern:
        st.markdown("#### 시간대별 이동 패턴")
        peak_hour = max(time_pattern.items(), key=lambda x: x[1])
        st.write(f"**최대 이동 시간:** {peak_hour[0]}시 ({peak_hour[1]:,}명)")
    
    # ===== 시각화 추가 =====
    visualizations = analysis_data.get("visualizations", {})
    mobility_charts = visualizations.get("mobility_charts", [])
    
    if mobility_charts:
        st.markdown("---")
        st.markdown("#### 📊 이동 패턴 차트")
        st.write(f"총 {len(mobility_charts)}개 차트")
        
        cols = st.columns(2)
        for idx, chart_info in enumerate(mobility_charts):
            col_idx = idx % 2
            with cols[col_idx]:
                chart_path = chart_info.get("path")
                chart_name = chart_info.get("name", f"Chart {idx+1}")
                
                if chart_path and Path(chart_path).exists():
                    try:
                        st.image(chart_path, caption=chart_name, use_column_width=True)
                    except Exception as e:
                        st.error(f"차트 로딩 실패: {chart_name}")
    else:
        st.info("이동 패턴 차트가 없습니다.")
        
        # 상위 5개 시간대
        top_hours = sorted(time_pattern.items(), key=lambda x: x[1], reverse=True)[:5]
        st.write("**상위 이동 시간대:**")
        for hour, count in top_hours:
            st.write(f"- {hour}시: {count:,}명")
    
    # 목적별 분석
    purpose_data = analysis.get("part3_purpose", {})
    if purpose_data:
        st.markdown("#### 목적별 이동")
        top_purposes = sorted(purpose_data.items(), key=lambda x: x[1], reverse=True)[:5]
        for purpose, count in top_purposes:
            st.write(f"- **{purpose}:** {count:,}명")
    
    # 교통수단
    transport_data = analysis.get("part4_transport", {})
    if transport_data:
        st.markdown("#### 교통수단별 이용")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**차량:** {transport_data.get('차량', 0):,}명")
            st.write(f"**지하철:** {transport_data.get('지하철', 0):,}명")
        with col2:
            st.write(f"**도보:** {transport_data.get('도보', 0):,}명")
            st.write(f"**버스:** {transport_data.get('일반버스', 0) + transport_data.get('광역버스', 0):,}명")

def display_panorama_analysis(analysis_data):
    """지역 분석 탭"""
    st.markdown("### 🏘️ 지역 분석 (파노라마)")
    
    panorama_data = analysis_data.get("panorama_analysis", {})
    if not panorama_data:
        st.info("파노라마 분석 데이터가 없습니다.")
        return
    
    metadata = panorama_data.get("metadata", {})
    if metadata:
        st.write(f"**분석 주소:** {metadata.get('input_address', 'N/A')}")
        st.write(f"**분석 반경:** {metadata.get('buffer_meters', 'N/A')}m")
        st.write(f"**분석 이미지:** {metadata.get('images_analyzed', 0)}개")
    
    # 종합 분석 결과
    synthesis = panorama_data.get("synthesis", {})
    if synthesis:
        st.markdown("#### 종합 분석 결과")
        
        area_summary = synthesis.get("area_summary", {})
        if area_summary:
            st.write(f"**지역 특성:** {area_summary.get('overall_character', 'N/A')}")
            st.write(f"**상권 유형:** {area_summary.get('primary_commercial_type', 'N/A')}")
        
        scores = synthesis.get("comprehensive_scores", {})
        if scores:
            st.markdown("#### 지역 점수")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("상권 활력", f"{scores.get('commercial_atmosphere', 0)}/10")
                st.metric("거리 분위기", f"{scores.get('street_atmosphere', 0)}/10")
            with col2:
                st.metric("청결도", f"{scores.get('cleanliness', 0)}/10")
                st.metric("유지보수", f"{scores.get('maintenance', 0)}/10")
            with col3:
                st.metric("보행성", f"{scores.get('walkability', 0)}/10")
                st.metric("안전감", f"{scores.get('safety_perception', 0)}/10")
        
        detailed_assessment = synthesis.get("detailed_assessment", {})
        if detailed_assessment:
            strengths = detailed_assessment.get("strengths", [])
            weaknesses = detailed_assessment.get("weaknesses", [])
            
            if strengths:
                st.markdown("#### 강점")
                for strength in strengths:
                    st.write(f"✅ {strength}")
            
            if weaknesses:
                st.markdown("#### 약점")
                for weakness in weaknesses:
                    st.write(f"❌ {weakness}")
            
            expert_opinion = detailed_assessment.get("expert_opinion")
            if expert_opinion:
                st.markdown("#### 전문가 의견")
                st.write(expert_opinion)
    
    # ===== 시각화 추가 =====
    visualizations = analysis_data.get("visualizations", {})
    panorama_images = visualizations.get("panorama_images", [])
    
    if panorama_images:
        st.markdown("---")
        st.markdown("#### 📷 파노라마 이미지")
        cols = st.columns(2)
        for idx, img_info in enumerate(panorama_images[:6]):  # 최대 6개
            col_idx = idx % 2
            with cols[col_idx]:
                img_path = img_info.get("path")
                img_name = img_info.get("name", f"Image {idx+1}")
                
                if img_path and Path(img_path).exists():
                    try:
                        st.image(img_path, caption=img_name, use_column_width=True)
                    except Exception as e:
                        st.error(f"이미지 로딩 실패: {img_name}")
    
    # 공간 분석 지도
    spatial_files = visualizations.get("spatial_files", [])
    if spatial_files:
        st.markdown("---")
        st.markdown("#### 🗺️ 공간 분석")
        for file_info in spatial_files:
            file_path = file_info.get("path")
            file_name = file_info.get("name", "Unknown")
            
            if file_path and Path(file_path).exists():
                if ".png" in str(file_path):
                    try:
                        st.image(file_path, caption=file_name, use_column_width=True)
                    except:
                        pass
                elif ".html" in str(file_path):
                    st.markdown(f"**{file_name}:**")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        st.components.v1.html(html_content, height=600)
                    except Exception as e:
                        st.error(f"지도 로딩 실패: {e}")
                        st.markdown(f"[지도 보기]({file_path})")

def display_marketplace_analysis(analysis_data):
    """상권 분석 탭 - Gemini로 분석 결과 생성"""
    st.markdown("### 🏬 상권 분석")
    
    marketplace_data = analysis_data.get("marketplace_analysis", {})
    if not marketplace_data:
        st.info("상권 분석 데이터가 없습니다.")
        return
    
    # Gemini로 상권 분석 결과 생성
    try:
        if not GEMINI_AVAILABLE:
            st.warning("Gemini 클라이언트를 사용할 수 없습니다.")
            return
        
        client = GeminiClient()
        
        # 상권 데이터를 Gemini에게 전달하여 분석
        prompt = f"""
다음 상권 분석 데이터를 바탕으로 전문적이고 상세한 상권 분석 리포트를 작성해주세요.

상권 데이터:
{json.dumps(marketplace_data, ensure_ascii=False, indent=2)}

다음 형식으로 분석해주세요:

## 🏬 상권 개요
- 상권명과 위치 정보
- 분석 시점과 주요 특징

## 📊 핵심 지표 분석
- 점포수 변화 추이와 의미
- 매출액 변화와 상권 활력도
- 면적 대비 점포 밀도 분석

## 📈 상권 동향 분석
- 전분기/전년 동분기 대비 변화 해석
- 상권 성장성과 안정성 평가
- 경쟁 환경과 시장 포화도

## 💡 상권 전망 및 시사점
- 향후 전망과 기회 요소
- 주의해야 할 리스크 요인
- 상권 내 입지 선택 가이드

각 섹션을 구체적이고 실용적인 내용으로 작성해주세요.
"""
        
        response = client.chat_completion([{"role": "user", "content": prompt}])
        
        # Gemini 응답을 표시
        st.markdown(response)
        
    except Exception as e:
        st.error(f"상권 분석 생성 실패: {e}")
        
        # 백업: 기본 데이터 표시
        st.write(f"**상권명:** {marketplace_data.get('상권명', 'N/A')}")
        st.write(f"**분석일시:** {marketplace_data.get('분석일시', 'N/A')}")
        
        # 데이터 섹션
        data_section = marketplace_data.get("데이터", [])
        if data_section:
            # 종합의견 찾기
            for item in data_section:
                if item.get("유형") == "종합의견":
                    st.markdown("#### 종합의견")
                    
                    # 면적 정보
                    area_info = item.get("면적", {})
                    if area_info:
                        st.write(f"**분석 면적:** {area_info.get('분석', 'N/A')}㎡")
                    
                    # 점포수 정보
                    store_count = item.get("점포수", {})
                    if store_count:
                        current = store_count.get("현재", {})
                        st.write(f"**현재 점포수:** {current.get('값', 'N/A')}개 ({current.get('기준', 'N/A')})")
                        
                        # 변화량
                        quarter_change = store_count.get("전분기대비", {})
                        year_change = store_count.get("전년동분기대비", {})
                        if quarter_change:
                            st.write(f"**전분기 대비:** {quarter_change.get('변화', 'N/A')}개")
                        if year_change:
                            st.write(f"**전년 동분기 대비:** {year_change.get('변화', 'N/A')}개")
                    
                    # 매출액 정보
                    sales_info = item.get("매출액", {})
                    if sales_info:
                        current_sales = sales_info.get("현재", {})
                        st.write(f"**현재 매출액:** {current_sales.get('값', 'N/A')}만원 ({current_sales.get('기준', 'N/A')})")
                        
                        # 변화량
                        quarter_sales = sales_info.get("전분기대비", {})
                        if quarter_sales:
                            st.write(f"**전분기 대비:** {quarter_sales.get('변화', 'N/A')}만원")
                
                break

def display_marketing_analysis(analysis_data):
    """마케팅 분석 탭"""
    st.markdown("### 📈 마케팅 분석")
    
    marketing_data = analysis_data.get("marketing_analysis", {})
    if not marketing_data:
        st.info("마케팅 분석 데이터가 없습니다.")
        return
    
    # 페르소나 분석
    persona_analysis = marketing_data.get("persona_analysis", {})
    if persona_analysis:
        st.markdown("#### 페르소나 분석")
        st.write(f"**페르소나 유형:** {persona_analysis.get('persona_type', 'N/A')}")
        st.write(f"**페르소나 설명:** {persona_analysis.get('persona_description', 'N/A')}")
        
        # 마케팅 톤
        marketing_tone = persona_analysis.get("marketing_tone", "")
        if marketing_tone:
            st.write(f"**마케팅 톤:** {marketing_tone}")
        
        # 핵심 채널
        key_channels = persona_analysis.get("key_channels", [])
        if key_channels:
            st.markdown("#### 핵심 마케팅 채널")
            for i, channel in enumerate(key_channels[:5], 1):
                st.write(f"{i}. {channel}")
    
    # 위험 분석
    risk_analysis = marketing_data.get("risk_analysis", {})
    if risk_analysis:
        st.markdown("#### 위험 분석")
        st.write(f"**전체 위험도:** {risk_analysis.get('overall_risk_level', 'N/A')}")
        
        detected_risks = risk_analysis.get("detected_risks", [])
        if detected_risks:
            st.write("**감지된 위험 요소:**")
            for risk in detected_risks[:3]:  # 상위 3개만 표시
                st.write(f"- **{risk.get('name', 'N/A')}:** {risk.get('description', 'N/A')} (우선순위: {risk.get('priority', 'N/A')})")
    
    # 마케팅 전략
    strategies = marketing_data.get("marketing_strategies", [])
    if strategies:
        st.markdown("#### 📈 마케팅 전략")
        for i, strategy in enumerate(strategies[:6], 1):  # 상위 6개 표시
            with st.expander(f"**{i}. {strategy.get('name', 'N/A')}**", expanded=(i==1)):
                st.markdown(f"**📋 전략 설명:**")
                st.write(strategy.get('description', 'N/A'))
                
                st.markdown(f"**🎯 예상 효과:** {strategy.get('expected_impact', 'N/A')}")
                
                # 전술 상세 표시
                tactics = strategy.get("tactics", [])
                if tactics:
                    st.markdown("**⚡ 주요 전술:**")
                    for tactic in tactics:
                        st.write(f"  • {tactic}")
                
                # 채널 정보
                channel = strategy.get("channel", "N/A")
                if channel != "N/A":
                    st.markdown(f"**📱 마케팅 채널:** {channel}")
                
                # 구현 정보
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("⏱️ 구현 기간", strategy.get('implementation_time', 'N/A'))
                with col2:
                    st.metric("💰 예산", strategy.get('budget_estimate', 'N/A'))
                with col3:
                    st.metric("⭐ 우선순위", f"{strategy.get('priority', 'N/A')}")
                
                # 성공 지표
                success_metrics = strategy.get("success_metrics", [])
                if success_metrics:
                    st.markdown("**📊 성공 지표:**")
                    for metric in success_metrics:
                        st.write(f"  ✓ {metric}")
                
                st.markdown("---")
    
    # 캠페인 계획
    campaign_plan = marketing_data.get("campaign_plan", {})
    if campaign_plan:
        st.markdown("#### 캠페인 계획")
        st.write(f"**캠페인명:** {campaign_plan.get('name', 'N/A')}")
        st.write(f"**기간:** {campaign_plan.get('duration', 'N/A')}")
        
        expected_kpis = campaign_plan.get("expected_kpis", {})
        if expected_kpis:
            st.write("**예상 KPI:**")
            for kpi, value in expected_kpis.items():
                st.write(f"- {kpi}: {value}")

def display_visualizations(analysis_data):
    """시각화 탭"""
    st.markdown("### 📊 시각화")
    
    visualizations = analysis_data.get("visualizations", {})
    if not visualizations:
        st.info("시각화 파일이 없습니다.")
        return
    
    # Store 차트들
    store_charts = visualizations.get("store_charts", [])
    if store_charts:
        st.markdown("#### 🏪 매장 분석 차트")
        cols = st.columns(2)
        for i, chart_info in enumerate(store_charts[:6]):  # 최대 6개 표시
            col_idx = i % 2
            with cols[col_idx]:
                chart_path = chart_info.get("path")
                chart_name = chart_info.get("name", f"Chart {i+1}")
                
                if chart_path and Path(chart_path).exists():
                    try:
                        st.image(chart_path, caption=chart_name, use_column_width=True)
                    except Exception as e:
                        st.error(f"차트 로딩 실패: {chart_name}")
                else:
                    st.write(f"차트 없음: {chart_name}")
    
    # Mobility 차트들
    mobility_charts = visualizations.get("mobility_charts", [])
    if mobility_charts:
        st.markdown("#### 🚶 이동 분석 차트")
        cols = st.columns(2)
        for i, chart_info in enumerate(mobility_charts[:6]):  # 최대 6개 표시
            col_idx = i % 2
            with cols[col_idx]:
                chart_path = chart_info.get("path")
                chart_name = chart_info.get("name", f"Chart {i+1}")
                
                if chart_path and Path(chart_path).exists():
                    try:
                        st.image(chart_path, caption=chart_name, use_column_width=True)
                    except Exception as e:
                        st.error(f"차트 로딩 실패: {chart_name}")
                else:
                    st.write(f"차트 없음: {chart_name}")
    
    # Panorama 이미지들
    panorama_images = visualizations.get("panorama_images", [])
    if panorama_images:
        st.markdown("#### 🏘️ 파노라마 분석 이미지")
        cols = st.columns(2)
        for i, img_info in enumerate(panorama_images[:4]):  # 최대 4개 표시
            col_idx = i % 2
            with cols[col_idx]:
                img_path = img_info.get("path")
                img_name = img_info.get("name", f"Image {i+1}")
                
                if img_path and Path(img_path).exists():
                    try:
                        st.image(img_path, caption=img_name, use_column_width=True)
                    except Exception as e:
                        st.error(f"이미지 로딩 실패: {img_name}")
                else:
                    st.write(f"이미지 없음: {img_name}")
    
    # Spatial 파일들
    spatial_files = visualizations.get("spatial_files", [])
    if spatial_files:
        st.markdown("#### 🗺️ 공간 분석")
        for file_info in spatial_files:
            file_path = file_info.get("path")
            file_name = file_info.get("name", "Unknown")
            file_type = file_info.get("type", "unknown")
            
            if file_path and Path(file_path).exists():
                if file_type == "spatial_chart" or file_type == "panorama_map":
                    try:
                        st.image(file_path, caption=file_name, use_column_width=True)
                    except Exception as e:
                        st.error(f"파일 로딩 실패: {file_name}")
                elif file_type == "spatial_map" or file_type == "panorama_map":
                    st.write(f"**{file_name}:** [지도 파일]({file_path})")
                else:
                    st.write(f"**{file_name}:** {file_path}")
            else:
                st.write(f"파일 없음: {file_name}")
    
    if not store_charts and not mobility_charts and not panorama_images and not spatial_files:
        st.info("표시할 시각화 파일이 없습니다.")

def save_final_reports(store_code, md_content, json_content):
    """최종 리포트 파일 저장"""
    try:
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = output_dir / f"final_reports_{store_code}_{timestamp}"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # MD 파일 저장
        if md_content:
            md_file = report_dir / "final.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"Final MD saved: {md_file}")
        
        # JSON 파일 저장
        if json_content:
            json_file = report_dir / "final.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_content, f, ensure_ascii=False, indent=2)
            print(f"Final JSON saved: {json_file}")
        
        return str(report_dir)
        
    except Exception as e:
        print(f"파일 저장 실패: {e}")
        return None

def merge_all_analysis_files(analysis_data):
    """모든 분석 결과를 하나의 JSON과 MD로 통합 (요약이 아닌 원본 데이터 전부)"""
    try:
        # 통합된 전체 데이터
        merged_data = {
            "store_code": analysis_data.get("store_code", "N/A"),
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_directory": analysis_data.get("analysis_dir", "N/A"),
            "store_analysis": analysis_data.get("store_analysis", {}),
            "marketing_analysis": analysis_data.get("marketing_analysis", {}),
            "marketplace_analysis": analysis_data.get("marketplace_analysis", {}),
            "panorama_analysis": analysis_data.get("panorama_analysis", {}),
            "mobility_analysis": analysis_data.get("mobility_analysis", {}),
            "comprehensive_analysis": analysis_data.get("comprehensive_analysis", {}),
            "visualizations": analysis_data.get("visualizations", {})
        }
        
        # 분석 디렉토리에 통합 파일 저장
        if "analysis_dir" in analysis_data:
            analysis_dir = Path(analysis_data["analysis_dir"])
            
            # JSON 파일 저장
            merged_json_file = analysis_dir / "merged_analysis_full.json"
            with open(merged_json_file, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)
            
            print(f"[OK] 통합 JSON 파일 저장: {merged_json_file}")
            print(f"[OK] 통합 데이터 크기: {len(json.dumps(merged_data))} bytes")
            
            # MD 파일 생성
            merged_md_file = analysis_dir / "merged_analysis_full.md"
            md_content = generate_comprehensive_markdown(merged_data)
            
            with open(merged_md_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            print(f"[OK] 통합 MD 파일 저장: {merged_md_file}")
            
            return str(merged_json_file), str(merged_md_file)
        
        return None, None
        
    except Exception as e:
        print(f"[ERROR] 통합 파일 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def generate_comprehensive_markdown(merged_data):
    """통합 분석 데이터를 마크다운으로 변환"""
    store_code = merged_data.get("store_code", "N/A")
    timestamp = merged_data.get("analysis_timestamp", "N/A")
    
    md = f"""# 매장 종합 분석 리포트 (전체)

## 기본 정보
- 상점 코드: {store_code}
- 분석 일시: {timestamp}
- 분석 디렉토리: {merged_data.get('analysis_directory', 'N/A')}

---

"""
    
    # 1. Store 분석
    store_analysis = merged_data.get("store_analysis", {})
    if store_analysis:
        md += f"""## 1. 매장 분석 (Store Analysis)

### 기본 정보
"""
        store_summary = store_analysis.get("store_summary", {})
        if store_summary:
            md += f"""- 매장명: {store_summary.get('store_name', 'N/A')}
- 업종: {store_summary.get('industry', 'N/A')}
- 상권: {store_summary.get('commercial_area', 'N/A')}
- 품질 점수: {store_summary.get('quality_score', 'N/A')}
- 주요 고객층: {store_summary.get('main_customer', 'N/A')}
- 고객 유형: {store_summary.get('customer_type', 'N/A')}

"""
    
    # 2. Marketing 분석
    marketing_analysis = merged_data.get("marketing_analysis", {})
    if marketing_analysis:
        md += f"""## 2. 마케팅 분석 (Marketing Analysis)

### 페르소나 정보
- 페르소나 타입: {marketing_analysis.get('persona_type', 'N/A')}
- 리스크 레벨: {marketing_analysis.get('risk_level', 'N/A')}

### 마케팅 전략
"""
        strategies = marketing_analysis.get("strategies", [])
        for i, strategy in enumerate(strategies, 1):
            md += f"""
#### 전략 {i}: {strategy.get('title', 'N/A')}
- 설명: {strategy.get('description', 'N/A')}
- 타겟: {strategy.get('target', 'N/A')}
- 예상 효과: {strategy.get('expected_impact', 'N/A')}
"""
        
        md += "\n### 마케팅 캠페인\n"
        campaigns = marketing_analysis.get("campaigns", [])
        for i, campaign in enumerate(campaigns, 1):
            md += f"""
#### 캠페인 {i}: {campaign.get('name', 'N/A')}
- 설명: {campaign.get('description', 'N/A')}
- 채널: {campaign.get('channels', 'N/A')}
- 예산: {campaign.get('budget', 'N/A')}
"""
    
    # 3. Marketplace 분석
    marketplace_analysis = merged_data.get("marketplace_analysis", {})
    if marketplace_analysis:
        md += f"""## 3. 상권 분석 (Marketplace Analysis)

### 기본 정보
- 상권명: {marketplace_analysis.get('상권명', 'N/A')}
- 분석일시: {marketplace_analysis.get('분석일시', 'N/A')}

### 상권 데이터
"""
        data_section = marketplace_analysis.get("데이터", [])
        for item in data_section:
            if item.get("유형") == "종합의견":
                area_info = item.get("면적", {})
                if area_info:
                    md += f"- 분석 면적: {area_info.get('분석', 'N/A')}㎡\n"
                
                store_count = item.get("점포수", {})
                if store_count:
                    current = store_count.get("현재", {})
                    md += f"- 현재 점포수: {current.get('값', 'N/A')}개 ({current.get('기준', 'N/A')})\n"
                    
                    quarter_change = store_count.get("전분기대비", {})
                    if quarter_change:
                        md += f"- 전분기 대비: {quarter_change.get('변화', 'N/A')}개\n"
                    
                    year_change = store_count.get("전년동분기대비", {})
                    if year_change:
                        md += f"- 전년 동분기 대비: {year_change.get('변화', 'N/A')}개\n"
                
                sales_info = item.get("매출액", {})
                if sales_info:
                    current_sales = sales_info.get("현재", {})
                    md += f"- 현재 매출액: {current_sales.get('값', 'N/A')}만원 ({current_sales.get('기준', 'N/A')})\n"
                    
                    quarter_sales = sales_info.get("전분기대비", {})
                    if quarter_sales:
                        md += f"- 전분기 대비: {quarter_sales.get('변화', 'N/A')}만원\n"
                
                break
    
    # 4. Panorama 분석
    panorama_analysis = merged_data.get("panorama_analysis", {})
    if panorama_analysis:
        md += f"""
## 4. 파노라마 분석 (Panorama Analysis)

### 위치 정보
- 주소: {panorama_analysis.get('address', 'N/A')}
- 좌표: {panorama_analysis.get('coordinates', 'N/A')}
- 행정동: {panorama_analysis.get('administrative_dong', 'N/A')}
- 상권: {panorama_analysis.get('marketplace', 'N/A')}

"""
    
    # 5. Mobility 분석
    mobility_analysis = merged_data.get("mobility_analysis", {})
    if mobility_analysis:
        md += f"""## 5. 이동 패턴 분석 (Mobility Analysis)

### 이동 데이터
- 데이터 포함: {len(mobility_analysis)} 항목

"""
    
    # 6. Comprehensive 분석
    comprehensive_analysis = merged_data.get("comprehensive_analysis", {})
    if comprehensive_analysis:
        md += f"""## 6. 종합 분석 (Comprehensive Analysis)

{json.dumps(comprehensive_analysis, ensure_ascii=False, indent=2)}

"""
    
    # 7. 시각화 정보
    visualizations = merged_data.get("visualizations", {})
    if visualizations:
        md += f"""## 7. 시각화 파일 목록

"""
        for viz_type, files in visualizations.items():
            md += f"### {viz_type}\n"
            for file_info in files:
                md += f"- {file_info.get('name', 'N/A')}: {file_info.get('path', 'N/A')}\n"
    
    md += f"""
---

## 분석 완료
이 리포트는 모든 분석 결과를 통합한 전체 데이터를 포함하고 있습니다.
상담 모드에서 이 데이터를 바탕으로 질문하실 수 있습니다.
"""
    
    return md

# 메인 2패널 레이아웃
col1, col2 = st.columns([1, 1])

# 왼쪽 패널: 채팅 인터페이스
with col1:
    st.markdown("## BigContest AI Agent - 1:1 비밀 상담 서비스")
    
    # 초기 환영 메시지
    if not st.session_state.messages:
        st.session_state.messages = [{
            "role": "assistant", 
            "content": "안녕하세요! 비밀 상담사 AI 시스템입니다. 10자리 상점 코드를 입력해주시면 종합 분석을 시작하겠습니다. (예: 000F03E44A, 002816BA73)"
        }]
    
    # 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # 분석 중일 때 로딩 표시
    if st.session_state.is_analyzing:
        with st.chat_message("assistant"):
            st.markdown("🔄 5차원 종합 분석을 진행하겠습니다. 약 3-5분 정도 소요됩니다.")
    
    # 사용자 입력
    if prompt := st.chat_input("질문을 입력하세요..."):
        # Query Classifier로 의도 파악
        if AGENTS_AVAILABLE:
            query_result = classify_query_sync(prompt)
            intent = query_result.get("intent", "general_consultation")
            detected_store_code = query_result.get("store_code")
            
            # 1. 상점 코드 쿼리
            if intent == "store_code_query" and detected_store_code and not st.session_state.analysis_complete:
                store_code = detected_store_code
                st.session_state.store_code = store_code
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # 기존 분석 결과 확인
                print(f"[DEBUG] 상점 코드 {store_code}에 대한 기존 분석 결과 확인 중...")
                existing_analysis = load_analysis_data_from_output(store_code)
                print(f"[DEBUG] 기존 분석 결과: {existing_analysis is not None}")
                
                if existing_analysis:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"✅ 상점 코드 {store_code}의 기존 분석 결과를 발견했습니다! 바로 표시하겠습니다."
                    })
                    st.session_state.analysis_data = existing_analysis
                    st.session_state.analysis_complete = True
                    st.session_state.is_analyzing = False
                    
                    # 기존 분석도 통합 파일 생성 (JSON + MD)
                    merged_json, merged_md = merge_all_analysis_files(existing_analysis)
                    if merged_json and merged_md:
                        print(f"[OK] 기존 분석 통합 파일 생성됨: JSON={merged_json}, MD={merged_md}")
                    
                    st.rerun()
                else:
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": "분석을 시작합니다... 5차원 종합 분석을 진행하겠습니다. 약 3-5분 정도 소요됩니다."
                    })
                    st.session_state.is_analyzing = True
                    st.rerun()
            
            # 2. 재시작 요청
            elif intent == "restart_analysis":
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "새로운 분석을 시작하시겠습니까? 10자리 상점 코드를 입력해주세요."
                })
                # 상태 초기화
                st.session_state.analysis_complete = False
                st.session_state.consultation_mode = False
                st.session_state.consultation_chain = None
                st.session_state.consultation_memory = None
                st.rerun()
            
            # 3. 일반 상담 (Consultation 모드)
            elif st.session_state.consultation_mode and st.session_state.consultation_chain:
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                with st.spinner("상담사가 답변을 준비중입니다..."):
                    try:
                        response = chat_with_consultant(
                            st.session_state.consultation_chain,
                            st.session_state.consultation_memory,
                            prompt
                        )
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"죄송합니다. 오류가 발생했습니다: {str(e)}"
                        })
                st.rerun()
            
            # 4. 분석 완료 후 상담 시작 유도
            elif st.session_state.analysis_complete:
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "상담 모드를 시작하려면 아래 '💬 상담 시작' 버튼을 눌러주세요. AI 상담사가 분석 결과를 바탕으로 질문에 답변해드립니다."
                })
                st.rerun()
            
            # 5. 기본 (상점 코드 입력 유도)
            else:
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "10자리 상점 코드를 입력해주세요. (예: 000F03E44A, 002816BA73)"
                })
                st.rerun()
        
        else:
            # Agents 미사용 시 간단한 정규식 매칭
            import re
            store_code_match = re.search(r'[A-Z0-9]{10}', prompt)
            
            if store_code_match and not st.session_state.analysis_complete:
                store_code = store_code_match.group()
                st.session_state.store_code = store_code
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                existing_analysis = load_analysis_data_from_output(store_code)
                
                if existing_analysis:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"✅ 상점 코드 {store_code}의 기존 분석 결과를 발견했습니다!"
                    })
                    st.session_state.analysis_data = existing_analysis
                    st.session_state.analysis_complete = True
                    st.session_state.is_analyzing = False
                    st.rerun()
                else:
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": "분석을 시작합니다..."
                    })
                    st.session_state.is_analyzing = True
                    st.rerun()
            else:
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "10자리 상점 코드를 입력해주세요. (예: 000F03E44A)"
                })
                st.rerun()

# 오른쪽 패널: 분석 결과 대시보드
with col2:
    st.markdown("## 분석 결과")
    
    # 분석 진행 중
    if st.session_state.is_analyzing and not st.session_state.analysis_complete:
        st.info("🔄 분석 진행 중...")
        
        # 실제 분석 실행
        try:
            result = asyncio.run(run_full_analysis_pipeline(st.session_state.store_code))
            
            if result and result.get("status") == "success":
                st.session_state.is_analyzing = False
                st.session_state.analysis_complete = True
                st.session_state.analysis_data = result
                
                # 모든 분석 결과를 하나의 파일로 통합 (JSON + MD)
                merged_json, merged_md = merge_all_analysis_files(result)
                if merged_json and merged_md:
                    print(f"[OK] 통합 분석 파일 생성됨: JSON={merged_json}, MD={merged_md}")
                
                # 완료 메시지 추가
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "분석 완료! 우측 패널에서 상세 분석 결과를 확인하실 수 있습니다. 궁금하신 점이 있으시면 언제든 질문해주세요!"
                })
                
                # 최종 리포트 생성 버튼 표시
                if st.button("📋 최종 리포트 생성 (Gemini)", type="primary"):
                    with st.spinner("Gemini로 최종 리포트를 생성 중..."):
                        md_content, json_content = generate_final_report_with_gemini(result)
                        if md_content:
                            report_dir = save_final_reports(st.session_state.store_code, md_content, json_content)
                            if report_dir:
                                st.success(f"최종 리포트가 생성되었습니다: {report_dir}")
                                st.session_state.final_report_generated = True
                                st.rerun()
                        else:
                            st.error("최종 리포트 생성에 실패했습니다.")
                
                st.rerun()
            else:
                st.error("분석 실패")
                st.session_state.is_analyzing = False
                st.rerun()
                
        except Exception as e:
            st.error(f"분석 실패: {str(e)}")
            st.session_state.is_analyzing = False
            st.rerun()
    
    # 분석 완료 후 결과 표시
    elif st.session_state.analysis_complete and st.session_state.analysis_data:
        # 실제 output 폴더에서 데이터 로드
        store_code = st.session_state.store_code
        analysis_data = load_analysis_data_from_output(store_code)
        
        if not analysis_data:
            st.error("분석 데이터를 로드할 수 없습니다.")
        else:
            st.success(f"✅ 분석 완료! ({analysis_data['timestamp']})")
            
            # 기본 정보 표시
            display_basic_info(analysis_data)
            
            # 최종 리포트 생성 버튼
            display_final_report_button(store_code, analysis_data)
            
            # 상담 시작 버튼
            st.markdown("---")
            if not st.session_state.consultation_mode:
                if st.button("💬 상담 시작", type="primary", use_container_width=True):
                    if AGENTS_AVAILABLE:
                        with st.spinner("상담 시스템을 준비중입니다..."):
                            try:
                                # 통합 분석 파일 로드
                                merged_data, merged_md = load_merged_analysis(analysis_data["analysis_dir"])
                                
                                if merged_data and merged_md:
                                    print(f"[OK] 통합 파일 로드 완료")
                                    print(f"[DEBUG] Analysis Dir: {analysis_data['analysis_dir']}")
                                    print(f"[DEBUG] MD 파일 크기: {len(merged_md)} bytes")
                                    
                                    # Langchain Consultation Chain 생성
                                    chain, memory = create_consultation_chain(store_code, merged_data, merged_md)
                                    
                                    if chain and memory:
                                        st.session_state.consultation_chain = chain
                                        st.session_state.consultation_memory = memory
                                        st.session_state.merged_data = merged_data
                                        st.session_state.merged_md = merged_md
                                        st.session_state.consultation_mode = True
                                        
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": "상담을 시작합니다! 통합 분석 결과를 바탕으로 무엇이든 물어보세요. 📊"
                                        })
                                        st.success("✅ 상담 모드가 활성화되었습니다!")
                                        st.rerun()
                                    else:
                                        st.error("상담 체인 생성에 실패했습니다.")
                                else:
                                    st.error(f"통합 파일을 찾을 수 없습니다.")
                            except Exception as e:
                                st.error(f"상담 시스템 초기화 실패: {e}")
                                import traceback
                                traceback.print_exc()
                    else:
                        st.warning("AI Agents가 로드되지 않았습니다. 기본 모드로 진행합니다.")
            else:
                st.info("✅ 상담 모드 활성화됨 - 자유롭게 질문하세요!")
            
            # 탭으로 상세 결과 표시
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                "개요", "고객 분석", "이동 패턴", "지역 분석", "상권 분석", "마케팅", "시각화"
            ])
            
            with tab1:
                display_store_overview(analysis_data)
            
            with tab2:
                display_customer_analysis(analysis_data)
            
            with tab3:
                display_mobility_analysis(analysis_data)
            
            with tab4:
                display_panorama_analysis(analysis_data)
            
            with tab5:
                display_marketplace_analysis(analysis_data)
            
            with tab6:
                display_marketing_analysis(analysis_data)
            
            with tab7:
                display_visualizations(analysis_data)
    
    else:
        # 초기 상태
        st.info("👈 왼쪽에서 상점 코드를 입력하세요!")
        
        # 기존 분석 결과가 있는 상점 코드 예시 표시
        st.markdown("### 📊 기존 분석 결과가 있는 상점 코드:")
        st.code("000F03E44A  # 기존 분석 결과 있음")
        st.code("002816BA73  # 기존 분석 결과 있음")
