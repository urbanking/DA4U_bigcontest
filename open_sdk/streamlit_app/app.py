"""

BigContest AI Agent - 1:1 비밀 상담 서비스

Langchain + Gemini 버전 (OpenAI Agents SDK 제거)

"""
# app.py 라인 상단 import 섹션에 추가 (약 400번째 줄 근처)

import streamlit as st  # ✅ 이게 제일 먼저!
# 페이지 설정 (가장 먼저 실행되어야 함)
st.set_page_config(
    page_title="BigContest DA4U AI Agent - 1:1 비밀 상담 서비스",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)
import pandas as pd
from pathlib import Path

import json

import asyncio

import os

import sys

import time

from datetime import datetime

import platform

from dotenv import load_dotenv

import io

import threading

from contextlib import redirect_stdout, redirect_stderr
import logging
from streamlit_autorefresh import st_autorefresh

# 환경 변수 로더 (Streamlit Secrets → 환경 변수 변환)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "utils"))
from env_loader import load_env
load_env()



# 한글 폰트 설정
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns

def set_korean_font():
    """한글 폰트 설정"""
    system = platform.system()
    
    if system == "Windows":
        font_name = "Malgun Gothic"
    elif system == "Darwin":  # macOS
        font_name = "AppleGothic"
    else:  # Linux
        font_name = "DejaVu Sans"
    
    # matplotlib 폰트 설정
    plt.rcParams['font.family'] = font_name
    plt.rcParams['axes.unicode_minus'] = False
    
    # seaborn 폰트 설정
    sns.set_style("whitegrid")
    sns.set_palette("husl")
    
    return font_name

# 폰트 설정 실행
KOREAN_FONT = set_korean_font()

# 차트 폰트 설정 함수
def configure_chart_fonts():
    """차트에서 한글 폰트 설정"""
    # Plotly 폰트 설정
    import plotly.graph_objects as go
    import plotly.express as px
    
    # Plotly 기본 폰트 설정
    go.layout.template = "plotly_white"
    
    # Plotly 폰트 설정을 위한 레이아웃
    plotly_font_config = {
        'family': 'Malgun Gothic, 맑은 고딕, sans-serif',
        'size': 12,
        'color': 'black'
    }
    
    return plotly_font_config

# 차트 폰트 설정 실행
CHART_FONT_CONFIG = configure_chart_fonts()

# Streamlit CSS 설정 (한글 폰트)

# CSS 스타일 추가
st.markdown(f"""
<style>
    /* 한글 폰트 설정 */
    .main .block-container {{
        font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
    }}
    
    .stApp {{
        font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
    }}
    
    .stSelectbox label,
    .stTextInput label,
    .stTextArea label,
    .stNumberInput label,
    .stDateInput label,
    .stTimeInput label,
    .stFileUploader label,
    .stRadio label,
    .stCheckbox label,
    .stSlider label,
    .stMultiSelect label {{
        font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
    }}
    
    /* 차트 제목 및 라벨 폰트 설정 */
    .plotly-graph-div {{
        font-family: 'Malgun Gothic', '맑은 고딕', sans-serif !important;
    }}
    
    /* 테이블 폰트 설정 */
    .dataframe {{
        font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
    }}
    
    /* 메트릭 폰트 설정 */
    .metric-container {{
        font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
    }}
    
    /* 알림 메시지 폰트 설정 */
    .stAlert {{
        font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
    }}
    
    /* 버튼 폰트 설정 */
    .stButton button {{
        font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
    }}
    
    /* 탭 폰트 설정 */
    .stTabs [data-baseweb="tab-list"] {{
        font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
    }}
    
    /* 사이드바 폰트 설정 */
    .css-1d391kg {{
        font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
    }}
</style>
""", unsafe_allow_html=True)


# 개선된 Streamlit 로깅 핸들러

class StreamlitHandler(logging.Handler):

    def emit(self, record):

        log_entry = self.format(record)

        if "log_data" not in st.session_state:

            st.session_state["log_data"] = ""

        st.session_state["log_data"] += log_entry + "\n"

        

        # 로그가 너무 많아지면 최근 1000줄만 유지

        if len(st.session_state["log_data"].split('\n')) > 1000:

            lines = st.session_state["log_data"].split('\n')

            st.session_state["log_data"] = '\n'.join(lines[-1000:])



# 로거 설정

logger = logging.getLogger(__name__)

handler = StreamlitHandler()

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

handler.setFormatter(formatter)

logger.addHandler(handler)

logger.setLevel(logging.INFO)



# 기존 LogCapture 호환성을 위한 래퍼 클래스

class LogCapture:

    def __init__(self):

        self.logs = []

        

    def add_log(self, message, level="INFO"):

        """수동으로 로그 추가"""

        if level == "INFO":

            logger.info(message)

        elif level == "SUCCESS":

            logger.info(f"✅ {message}")

        elif level == "ERROR":

            logger.error(message)

        elif level == "WARN":

            logger.warning(message)

        elif level == "DEBUG":

            logger.debug(message)

        elif level == "OK":

            logger.info(f"✓ {message}")

        else:

            logger.info(f"[{level}] {message}")

        

    def get_logs(self, max_lines=100):

        """최근 로그 반환"""

        if "log_data" in st.session_state:

            lines = st.session_state["log_data"].split('\n')

            return lines[-max_lines:] if lines else []

        return []

        

    def clear_logs(self):

        """로그 초기화"""

        if "log_data" in st.session_state:

            st.session_state["log_data"] = ""



# 전역 로그 캡처 인스턴스

log_capture = LogCapture()



# 누락된 함수들 정의
def convert_store_to_marketing_format(store_analysis):
    """Store 분석 결과를 마케팅 에이전트용 포맷으로 변환"""
    if not store_analysis:
        return None
    
    # 기본 변환 로직
    marketing_format = {
        "store_code": store_analysis.get("store_code", ""),
        "store_overview": store_analysis.get("store_overview", {}),
        "sales_analysis": store_analysis.get("sales_analysis", {}),
        "customer_analysis": store_analysis.get("customer_analysis", {}),
        "analysis_timestamp": datetime.now().isoformat()
    }
    
    return marketing_format

def _convert_enums_to_strings(obj):
    """Enum 객체를 문자열로 변환"""
    if isinstance(obj, dict):
        return {key: _convert_enums_to_strings(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_enums_to_strings(item) for item in obj]
    elif hasattr(obj, 'value'):  # Enum 객체
        return obj.value
    else:
        return obj

# 분석 진행 상황 업데이트 함수

def update_analysis_progress(step: str, status: str = "in_progress"):

    """분석 진행 상황 업데이트"""

    if "analysis_progress" not in st.session_state:

        st.session_state.analysis_progress = {}

    

    st.session_state.analysis_progress[step] = status



# matplotlib import 및 설정

import matplotlib

import matplotlib.pyplot as plt

import seaborn as sns



# 한글 폰트 설정은 위에서 이미 처리됨


print("[OK] Matplotlib loaded successfully")









# run_analysis.py 직접 import

sys.path.insert(0, str(Path(__file__).parent.parent))  # open_sdk 디렉토리 추가

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents_new"))  # agents_new 추가

from run_analysis import run_full_analysis_pipeline

# Marketing Module import (LangChain Version)
MARKETING_MODULE_AVAILABLE = False
try:
    from agents_new.marketing_agent.marketing_langchain import run_marketing_sync_langchain as run_marketing_sync
    MARKETING_MODULE_AVAILABLE = True
    print("[OK] Marketing Module (LangChain) loaded successfully")
except ImportError as e:

    print(f"[WARN] Marketing Module import failed: {e}")
except Exception as e:

    print(f"[ERROR] Marketing Module error: {e}")
    import traceback
    traceback.print_exc()
# sys.path.insert (라인 359)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents_new"))

# ===== NewProductAgent import 추가 =====
NEW_PRODUCT_AGENT_AVAILABLE = False
try:
    from agents_new.new_product_agent import NewProductAgent
    NEW_PRODUCT_AGENT_AVAILABLE = True
    print("[OK] New Product Agent loaded successfully")
except ImportError as e:
    print(f"[WARN] New Product Agent import failed: {e}")
except Exception as e:
    print(f"[ERROR] New Product Agent error: {e}")
    import traceback
    traceback.print_exc()

# run_analysis.py 직접 import (기존 코드)
from run_analysis import run_full_analysis_pipeline
# Google Maps MCP Lookup import (HTTP Version)
MCP_LOOKUP_AVAILABLE = False
GOOGLE_MAPS_TOOLS_AVAILABLE = False
try:
    from agents_new.google_map_mcp.http_client import run_lookup_from_code_http as run_gm_lookup
    from agents_new.google_map_mcp.langchain_tools import get_google_maps_tools
    MCP_LOOKUP_AVAILABLE = True
    GOOGLE_MAPS_TOOLS_AVAILABLE = True
    print("[OK] Google Maps MCP Lookup (HTTP) loaded successfully")
    print("[OK] Google Maps LangChain Tools loaded successfully")
except ImportError as e:
    print(f"[WARN] Google Maps MCP Lookup import failed: {e}")
except Exception as e:
    print(f"[ERROR] Google Maps MCP Lookup error: {e}")
    import traceback

    traceback.print_exc()

# Panorama Analysis는 위에서 초기화됨

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



# OpenAI SDK로 Gemini 2.5 Flash 사용

try:

    from openai import OpenAI

    OPENAI_AVAILABLE = True

    # OpenAI SDK로 Gemini API 호출

    openai_client = OpenAI(

        api_key=os.getenv("GEMINI_API_KEY"),

        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"

    )

    print("[OK] OpenAI SDK with Gemini 2.5 Flash initialized")

except Exception as e:

    OPENAI_AVAILABLE = False

    openai_client = None

    print(f"OpenAI client with Gemini not available: {e}")





# 자동 새로고침 비활성화 (무한 루프 방지)

# if st.session_state.get('is_analyzing', False) and not st.session_state.get('stop_autorefresh', False):

#     st_autorefresh(interval=5000, limit=50, key="logrefresh")



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

if 'mcp_search_initialized' not in st.session_state:

    st.session_state.mcp_search_initialized = False

if 'mcp_search_progress' not in st.session_state:

    st.session_state.mcp_search_progress = {

        "total": 0,

        "processed": 0,

        "success": 0,

        "failed": 0

    }



def generate_marketplace_summary_with_gemini(marketplace_data):

    """OpenAI를 사용하여 상권 분석 요약 생성"""

    try:

        # OpenAI 클라이언트 확인

        if not OPENAI_AVAILABLE or not openai_client:

            return None

        

        # 상권 데이터를 텍스트로 변환

        data_text = json.dumps(marketplace_data, ensure_ascii=False, indent=2)

        

        # OpenAI 프롬프트

        prompt = f"""

다음은 상권 분석 데이터입니다. 이를 바탕으로 전문적이고 상세한 상권 분석 요약을 작성해주세요.



상권 데이터:

{data_text}



다음 형식으로 분석 요약을 작성해주세요:



## 🏬 상권 분석 요약



### 📍 상권 개요

- 상권 유형: [유형]

- 분석 면적: [면적]

- 점포수: [점포수]



### 📊 주요 지표

- 매출 현황: [현재 매출액]

- 성장률: [전년 대비]

- 상권 활성도: [점포 증감]



### 💡 핵심 인사이트

1. 상권 강점: [강점 분석]

2. 상권 약점: [약점 분석]

3. 기회 요소: [기회 분석]

4. 위험 요소: [위험 분석]



### 🎯 추천 업종

- 적합한 업종: [업종 추천]

- 성공 요인: [성공 조건]

- 주의사항: [주의점]



### 📈 전망 및 제언

- 상권 전망: [미래 전망]

- 창업 제언: [창업 가이드]

- 마케팅 전략: [마케팅 방향]



전문적이고 실용적인 관점에서 작성해주세요.

"""

        

        # OpenAI SDK로 Gemini 2.5 Flash 호출

        response = openai_client.chat.completions.create(

            model="gemini-2.5-flash",

            messages=[

                {"role": "system", "content": "당신은 전문적인 상권 분석 전문가입니다. 데이터를 바탕으로 실용적이고 통찰력 있는 분석을 제공합니다."},

                {"role": "user", "content": prompt}

            ],

            temperature=0.7,

            max_tokens=2000

        )

        

        if response and response.choices:

            return response.choices[0].message.content

        else:

            return None

            

    except Exception as e:

        print(f"OpenAI 상권 분석 실패: {e}")

        return None



def generate_final_report_with_gemini(analysis_data):

    """OpenAI를 사용해서 최종 리포트 생성"""

    if not OPENAI_AVAILABLE or not openai_client:

        return None, None

    

    try:

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

        

        response = openai_client.chat.completions.create(

            model="gemini-2.5-flash",

            messages=[

                {"role": "system", "content": "당신은 전문적인 비즈니스 분석가입니다. 데이터를 바탕으로 실행 가능한 전략과 명확한 리포트를 작성합니다."},

                {"role": "user", "content": prompt}

            ],

            temperature=0.7,

            max_tokens=3000

        )

        

        # MD와 JSON 분리

        md_content = response.choices[0].message.content

        json_content = None

        

        # JSON 부분 추출

        if "```json" in md_content:

            json_start = md_content.find("```json") + 7

            json_end = md_content.find("```", json_start)

            if json_end > json_start:

                json_str = md_content[json_start:json_end].strip()

                try:

                    json_content = json.loads(json_str)

                except:

                    json_content = None

        

        return md_content, json_content

        

    except Exception as e:

        print(f"OpenAI 리포트 생성 실패: {e}")

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
        # store_analysis에서 상권명 가져오기
        marketplace_json = None
        commercial_area_name = None
        
        if "store_analysis" in data and data["store_analysis"]:
            try:
                store_analysis = data["store_analysis"]
                # 먼저 store_overview에서 직접 확인
                if "store_overview" in store_analysis:
                    commercial_area_name = store_analysis["store_overview"].get("commercial_area", None)
                # 없으면 json_output 안에서 확인
                elif "json_output" in store_analysis and "store_overview" in store_analysis["json_output"]:
                    commercial_area_name = store_analysis["json_output"]["store_overview"].get("commercial_area", None)
                
                if commercial_area_name:
                    print(f"[INFO] 상권명 확인: {commercial_area_name}")
                else:
                    print(f"[WARN] 상권명을 찾을 수 없습니다.")
            except Exception as e:
                print(f"[WARN] 상권명 추출 실패: {e}")
        
        # 상권명이 있으면 상권분석서비스_결과 폴더에서 JSON 파일 찾기
        if commercial_area_name:
            marketplace_folder = Path(__file__).parent.parent.parent / "agents_new" / "data outputs" / "상권분석서비스_결과"
            marketplace_json_file = marketplace_folder / f"{commercial_area_name}.json"
            
            if marketplace_json_file.exists():
                try:
                    with open(marketplace_json_file, 'r', encoding='utf-8') as f:
                        marketplace_json = json.load(f)
                    print(f"[OK] 상권 분석 JSON 로드 성공: {commercial_area_name}")
                except Exception as e:
                    print(f"[WARN] 상권 분석 JSON 로드 실패: {e}")
            else:
                print(f"[WARN] 상권 분석 JSON 파일 없음: {marketplace_json_file}")
        
        # marketplace_json이 있으면 사용
        if marketplace_json:
            data["marketplace_analysis"] = marketplace_json
        else:
            # 기존 방식으로 fallback: 먼저 analysis 폴더 내부에서 찾기
            marketplace_file = latest_dir / "marketplace" / "marketplace_data.json"
            
            # 내부에 없으면 별도 marketplace_{timestamp} 폴더에서 찾기
            if not marketplace_file.exists():
                marketplace_dirs = sorted(
                    output_dir.glob("marketplace_*"), 
                    key=os.path.getmtime, 
                    reverse=True
                )
                if marketplace_dirs:
                    marketplace_file = marketplace_dirs[0] / "marketplace_data.json"
                    print(f"[INFO] marketplace 파일을 별도 폴더에서 찾음: {marketplace_file.parent.name}")

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

                    "path": str(chart_file),  # 절대 경로 사용

                    "absolute_path": str(chart_file),

                    "type": "store_chart"

                })

        

        # Mobility 차트들

        mobility_charts_dir = analysis_dir / "mobility_charts"

        if mobility_charts_dir.exists():

            for chart_file in mobility_charts_dir.glob("*.png"):

                viz_data["mobility_charts"].append({

                    "name": chart_file.stem,

                    "path": str(chart_file),  # 절대 경로 사용

                    "absolute_path": str(chart_file),

                    "type": "mobility_chart"

                })

        

        # Panorama 이미지들

        panorama_images_dir = analysis_dir / "panorama" / "images"

        if panorama_images_dir.exists():

            for img_file in panorama_images_dir.glob("*.jpg"):

                viz_data["panorama_images"].append({

                    "name": img_file.stem,

                    "path": str(img_file),  # 절대 경로 사용

                    "absolute_path": str(img_file),

                    "type": "panorama_image"

                })

        

        # Spatial 시각화 파일들

        spatial_map = analysis_dir / "spatial_map.html"

        spatial_chart = analysis_dir / "spatial_analysis.png"

        

        if spatial_map.exists():

            viz_data["spatial_files"].append({

                "name": "공간 분석 지도",

                "path": str(spatial_map),  # 절대 경로 사용

                "absolute_path": str(spatial_map),

                "type": "spatial_map"

            })

        

        if spatial_chart.exists():

            viz_data["spatial_files"].append({

                "name": "공간 분석 차트",

                "path": str(spatial_chart),  # 절대 경로 사용

                "absolute_path": str(spatial_chart),

                "type": "spatial_chart"

            })

        

        # Panorama 지도

        panorama_map = analysis_dir / "panorama" / "analysis_map.html"

        if panorama_map.exists():

            viz_data["spatial_files"].append({

                "name": "파노라마 분석 지도",

                "path": str(panorama_map),  # 절대 경로 사용

                "absolute_path": str(panorama_map),

                "type": "panorama_map"

            })
        image_locations_map = analysis_dir / "panorama" / "image_locations_map.html"
        if image_locations_map.exists():
            viz_data["spatial_files"].append({
                "name": "📍 파노라마 이미지 위치 지도",
                "path": str(image_locations_map),
                "absolute_path": str(image_locations_map),
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



#def display_final_report_button(store_code, analysis_data):

 #   """최종 리포트 생성 버튼 표시"""

#    if not st.session_state.final_report_generated:

 #       if st.button("📋 최종 리포트 생성 (Gemini)", type="primary"):
#
 #           with st.spinner("Gemini로 최종 리포트를 생성 중..."):
#
 #               md_content, json_content = generate_final_report_with_gemini(analysis_data)
#
 #               if md_content:

  #                  report_dir = save_final_reports(store_code, md_content, json_content)

   #                 if report_dir:

#                        st.success(f"최종 리포트가 생성되었습니다: {report_dir}")

#                        st.session_state.final_report_generated = True

#                        st.rerun()
#
  #              else:
##
  #                  st.error("최종 리포트 생성에 실패했습니다.")
#
 #   else:

   #     st.info("✅ 최종 리포트가 이미 생성되었습니다.")





def generate_comprehensive_analysis_with_gemini(analysis_data):

    """OpenAI SDK(Gemini 2.5 Flash)를 사용해서 전체 분석 데이터를 종합하여 인사이트 생성"""

    try:

        if not OPENAI_AVAILABLE or not openai_client:

            return None

        

        # 분석 데이터 요약

        store_data = analysis_data.get("store_analysis", {})

        marketing_data = analysis_data.get("marketing_strategy", {})

        panorama_data = analysis_data.get("panorama_analysis", {})

        marketplace_data = analysis_data.get("marketplace_analysis", {})

        mobility_data = analysis_data.get("mobility_analysis", {})

        

        # 데이터 요약 생성

        summary_text = f"""

## 매장 분석 데이터 요약



### 🏪 매장 기본 정보

- 매장명: {store_data.get('store_overview', {}).get('name', 'N/A')}

- 업종: {store_data.get('store_overview', {}).get('industry', 'N/A')}

- 상권: {store_data.get('store_overview', {}).get('commercial_area', 'N/A')}

- 운영 개월: {store_data.get('store_overview', {}).get('operating_months', 'N/A')}개월



### 📈 매출 분석

- 매출액 추세: {store_data.get('sales_analysis', {}).get('trends', {}).get('sales_amount', {}).get('trend', 'N/A')}

- 매출건수 추세: {store_data.get('sales_analysis', {}).get('trends', {}).get('sales_count', {}).get('trend', 'N/A')}

- 고유고객 추세: {store_data.get('sales_analysis', {}).get('trends', {}).get('unique_customers', {}).get('trend', 'N/A')}

- 평균 거래액 추세: {store_data.get('sales_analysis', {}).get('trends', {}).get('avg_transaction', {}).get('trend', 'N/A')}



### 👥 고객 분석

- 성별 분포: 남성 {store_data.get('customer_analysis', {}).get('gender_distribution', {}).get('male_ratio', 0):.1f}% / 여성 {store_data.get('customer_analysis', {}).get('gender_distribution', {}).get('female_ratio', 0):.1f}%

- 주요 연령대: {max(store_data.get('customer_analysis', {}).get('age_group_distribution', {}), key=store_data.get('customer_analysis', {}).get('age_group_distribution', {}).get) if store_data.get('customer_analysis', {}).get('age_group_distribution') else 'N/A'}



### 🎯 마케팅 전략

- 전략 수: {len(marketing_data.get('marketing_strategies', []))}개

- 페르소나 유형: {marketing_data.get('persona_analysis', {}).get('persona_type', 'N/A')}



### 🌆 지역 환경 분석

- 지역 유형: {panorama_data.get('area_summary', {}).get('dominant_zone_type', 'N/A')}

- 상권 분위기: {panorama_data.get('comprehensive_scores', {}).get('commercial_atmosphere', 'N/A')}/10



### 🏬 상권 분석

- 점포수: {marketplace_data.get('상권_점포수', 'N/A')}개

- 매출액: {marketplace_data.get('상권_매출액', 'N/A')}만원

        """

        

        prompt = f"""다음 매장 분석 데이터를 바탕으로 종합적인 비즈니스 인사이트와 전략적 제안을 작성해주세요.



{summary_text}



다음 형식으로 작성해주세요:



## 🎯 종합 비즈니스 분석 리포트



### 📊 핵심 인사이트

- 매장의 주요 강점과 약점

- 시장에서의 위치와 경쟁력

- 성장 잠재력 평가



### 🔍 상세 분석

- 매출 동향 분석 및 전망

- 고객층 특성 및 타겟팅 전략

- 상권 환경과의 적합성

- 마케팅 전략의 효과성



### ⚠️ 위험 요소 및 주의사항

- 매장 운영상 주의해야 할 점

- 시장 변화에 따른 리스크

- 경쟁 환경 변화 대응 방안



### 🚀 성장 전략 제안

- 매출 증대를 위한 구체적 방안

- 고객 유치 및 리텐션 전략

- 상권 특성을 활용한 차별화 방안

- 마케팅 전략 개선 제안



### 💡 실행 가능한 액션 플랜

- 단기 (1-3개월) 실행 계획

- 중기 (3-6개월) 실행 계획

- 장기 (6-12개월) 실행 계획



전문적이고 실용적인 분석을 제공해주세요."""

        

        response = openai_client.chat.completions.create(

            model="gemini-2.5-flash",

            messages=[

                {"role": "system", "content": "당신은 전문적인 비즈니스 분석가이자 컨설턴트입니다. 데이터를 종합하여 실행 가능한 전략적 인사이트를 제공합니다."},

                {"role": "user", "content": prompt}

            ],

            temperature=0.7,

            max_tokens=20000

        )

        

        return response.choices[0].message.content.strip()

        

    except Exception as e:

        print(f"[ERROR] OpenAI(Gemini) 종합 분석 생성 실패: {e}")

        return None





def display_store_overview(analysis_data):

    """매장 개요 탭 - 간단하고 핵심적인 개요"""

    st.markdown("### 🏪 매장 개요")

    

    store_data = analysis_data.get("store_analysis", {})

    if not store_data:

        st.info("매장 분석 데이터가 없습니다.")

        return

    

    store_info = store_data.get("store_overview", {})

    sales_data = store_data.get("sales_analysis", {})

    customer_data = store_data.get("customer_analysis", {})

    marketing = analysis_data.get("marketing_strategy", {})

    marketplace = analysis_data.get("marketplace_analysis", {})

    

    # 핵심 정보만 간단하게 표시

    col1, col2, col3 = st.columns(3)

    

    with col1:

        st.markdown("#### 🏪 기본 정보")

        st.write(f"**매장명:** {store_info.get('name', 'N/A')}")

        st.write(f"**업종:** {store_info.get('industry', 'N/A')}")

        st.write(f"**상권:** {store_info.get('commercial_area', 'N/A')}")

        st.write(f"**운영기간:** {store_info.get('operating_months', 0):.1f}개월")

    

    with col2:

        st.markdown("#### 📈 핵심 지표")

        # 매출 추세

        sales_trend = sales_data.get("trends", {}).get("sales_amount", {}).get("trend", "N/A")

        trend_icon = "📈" if "상승" in sales_trend else "📉" if "하락" in sales_trend else "➡️"

        st.write(f"**매출 추세:** {trend_icon} {sales_trend}")

        

        # 고객 추세

        customer_trend = sales_data.get("trends", {}).get("unique_customers", {}).get("trend", "N/A")

        trend_icon = "📈" if "상승" in customer_trend else "📉" if "하락" in customer_trend else "➡️"

        st.write(f"**고객 추세:** {trend_icon} {customer_trend}")

        

        # 순위

        industry_rank = sales_data.get("rankings", {}).get("industry_rank", {}).get("average", "N/A")

        st.write(f"**동종업계 순위:** {industry_rank}위")

        

        # 품질 점수

        quality_score = store_data.get("report_metadata", {}).get("quality_score", 0)

        st.write(f"**분석 품질:** {quality_score:.1%}")

    

    with col3:

        st.markdown("#### 👥 고객 특성")

        # 성별

        male_ratio = customer_data.get("gender_distribution", {}).get("male_ratio", 0)

        female_ratio = customer_data.get("gender_distribution", {}).get("female_ratio", 0)

        st.write(f"**성별:** 남성 {male_ratio:.1f}% / 여성 {female_ratio:.1f}%")

        

        # 주요 연령대

        age_dist = customer_data.get("age_group_distribution", {})

        main_age = max(age_dist, key=age_dist.get) if age_dist else "N/A"

        main_ratio = age_dist.get(main_age, 0) if age_dist else 0

        st.write(f"**주요 연령대:** {main_age} ({main_ratio:.1f}%)")

        

        # 고객 유형

        customer_dist = customer_data.get("customer_type_analysis", {}).get("customer_distribution", {})

        floating_ratio = customer_dist.get("floating", 0)

        st.write(f"**고객 유형:** 유동 {floating_ratio:.1f}%")

        

        # 마케팅 전략 수

        strategy_count = len(marketing.get("marketing_strategies", []))

        st.write(f"**마케팅 전략:** {strategy_count}개")

    # 마케팅 & Google Maps 통합 결과 표시
    integration_result = analysis_data.get("marketing_google_maps_integration")
    if integration_result:
        st.markdown("#### 🔗 마케팅 & Google Maps 통합 분석")
        
        if integration_result.get("integration_status") == "success":
            st.success("✅ 통합 분석 완료")
            
            # 통합 결과 파일 표시
            output_file = integration_result.get("output_file")
            if output_file and os.path.exists(output_file):
                st.markdown(f"📄 **통합 분석 결과 파일:** `{os.path.basename(output_file)}`")
                
                # 파일 내용 미리보기
                with st.expander("📋 통합 분석 결과 미리보기", expanded=False):
                    try:
                        with open(output_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            st.text(content[:1000] + "..." if len(content) > 1000 else content)
                    except Exception as e:
                        st.error(f"파일 읽기 실패: {e}")
            
            # Google Maps 정보 요약
            google_maps_info = integration_result.get("google_maps_info", {})
            if "error" not in google_maps_info:
                place_details = google_maps_info.get("place_details", {})
                if place_details and "error" not in place_details:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**매장명:** {place_details.get('name', 'N/A')}")
                        st.write(f"**평점:** {place_details.get('rating', 'N/A')}/5.0")
                    with col2:
                        st.write(f"**리뷰 수:** {place_details.get('user_ratings_total', 0)}개")
                        st.write(f"**전화번호:** {place_details.get('formatted_phone_number', 'N/A')}")
        else:
            st.warning("⚠️ 통합 분석 실패")
            error_msg = integration_result.get("error", "알 수 없는 오류")
            st.error(f"오류: {error_msg}")

    

    # 상권 정보 (간단하게)

    if marketplace:

        st.markdown("#### 🏘️ 상권 정보")

        col1, col2 = st.columns(2)

        with col1:

            st.write(f"**상권명:** {marketplace.get('상권명', 'N/A')}")

        with col2:

            store_count = marketplace.get("상권_점포수", "N/A")

            st.write(f"**점포수:** {store_count}개")

    

    # MCP 구글맵 검색 결과 (있으면 표시)

    mcp_result = analysis_data.get("mcp_search_result", {})

    mcp_file_path_str = mcp_result.get("output_path") or mcp_result.get("file")
    if mcp_file_path_str:
        st.markdown("---")

        st.markdown("#### 🗺️ Google Maps 정보")

        

        # txt 파일 읽기

        try:

            mcp_file_path = Path(mcp_file_path_str)
            if mcp_file_path.exists():

                with open(mcp_file_path, 'r', encoding='utf-8') as f:

                    mcp_content = f.read()

                

                # expander로 축약해서 표시

                with st.expander("📍 Google Maps 검색 결과 보기", expanded=False):

                    st.text(mcp_content)

        except Exception as e:

            st.warning(f"MCP 검색 결과 로드 실패: {e}")

    

    # AI 종합 분석 버튼

    st.markdown("---")

    st.markdown("#### 🤖 AI 종합 분석")

    if st.button("🔍 종합 분석 생성", type="primary", help="모든 분석 데이터를 종합하여 AI가 인사이트를 생성합니다"):

        with st.spinner("AI가 종합 분석을 생성하고 있습니다..."):

            comprehensive_analysis = generate_comprehensive_analysis_with_gemini(analysis_data)

            if comprehensive_analysis:

                st.markdown("##### 📋 AI 종합 분석 결과")

                st.write(comprehensive_analysis)

            else:

                st.error("종합 분석 생성에 실패했습니다.")



def display_customer_analysis(analysis_data):

    """고객 분석 탭 + 시각화 - JSON 데이터 기반 체계적 분석"""

    st.markdown("### 👥 고객 분석")

    

    store_data = analysis_data.get("store_analysis", {})

    if not store_data:

        st.info("매장 분석 데이터가 없습니다.")

        return

    

    customer_data = store_data.get("customer_analysis", {})

    if not customer_data:

        st.info("고객 분석 데이터가 없습니다.")

        return

    

    # 1. 성별 분포 (상세 분석)

    gender_data = customer_data.get("gender_distribution", {})

    if gender_data:

        st.markdown("#### 📊 성별 분포")

        col1, col2, col3 = st.columns([1, 1, 2])

        

        with col1:

            male_ratio = gender_data.get("male_ratio", 0)

            st.metric("남성", f"{male_ratio:.1f}%", help="전체 고객 중 남성 비율")

        

        with col2:

            female_ratio = gender_data.get("female_ratio", 0)

            st.metric("여성", f"{female_ratio:.1f}%", help="전체 고객 중 여성 비율")

        

        with col3:

            # 성별 비율 차이 분석

            gender_diff = abs(male_ratio - female_ratio)

            if gender_diff > 30:

                st.warning(f"성별 편중이 심합니다 (차이: {gender_diff:.1f}%)")

            elif gender_diff > 15:

                st.info(f"성별 편중이 있습니다 (차이: {gender_diff:.1f}%)")

            else:

                st.success("성별 분포가 균형적입니다")

    

    # 2. 연령대별 분포 (상세 분석)

    age_data = customer_data.get("age_group_distribution", {})

    if age_data:

        st.markdown("#### 🎂 연령대별 고객 분포")

        

        # 연령대별 카드 표시

        age_cols = st.columns(5)

        age_groups = ["20대 이하", "30대", "40대", "50대", "60대 이상"]

        

        for i, age_group in enumerate(age_groups):

            with age_cols[i]:

                ratio = age_data.get(age_group, 0)

                st.metric(age_group, f"{ratio:.1f}%")

        

        # 주요 연령대 분석

        max_age = max(age_data.items(), key=lambda x: x[1])

        st.info(f"**주요 고객층:** {max_age[0]} ({max_age[1]:.1f}%)")

    

    # 3. 상세 고객 비율 (성별+연령대 조합)

    detailed_ratios = customer_data.get("detailed_customer_ratios", {})

    if detailed_ratios:

        st.markdown("#### 🔍 상세 고객 비율 (성별+연령대)")

        

        # 상위 5개 고객 세그먼트 표시

        top_segments = sorted(detailed_ratios.items(), key=lambda x: x[1], reverse=True)[:5]

        

        for i, (segment, ratio) in enumerate(top_segments, 1):

            col1, col2 = st.columns([1, 4])

            with col1:

                st.write(f"**{i}위**")

            with col2:

                st.write(f"{segment}: {ratio:.1f}%")

                # 진행률 바

                st.progress(ratio / 100)

    

    # 4. 고객 유형 분석 (수정된 화살표 방향)

    customer_type = customer_data.get("customer_type_analysis", {})

    if customer_type:

        st.markdown("#### 🔄 고객 유형 분석")

        

        new_customers = customer_type.get("new_customers", {})

        returning_customers = customer_type.get("returning_customers", {})

        

        col1, col2 = st.columns(2)

        

        with col1:

            new_ratio = new_customers.get("ratio", 0)

            new_trend = new_customers.get("trend", "N/A")

            

            # 화살표 방향 수정

            if "상승" in new_trend or "증가" in new_trend:

                delta_icon = "📈"

            elif "하락" in new_trend or "감소" in new_trend:

                delta_icon = "📉"

            else:

                delta_icon = "➡️"

            

            st.metric("신규 고객", f"{new_ratio:.1f}%", delta=f"{delta_icon} {new_trend}")

        

        with col2:

            return_ratio = returning_customers.get("ratio", 0)

            return_trend = returning_customers.get("trend", "N/A")

            

            # 화살표 방향 수정

            if "상승" in return_trend or "증가" in return_trend:

                delta_icon = "📈"

            elif "하락" in return_trend or "감소" in return_trend:

                delta_icon = "📉"

            else:

                delta_icon = "➡️"

            

            st.metric("재방문 고객", f"{return_ratio:.1f}%", delta=f"{delta_icon} {return_trend}")

        

        # 고객 분포 (상세 분석)

        distribution = customer_type.get("customer_distribution", {})

        if distribution:

            st.markdown("#### 🏠 고객 분포 유형")

            

            dist_cols = st.columns(3)

            dist_types = [

                ("주거형", "residential", "🏠", "지역 주민"),

                ("직장형", "workplace", "🏢", "직장인"),

                ("유동형", "floating", "🚶", "유동인구")

            ]

            

            for i, (name, key, icon, desc) in enumerate(dist_types):

                with dist_cols[i]:

                    ratio = distribution.get(key, 0)

                    st.metric(f"{icon} {name}", f"{ratio:.1f}%", help=desc)

            

            # 주요 고객 유형 분석

            max_type = max(distribution.items(), key=lambda x: x[1])

            type_names = {"residential": "주거형", "workplace": "직장형", "floating": "유동형"}

            st.info(f"**주요 고객 유형:** {type_names.get(max_type[0], max_type[0])} ({max_type[1]:.1f}%)")

    

    # 5. 고객 분석 요약

    st.markdown("#### 📋 고객 분석 요약")

    

    # 주요 인사이트 생성

    insights = []

    

    if gender_data:

        male_ratio = gender_data.get("male_ratio", 0)

        if male_ratio > 60:

            insights.append(f"남성 고객이 {male_ratio:.1f}%로 압도적")

        elif male_ratio < 40:

            insights.append(f"여성 고객이 {100-male_ratio:.1f}%로 많음")

        else:

            insights.append("성별 분포가 균형적")

    

    if age_data:

        max_age = max(age_data.items(), key=lambda x: x[1])

        insights.append(f"{max_age[0]} 고객층이 {max_age[1]:.1f}%로 주력")

    

    if customer_type:

        new_ratio = customer_type.get("new_customers", {}).get("ratio", 0)

        return_ratio = customer_type.get("returning_customers", {}).get("ratio", 0)

        if return_ratio > new_ratio:

            insights.append(f"재방문 고객({return_ratio:.1f}%)이 신규 고객({new_ratio:.1f}%)보다 많음")

        else:

            insights.append(f"신규 고객({new_ratio:.1f}%)이 재방문 고객({return_ratio:.1f}%)보다 많음")

    

    if insights:

        for i, insight in enumerate(insights, 1):

            st.write(f"{i}. {insight}")

    

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

                            st.image(chart_path, caption=chart_name, use_container_width=True)

                        except Exception as e:

                            st.error(f"차트 로딩 실패: {chart_name}")
                            st.caption(f"경로: {chart_path}")
                            st.caption(f"에러: {str(e)}")
                    else:
                        st.warning(f"파일 없음: {chart_name}")
                        if chart_path:
                            st.caption(f"경로: {chart_path}")
                            st.caption(f"존재: {Path(chart_path).exists()}")

        else:

            st.info("고객 관련 차트가 없습니다.")



def display_mobility_analysis(analysis_data):

    """이동 패턴 분석 탭 - JSON 데이터 기반 체계적 분석"""

    st.markdown("### 🚶 이동 패턴 분석")

    

    mobility_data = analysis_data.get("mobility_analysis", {})

    if not mobility_data:

        st.info("이동 패턴 분석 데이터가 없습니다.")

        return

    

    analysis = mobility_data.get("analysis", {})

    if not analysis:

        st.info("이동 패턴 분석 결과가 없습니다.")

        return

    

    # 1. 기본 정보

    st.markdown("#### 📍 분석 기본 정보")

    col1, col2 = st.columns(2)

    

    with col1:

        st.write(f"**분석 대상:** {mobility_data.get('target_dong', 'N/A')}")

        st.write(f"**분석 시점:** {mobility_data.get('timestamp', 'N/A')}")

    

    with col2:

        total_moves = sum(analysis.get("part1_move_types", {}).values())

        st.write(f"**총 이동량:** {total_moves:,}명")

    

    # 2. 이동 유형 분석 (상세)

    move_types = analysis.get("part1_move_types", {})

    if move_types:

        st.markdown("#### 🔄 이동 유형 분석")

        

        inflow = move_types.get('유입', 0)

        outflow = move_types.get('유출', 0)

        internal = move_types.get('내부이동', 0)

        total = inflow + outflow + internal

        

        col1, col2, col3 = st.columns(3)

        

        with col1:

            inflow_ratio = (inflow / total * 100) if total > 0 else 0

            st.metric("유입", f"{inflow:,}명", f"{inflow_ratio:.1f}%")

        

        with col2:

            outflow_ratio = (outflow / total * 100) if total > 0 else 0

            st.metric("유출", f"{outflow:,}명", f"{outflow_ratio:.1f}%")

        

        with col3:

            internal_ratio = (internal / total * 100) if total > 0 else 0

            st.metric("내부이동", f"{internal:,}명", f"{internal_ratio:.1f}%")

        

        # 이동 유형 분석

        if outflow > inflow:

            st.warning("유출이 유입보다 많아 인구 감소 추세입니다")

        elif inflow > outflow:

            st.success("유입이 유출보다 많아 인구 증가 추세입니다")

        else:

            st.info("유입과 유출이 균형을 이루고 있습니다")

    

    # 3. 시간대별 패턴 분석 (상세)

    time_pattern = analysis.get("part2_time_pattern", {})

    if time_pattern:

        st.markdown("#### ⏰ 시간대별 이동 패턴")

        

        # 최대 이동 시간

        peak_hour = max(time_pattern.items(), key=lambda x: x[1])

        st.write(f"**최대 이동 시간:** {peak_hour[0]}시 ({peak_hour[1]:,}명)")

        

        # 시간대별 분류

        morning_hours = {k: v for k, v in time_pattern.items() if 6 <= int(k) <= 9}

        afternoon_hours = {k: v for k, v in time_pattern.items() if 10 <= int(k) <= 17}

        evening_hours = {k: v for k, v in time_pattern.items() if 18 <= int(k) <= 22}

        night_hours = {k: v for k, v in time_pattern.items() if 23 <= int(k) or int(k) <= 5}

        

        col1, col2, col3, col4 = st.columns(4)

        

        with col1:

            morning_total = sum(morning_hours.values())

            st.metric("오전 (6-9시)", f"{morning_total:,}명")

        

        with col2:

            afternoon_total = sum(afternoon_hours.values())

            st.metric("오후 (10-17시)", f"{afternoon_total:,}명")

        

        with col3:

            evening_total = sum(evening_hours.values())

            st.metric("저녁 (18-22시)", f"{evening_total:,}명")

        

        with col4:

            night_total = sum(night_hours.values())

            st.metric("야간 (23-5시)", f"{night_total:,}명")

        

        # 상위 5개 시간대

        top_hours = sorted(time_pattern.items(), key=lambda x: x[1], reverse=True)[:5]

        st.write("**상위 이동 시간대:**")

        for i, (hour, count) in enumerate(top_hours, 1):

            st.write(f"{i}. {hour}시: {count:,}명")

    

    # 4. 목적별 분석 (상세)

    purpose_data = analysis.get("part3_purpose", {})

    if purpose_data:

        st.markdown("#### 🎯 목적별 이동 분석")

        

        total_purpose = sum(purpose_data.values())

        top_purposes = sorted(purpose_data.items(), key=lambda x: x[1], reverse=True)[:5]

        

        for i, (purpose, count) in enumerate(top_purposes, 1):

            percentage = (count / total_purpose * 100) if total_purpose > 0 else 0

            col1, col2 = st.columns([1, 3])

            

            with col1:

                st.write(f"**{i}위**")

            with col2:

                st.write(f"{purpose}: {count:,}명 ({percentage:.1f}%)")

                st.progress(percentage / 100)

    

    # 5. 교통수단별 분석 (상세)

    transport_data = analysis.get("part4_transport", {})

    if transport_data:

        st.markdown("#### 🚗 교통수단별 이용 분석")

        

        total_transport = sum(transport_data.values())

        

        # 주요 교통수단

        main_transports = {

            "차량": transport_data.get('차량', 0),

            "지하철": transport_data.get('지하철', 0),

            "도보": transport_data.get('도보', 0),

            "버스": transport_data.get('일반버스', 0) + transport_data.get('광역버스', 0),

            "기타": transport_data.get('기타', 0)

        }

        

        col1, col2 = st.columns(2)

        

        with col1:

            for transport, count in list(main_transports.items())[:3]:

                percentage = (count / total_transport * 100) if total_transport > 0 else 0

                st.metric(transport, f"{count:,}명", f"{percentage:.1f}%")

        

        with col2:

            for transport, count in list(main_transports.items())[3:]:

                percentage = (count / total_transport * 100) if total_transport > 0 else 0

                st.metric(transport, f"{count:,}명", f"{percentage:.1f}%")

    

    # 6. 연령대별 분석 (상세)

    age_data = analysis.get("part5_age", {})

    if age_data:

        st.markdown("#### 👥 연령대별 이동 분석")

        

        total_age = sum(age_data.values())

        age_groups = {

            "10대 이하": age_data.get("00대", 0) + age_data.get("10대", 0),

            "20-30대": age_data.get("20대", 0) + age_data.get("30대", 0),

            "40-50대": age_data.get("40대", 0) + age_data.get("50대", 0),

            "60대 이상": age_data.get("60대", 0) + age_data.get("70대 이상", 0)

        }

        

        age_cols = st.columns(4)

        for i, (age_group, count) in enumerate(age_groups.items()):

            with age_cols[i]:

                percentage = (count / total_age * 100) if total_age > 0 else 0

                st.metric(age_group, f"{count:,}명", f"{percentage:.1f}%")

    

    # 7. 연령대별 목적 분석

    age_purpose_data = analysis.get("part5_2_age_purpose", {})

    if age_purpose_data:

        st.markdown("#### 🎯 연령대별 주요 목적")

        

        for age_group, data in age_purpose_data.items():

            if isinstance(data, dict):

                purpose = data.get("top_purpose", "N/A")

                percentage = data.get("percentage", 0)

                st.write(f"**{age_group}:** {purpose} ({percentage:.1f}%)")

    

    # 8. 이동 패턴 요약

    st.markdown("#### 📋 이동 패턴 요약")

    

    insights = []

    

    if move_types:

        inflow = move_types.get('유입', 0)

        outflow = move_types.get('유출', 0)

        if outflow > inflow:

            insights.append(f"유출({outflow:,}명)이 유입({inflow:,}명)보다 많아 인구 감소 추세")

        else:

            insights.append(f"유입({inflow:,}명)이 유출({outflow:,}명)보다 많아 인구 증가 추세")

    

    if time_pattern:

        peak_hour = max(time_pattern.items(), key=lambda x: x[1])

        insights.append(f"{peak_hour[0]}시에 최대 이동량({peak_hour[1]:,}명) 발생")

    

    if purpose_data:

        top_purpose = max(purpose_data.items(), key=lambda x: x[1])

        insights.append(f"주요 이동 목적: {top_purpose[0]}({top_purpose[1]:,}명)")

    

    if transport_data:

        top_transport = max(transport_data.items(), key=lambda x: x[1])

        insights.append(f"주요 교통수단: {top_transport[0]}({top_transport[1]:,}명)")

    

    if insights:

        for i, insight in enumerate(insights, 1):

            st.write(f"{i}. {insight}")

    

    # 9. 시각화 (기존 차트 표시)

    visualizations = analysis_data.get("visualizations", {})

    mobility_charts = visualizations.get("mobility_charts", [])

    

    if mobility_charts:

        st.markdown("---")

        st.markdown("#### 📊 이동 패턴 차트")

        

        cols = st.columns(2)

        for idx, chart_info in enumerate(mobility_charts[:6]):  # 최대 6개

            col_idx = idx % 2

            with cols[col_idx]:

                chart_path = chart_info.get("path")

                chart_name = chart_info.get("name", f"Chart {idx+1}")

                

                if chart_path and Path(chart_path).exists():

                    try:

                        st.image(chart_path, caption=chart_name, use_container_width=True)

                    except Exception as e:

                        st.error(f"차트 로딩 실패: {chart_name}")
                        st.caption(f"경로: {chart_path}")
                        st.caption(f"에러: {str(e)}")
                else:
                    st.warning(f"파일 없음: {chart_name}")
                    if chart_path:
                        st.caption(f"경로: {chart_path}")

    else:

        st.info("이동 패턴 차트가 없습니다.")



def display_panorama_analysis(analysis_data):

    """지역 분석 탭"""

    st.markdown("### 🏘️ 지역 분석 (파노라마)")

    

    panorama_data = analysis_data.get("panorama_analysis", {})

    if not panorama_data:

        st.info("파노라마 분석 데이터가 없습니다.")

        return
    
    # Get analysis directory for image loading
    analysis_dir_str = analysis_data.get("analysis_dir", "")
    panorama_images_dir = None
    if analysis_dir_str:
        panorama_images_dir = Path(analysis_dir_str) / "panorama" / "images"

    

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
    
    # panorama_analysis에서 직접 이미지 경로 추출
    panorama_images_list = []
    
    # 0. panorama/images 폴더에서 모든 이미지 파일 자동 로드
    if panorama_images_dir and panorama_images_dir.exists():
        image_files = sorted([f for f in panorama_images_dir.iterdir() 
                             if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']])
        for img_file in image_files[:10]:  # 최대 10개
            panorama_images_list.append({
                "path": str(img_file),
                "name": img_file.name
            })
    
    # 1. individual_analyses 배열에서 이미지 추출
    if "panorama_analysis" in analysis_data:
        panorama_data = analysis_data["panorama_analysis"]
        
        individual_analyses = panorama_data.get("individual_analyses", [])
        if isinstance(individual_analyses, list):
            for idx, analysis_item in enumerate(individual_analyses, 1):
                if isinstance(analysis_item, dict):
                    # 원본 이미지 경로 (JSON에서 가져옴)
                    original_img_path = analysis_item.get("image_path", "")
                    
                    # 이미지 파일명 추출 (확장자 포함)
                    img_filename = Path(original_img_path).name if original_img_path else None
                    
                    # panorama/images 폴더에서 동일한 파일명 찾기 (JPG, PNG 모두 지원)
                    if img_filename and panorama_images_dir:
                        # JPG로 시도
                        local_img_path_jpg = panorama_images_dir / img_filename
                        local_img_path_png = panorama_images_dir / f"{Path(img_filename).stem}.png"
                        local_img_path = None
                        
                        if local_img_path_jpg.exists():
                            local_img_path = local_img_path_jpg
                        elif local_img_path_png.exists():
                            local_img_path = local_img_path_png
                        
                        # 파일이 존재하면 사용
                        if local_img_path:
                            point_id = analysis_item.get("point_id", idx)
                            lon = analysis_item.get("lon", "N/A")
                            lat = analysis_item.get("lat", "N/A")
                            img_name = f"포인트 {point_id} (경도: {lon}, 위도: {lat})"
                            panorama_images_list.append({"path": str(local_img_path), "name": img_name})
                        else:
                            # 파일이 없으면 원본 경로 사용 시도
                            point_id = analysis_item.get("point_id", idx)
                            lon = analysis_item.get("lon", "N/A")
                            lat = analysis_item.get("lat", "N/A")
                            img_name = f"포인트 {point_id} (경도: {lon}, 위도: {lat})"
                            if original_img_path and Path(original_img_path).exists():
                                panorama_images_list.append({"path": original_img_path, "name": img_name})
    
    # 2. visualizations에서 이미지 추가
    visualizations = analysis_data.get("visualizations", {})
    panorama_images_from_viz = visualizations.get("panorama_images", [])
    
    if panorama_images_from_viz:
        panorama_images_list.extend(panorama_images_from_viz)
    
    # 이미지 표시
    if panorama_images_list:
        st.markdown("---")
        st.markdown("#### 📷 파노라마 이미지")
        cols = st.columns(2)
        
        for idx, img_info in enumerate(panorama_images_list[:6]):  # 최대 6개
            col_idx = idx % 2
            with cols[col_idx]:
                img_path = img_info.get("path") if isinstance(img_info, dict) else img_info
                img_name = img_info.get("name", f"Image {idx+1}") if isinstance(img_info, dict) else f"Image {idx+1}"
                
                if img_path:
                    try:
                        if Path(img_path).exists():
                            st.image(img_path, caption=img_name, use_container_width=True)
                        else:
                            # 절대 경로 변환 시도
                            absolute_path = Path(img_path).resolve()
                            if absolute_path.exists():
                                st.image(str(absolute_path), caption=img_name, use_container_width=True)
                            else:
                                st.write(f"이미지를 찾을 수 없습니다: {img_name}")
                    except Exception as e:
                        st.error(f"이미지 로딩 실패: {img_name} ({str(e)})")

    

    # 공간 분석 지도

    spatial_files = visualizations.get("spatial_files", [])

    if spatial_files:

        st.markdown("---")

        st.markdown("#### 🗺️ 공간 분석")

        for file_info in spatial_files:

            file_path = file_info.get("path")

            file_name = file_info.get("name", "Unknown")

            file_type = file_info.get("type", "unknown")

            

            if file_path and Path(file_path).exists():

                if file_type == "spatial_chart":
                    # PNG 차트는 이미지로 표시
                    try:
                        st.image(file_path, caption=file_name, use_container_width=True)
                    except Exception as e:
                        st.error(f"파일 로딩 실패: {file_name}")
                        
                elif file_type == "spatial_map" or file_type == "panorama_map":
                    # HTML 지도는 컴포넌트로 표시
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        
                        # HTML을 Streamlit 컴포넌트로 표시
                        import streamlit.components.v1 as components
                        components.html(html_content, height=600, scrolling=True)
                        st.caption(file_name)
                    except Exception as e:
                        st.error(f"지도 로딩 실패: {file_name} ({str(e)})")
                        st.write(f"**{file_name}:** [지도 파일]({file_path})")
                else:
                    st.write(f"**{file_name}:** {file_path}")

            else:
                st.write(f"파일 없음: {file_name}")

    




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

- 배달 비중: {store_summary.get('delivery_ratio', 'N/A')}



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

        # 상권명 사용 (spatial_matcher에서 이미 올바른 상권명으로 수정됨)
        corrected_marketplace_name = marketplace_analysis.get('상권명', 'N/A')
        
        md += f"""## 3. 상권 분석 (Marketplace Analysis)



### 기본 정보

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



# 사이드바: 분석 진행 상황 표시

with st.sidebar:

    st.markdown("## 📊 분석 진행 상황")

    

    # 환경 변수 설정 안내

    
    
    # 분석 상태 표시

    if st.session_state.get('is_analyzing', False):

        st.info("🔄 분석 진행 중...")

        

        # 진행 단계 표시 (접을 수 있는 형태)

        with st.expander("📋 현재 진행 단계", expanded=True):

            progress = st.session_state.get('analysis_progress', {})

            

            steps = [

                ("주소 정보 분석", "address"),

                ("Store Agent 분석", "store"),

                ("Marketing 분석", "marketing"),

                ("Mobility 분석", "mobility"),

                ("Panorama 분석", "panorama"),

                ("Marketplace 분석", "marketplace"),

                ("결과 통합", "integration")

            ]

            

            for i, (step_name, step_key) in enumerate(steps, 1):

                status = progress.get(step_key, "waiting")

                

                if status == "completed":

                    st.write(f"{i}. ✅ {step_name}")

                elif status == "in_progress":

                    st.write(f"{i}. 🔄 {step_name} 중...")

                else:

                    st.write(f"{i}. ⏳ {step_name} 대기")

            

    elif st.session_state.get('analysis_complete', False):

        st.success("✅ 분석 완료!")

        

        # 완료된 분석 정보

        with st.expander("📋 분석 결과 요약", expanded=True):

            store_code = st.session_state.get('store_code', 'N/A')

            st.write(f"**상점 코드:** {store_code}")

            st.write("**분석 완료 시간:** 방금 전")

            st.write("**분석 항목:** 5차원 종합 분석")

            st.write("**상태:** 모든 분석 완료")

            

    else:

        st.info("⏳ 대기 중...")

        

        # 대기 상태 안내

        with st.expander("📋 사용 방법", expanded=True):

            st.write("1. 상점 코드 입력")

            st.write("2. 분석 시작")

            st.write("3. 결과 확인")

            st.write("4. 상담 시작")

    

    # 새로고침 버튼

    if st.button("🔄 새로고침", use_container_width=True):

        st.rerun()



# 메인 2패널 레이아웃

col1, col2 = st.columns([1, 1])



# 왼쪽 패널: 채팅 인터페이스

with col1:

    st.markdown("## BigContest AI Agent - 1:1 비밀 상담 서비스")

    

    # 초기 환영 메시지

    if not st.session_state.messages:

        st.session_state.messages = [{

            "role": "assistant", 

            "content": "안녕하세요! 비밀 상담사 AI 시스템입니다. 10자리 상점 코드를 입력해주시면 초기 분석을 시작하겠습니다. (예: 000F03E44A, 002816BA73)"

        }]

    

    # 메시지 표시

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.write(message["content"])

    

    # 분석 중일 때 로딩 표시

    if st.session_state.is_analyzing:

        with st.chat_message("assistant"):

            st.markdown("🔄 초기 분석을 진행하겠습니다. 완료시 상담시작 버튼을 눌러주세요")

    

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

                    

                    # 분석 데이터 로드 성공 로그

                    print(f"[OK] 기존 분석 데이터 로드 성공: {len(existing_analysis)} 섹션")

                    

                    st.rerun()

                else:

                    st.session_state.messages.append({

                        "role": "assistant", 

                        "content": "분석을 시작합니다... 초기 분석을 진행하겠습니다. 약 1분 정도 소요됩니다. 이후 상담 시작 버튼을 눌러 분석을 완료해주세요요"

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

                        print(f"[INFO] 상담 질문 처리 중: {prompt[:50]}...")

                        # 상담에 필요한 데이터 전달
                        store_data = st.session_state.merged_data.get("store_analysis", {}) if st.session_state.merged_data else {}
                        panorama_data = st.session_state.merged_data.get("panorama_analysis", {}) if st.session_state.merged_data else {}
                        
                        response = chat_with_consultant(

                            st.session_state.consultation_chain,

                            st.session_state.consultation_memory,

                            prompt,
                            store_data,
                            panorama_data
                        )

                        print(f"[SUCCESS] 상담 답변 생성 완료")

                        st.session_state.messages.append({"role": "assistant", "content": response})

                    except Exception as e:

                        print(f"[ERROR] 상담 중 오류 발생: {str(e)}")

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

                

                log_capture.add_log(f"기존 분석 결과 확인 중: {store_code}", "INFO")

                existing_analysis = load_analysis_data_from_output(store_code)

                

                if existing_analysis:

                    log_capture.add_log(f"기존 분석 결과 발견: {store_code}", "SUCCESS")

                    st.session_state.messages.append({

                        "role": "assistant",

                        "content": f"✅ 상점 코드 {store_code}의 기존 분석 결과를 발견했습니다!"

                    })

                    st.session_state.analysis_data = existing_analysis

                    st.session_state.analysis_complete = True

                    st.session_state.is_analyzing = False

                    st.rerun()

                else:

                    log_capture.add_log(f"기존 분석 결과 없음, 새 분석 시작: {store_code}", "INFO")

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

            log_capture.add_log(f"분석 시작: {st.session_state.store_code}", "INFO")

            log_capture.add_log("5차원 종합 분석 진행 중...", "INFO")

            

            # 분석 진행 상황 초기화

            st.session_state.analysis_progress = {}

            

            # 분석 실행
            try:
                result = asyncio.run(run_full_analysis_pipeline(st.session_state.store_code))
                print(f"[DEBUG] run_full_analysis_pipeline 결과: {result}")
                
                
            except Exception as e:
                print(f"[ERROR] run_full_analysis_pipeline 실행 오류: {e}")
                import traceback
                traceback.print_exc()
                result = {"status": "failed", "error": str(e)}

            

            # Marketing Module은 상담 시작 단계에서 실행되도록 이동
            

            # 분석 완료 후 결과 로드

            if result and result.get("status") == "success":

                log_capture.add_log(f"분석 완료: {st.session_state.store_code}", "SUCCESS")

                st.session_state.is_analyzing = False

                st.session_state.analysis_complete = True

                

                # 실제 output 폴더에서 최신 결과 로드

                analysis_data = load_analysis_data_from_output(st.session_state.store_code)

                if analysis_data:

                    st.session_state.analysis_data = analysis_data

                    log_capture.add_log("분석 데이터 로드 성공", "OK")

                else:

                    st.session_state.analysis_data = result

                    log_capture.add_log("기본 마케팅 결과 사용", "WARN")

                

                # 모든 분석 결과를 하나의 파일로 통합 (JSON + MD)

                log_capture.add_log("분석 결과 통합 중...", "INFO")

                merged_json, merged_md = merge_all_analysis_files(st.session_state.analysis_data)

                if merged_json and merged_md:

                    log_capture.add_log(f"통합 분석 파일 생성됨: JSON={merged_json}, MD={merged_md}", "OK")

                

                # 완료 메시지 추가

                st.session_state.messages.append({

                    "role": "assistant",

                    "content": "분석 완료! 우측 패널에서 상세 분석 결과를 확인하실 수 있습니다. 궁금하신 점이 있으시면 언제든 질문해주세요!"

                })

                

                # 분석 완료 후 즉시 결과 표시

                st.success("✅ 분석이 완료되었습니다!")

                st.rerun()

                

                # 최종 리포트 생성 버튼 표시

                #if st.button("📋 최종 리포트 생성 (Gemini)", type="primary"):

                 #   with st.spinner("Gemini로 최종 리포트를 생성 중..."):

                  #      md_content, json_content = generate_final_report_with_gemini(result)

                   #     if md_content:

#                            report_dir = save_final_reports(st.session_state.store_code, md_content, json_content)

 #                           if report_dir:

  #                              st.success(f"최종 리포트가 생성되었습니다: {report_dir}")

#                                st.session_state.final_report_generated = True

 #                               st.rerun()

  #                      else:

   #                         st.error("최종 리포트 생성에 실패했습니다.")

                

                st.rerun()

            else:

                log_capture.add_log(f"분석 실패: {st.session_state.store_code}", "ERROR")

                st.error("분석 실패")

                st.session_state.is_analyzing = False

                st.rerun()

                

        except Exception as e:

            log_capture.add_log(f"분석 중 오류 발생: {str(e)}", "ERROR")

            st.error(f"분석 실패: {str(e)}")

            st.session_state.is_analyzing = False

            st.rerun()

    

    # 분석 완료 후 결과 표시

    elif st.session_state.analysis_complete and st.session_state.analysis_data:

        # session_state에 저장된 분석 데이터 사용

        store_code = st.session_state.store_code

        analysis_data = st.session_state.analysis_data

        

        if not analysis_data:

            st.error("분석 데이터를 로드할 수 없습니다.")

        else:

            st.success(f"✅ 분석 완료! ({analysis_data.get('timestamp', 'N/A')})")

            

            # 기본 정보 표시

            display_basic_info(analysis_data)

            

            # 최종 리포트 생성 버튼

           # display_final_report_button(store_code, analysis_data)

            

            # 상담 시작 버튼

            st.markdown("---")

            if not st.session_state.consultation_mode:

                if st.button("💬 상담 시작 (분석 3~5분 소요)", type="primary", use_container_width=True):
                    print(f"[INFO] 상담 모드 시작 요청: {store_code}")

                    if AGENTS_AVAILABLE:

                        print(f"[INFO] Langchain AI Agents 사용하여 상담 시스템 준비 중...")

                        with st.spinner("파노라마 분석 → 마케팅 전략 → MCP 검색 → 크롤링 → 상담 시스템 준비 중..."):
                            try:
                                # 1. 파노라마 분석 먼저 실행
                                log_capture.add_log("파노라마 분석 시작...", "INFO")
                                try:
                                    from agents_new.panorama_img_anal.analyze_area_by_address import analyze_area_by_address
                                    
                                    # 주소 가져오기
                                    address = None
                                    if "store_analysis" in analysis_data and "store_overview" in analysis_data["store_analysis"]:
                                        address = analysis_data["store_analysis"]["store_overview"].get("address")
                                    
                                    if not address:
                                        log_capture.add_log("❌ 매장 주소 없음", "ERROR")
                                        analysis_data["panorama_analysis"] = {"error": "매장 주소 없음"}
                                        raise Exception("매장 주소 없음")    
                                    # 파노라마 분석 실행
                                    panorama_result = analyze_area_by_address(
                                        address=address,
                                        buffer_meters=300,
                                        max_images=6,
                                        create_map=True
                                    )
                                    
                                    # 결과를 analysis_data에 저장
                                    analysis_data["panorama_analysis"] = panorama_result
                                    log_capture.add_log(f"파노라마 분석 완료: {panorama_result.get('output_folder', 'N/A')}", "OK")
                                    
                                except Exception as e:
                                    log_capture.add_log(f"파노라마 분석 오류: {e}", "ERROR")
                                    analysis_data["panorama_analysis"] = {"error": str(e)}

                                # 2. 통합 분석 파일 로드
                                log_capture.add_log("통합 분석 파일 로드 중...", "INFO")
                                merged_data, merged_md = load_merged_analysis(analysis_data["analysis_dir"])

                                

                                if merged_data and merged_md:

                                    log_capture.add_log("통합 파일 로드 완료", "OK")

                                    log_capture.add_log(f"Analysis Dir: {analysis_data['analysis_dir']}", "DEBUG")

                                    log_capture.add_log(f"MD 파일 크기: {len(merged_md)} bytes", "DEBUG")

                                    

                                    # ===== 1단계: Marketing Module 실행 =====
                                    print("\n" + "="*60)

                                    print("[1/3] Marketing Module 실행!")
                                    print("="*60)

                                    
                                    # Marketing Module 결과가 이미 있는지 확인
                                    marketing_file = Path(analysis_data.get("analysis_dir", "")) / "marketing_result.json"
                                    if marketing_file.exists():
                                        print(f"[INFO] Marketing result already exists: {marketing_file.name}")
                                        log_capture.add_log(f"✅ Marketing Module 결과 이미 존재: {marketing_file.name}", "INFO")
                                        
                                        # 기존 결과 로드
                                        with open(marketing_file, 'r', encoding='utf-8') as f:
                                            marketing_result = json.load(f)
                                        analysis_data["marketing_analysis"] = marketing_result
                                        
                                        # 프론트엔드 표시를 위해 marketing_result도 설정
                                        analysis_data["marketing_result"] = marketing_result
                                        
                                        # 기존 마케팅 결과에 대해서도 Google Maps 연동 수행
                                        try:
                                            log_capture.add_log("🔄 기존 마케팅 결과에 대한 Google Maps 자동 연동 시작...", "INFO")
                                            from agents_new.google_map_mcp.auto_integration import auto_marketing_google_maps_integration
                                            
                                            integration_result = auto_marketing_google_maps_integration(
                                                store_code=store_code,
                                                marketing_result=marketing_result,
                                                output_dir=analysis_data.get("analysis_dir", "")
                                            )
                                            
                                            if integration_result.get("integration_status") == "success":
                                                analysis_data["marketing_google_maps_integration"] = integration_result
                                                log_capture.add_log("✅ Google Maps 자동 연동 완료!", "SUCCESS")
                                                log_capture.add_log(f"📄 통합 결과 파일: {integration_result.get('output_file', 'N/A')}", "INFO")
                                            else:
                                                log_capture.add_log(f"⚠️ Google Maps 자동 연동 실패: {integration_result.get('error', 'N/A')}", "WARN")
                                                
                                        except Exception as e:
                                            log_capture.add_log(f"❌ Google Maps 자동 연동 오류: {str(e)}", "ERROR")
                                    else:
                                        try:
                                            log_capture.add_log("[1/3] Marketing Module 분석 시작...", "INFO")
                                            
                                            # Store analysis에서 marketing format으로 변환
                                            store_analysis = analysis_data.get("store_analysis")
                                            if store_analysis:
                                                # Marketing Module 실행 (JSON 2개 자동 저장)
                                                if MARKETING_MODULE_AVAILABLE:
                                                    marketing_result = run_marketing_sync(
                                                        store_code, 
                                                        analysis_data.get("analysis_dir", ""), 
                                                        store_analysis
                                                    )
                                                else:
                                                    log_capture.add_log("Marketing Module을 사용할 수 없습니다 - GEMINI_API_KEY 또는 GOOGLE_API_KEY 환경 변수를 설정해주세요", "WARN")
                                                    log_capture.add_log("기본 마케팅 결과를 생성합니다...", "INFO")
                                                    marketing_result = None
                                                
                                                if marketing_result:
                                                    analysis_data["marketing_analysis"] = marketing_result
                                                    analysis_data["marketing_result"] = marketing_result
                                                    log_capture.add_log("✅ Marketing Module 완료!", "SUCCESS")
                                                    
                                                    # 마케팅 분석 후 Google Maps 자동 연동
                                                    try:
                                                        log_capture.add_log("🔄 Google Maps 자동 연동 시작...", "INFO")
                                                        from agents_new.google_map_mcp.auto_integration import auto_marketing_google_maps_integration
                                                        
                                                        integration_result = auto_marketing_google_maps_integration(
                                                            store_code=store_code,
                                                            marketing_result=marketing_result,
                                                            output_dir=analysis_data.get("analysis_dir", "")
                                                        )
                                                        
                                                        if integration_result.get("integration_status") == "success":
                                                            analysis_data["marketing_google_maps_integration"] = integration_result
                                                            log_capture.add_log("✅ Google Maps 자동 연동 완료!", "SUCCESS")
                                                            log_capture.add_log(f"📄 통합 결과 파일: {integration_result.get('output_file', 'N/A')}", "INFO")
                                                        else:
                                                            log_capture.add_log(f"⚠️ Google Maps 자동 연동 실패: {integration_result.get('error', 'N/A')}", "WARN")
                                                            
                                                    except Exception as e:
                                                        log_capture.add_log(f"❌ Google Maps 자동 연동 오류: {str(e)}", "ERROR")
                                                else:
                                                    log_capture.add_log("Marketing Module 실패", "WARN")
                                            else:
                                                log_capture.add_log("Store 분석 없음", "WARN")
                                        except Exception as e:
                                            log_capture.add_log(f"❌ Marketing Module 오류: {str(e)}", "ERROR")
                                            import traceback
                                            traceback.print_exc()
                                    
                                    # ===== 2단계: MCP 매장 검색 실행 =====
                                    print("\n" + "="*60)
                                    print("[2/3] MCP 매장 검색 실행!")
                                    print("="*60)
                                    try:
                                        log_capture.add_log(f"[2/3] MCP 매장 검색 시작: {store_code}", "INFO")
                                        print(f"🔍 MCP 검색 중: {store_code}")
                                        
                                        if MCP_LOOKUP_AVAILABLE:
                                            # CSV 경로: agents_new/google_map_mcp/matched_store_results.csv
                                            csv_path = Path(__file__).parent.parent.parent / "agents_new" / "google_map_mcp" / "matched_store_results.csv"

                                            if csv_path.exists():
                                                # 출력 경로: 현재 분석 디렉토리 우선 사용
                                                out_dir = Path(analysis_data.get("analysis_dir") or (Path(__file__).parent.parent / "output"))
                                                out_dir.mkdir(parents=True, exist_ok=True)

                                                # MCP 서버 URL 설정 (환경 변수 또는 기본값)
                                                mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000")
                                                
                                                mcp_result = run_gm_lookup(
                                                    store_code,
                                                    csv_path=str(csv_path),
                                                    out_dir=str(out_dir),
                                                    force=False,
                                                    dry_run=False,
                                                    mcp_server_url=mcp_server_url
                                                )

                                                output_file = mcp_result.get("output_path", "")
                                                if output_file and Path(output_file).exists():
                                                    print(f"✅ MCP 검색 성공! 저장: {Path(output_file).name}")
                                                    log_capture.add_log(f"✅ MCP 매장 검색 성공: {Path(output_file).name}", "SUCCESS")
                                                else:
                                                    log_capture.add_log("⚠️ MCP 검색은 수행되었으나 출력 파일 확인 실패", "WARNING")

                                                # 결과 저장 (성공/실패 관계없이 세부 내용 유지)
                                                analysis_data["mcp_search_result"] = mcp_result
                                            else:
                                                log_capture.add_log(f"⚠️ MCP CSV 파일 없음: {csv_path}", "WARNING")
                                        else:
                                            log_capture.add_log("MCP Lookup 모듈을 사용할 수 없습니다 - 환경변수 또는 의존성 확인", "WARN")

                                    except Exception as e:
                                        log_capture.add_log(f"❌ MCP 매장 검색 오류: {e}", "ERROR")
                                        import traceback
                                        traceback.print_exc()

                                    

                        
                                    # 라인 4465-4480 부분을 완전히 교체

 
                                    # ===== 3단계: New Product Agent 실행 =====
                                    print("\n" + "="*60)
                                    print("[3/3] New Product Agent 실행 (JSON 캐시 사용)")
                                    print("="*60)
                                    

# New Product Agent 실행
                                    if NEW_PRODUCT_AGENT_AVAILABLE:
                                        try:
                                            log_capture.add_log("[3/3] New Product Agent 실행 중...", "INFO")
                                            
                                            # StoreAgent 리포트 가져오기
                                            store_report = None
                                            
                                            if "store_analysis" in analysis_data and analysis_data["store_analysis"]:
                                                store_report = analysis_data["store_analysis"]
                                                log_capture.add_log(f"✅ StoreAgent 리포트 로드: {len(str(store_report))} bytes", "INFO")
                                            elif "store_analysis_report" in analysis_data:
                                                store_report = analysis_data["store_analysis_report"]
                                                log_capture.add_log(f"✅ StoreAgent 리포트 로드 (alt key): {len(str(store_report))} bytes", "INFO")
                                            else:
                                                log_capture.add_log("⚠️ StoreAgent 리포트 없음, NewProductAgent 스킵", "WARNING")



                                            
                                            # StoreAgent 리포트가 있으면 Agent 실행
                                            
                                           
                                            if store_report:
                                                # 절대 경로로 캐시 파일 경로 생성
                                                import os
                                                current_file = Path(__file__)
                                                # 경로 설정
                                                project_root = current_file.parent.parent.parent  # 프로젝트 루트
                                                open_sdk_dir = current_file.parent.parent  # open_sdk
                                                
                                                # keywords_20251026.json 절대 경로 (프로젝트 루트 기준)
                                                cache_path = project_root / "agents_new" / "new_product_agent" / "keywords_20251026.json"
                                                
                                                # output 디렉토리 절대 경로 (open_sdk 기준) - ✅ 수정
                                                output_dir = open_sdk_dir / "output"  # open_sdk/output
                                                
                                                print(f"[DEBUG] Cache path: {cache_path}")
                                                print(f"[DEBUG] Cache exists: {cache_path.exists()}")
                                                print(f"[DEBUG] Output dir: {output_dir}")
                                                
                                                # JSON 캐시 모드로 Agent 초기화
                                                agent = NewProductAgent(
                                                    use_cache=True,  # JSON 캐시 사용
                                                    save_outputs=True,
                                                    output_dir=str(output_dir),  # open_sdk/output 사용
                                                    cache_json_path=str(cache_path)  # 캐시 파일 절대 경로 전달
                                                )
                                                
                                                # Agent 실행 (비동기)
                                                new_product_result = asyncio.run(agent.run(store_report))
                                                analysis_data["new_product_result"] = new_product_result
                                                log_capture.add_log("✅ New Product Agent 완료", "SUCCESS")
                                            else:
                                                new_product_result = {"activated": False, "reason": "StoreAgent 리포트 없음"}
                                                analysis_data["new_product_result"] = new_product_result
                                        
                                        except Exception as e:
                                            log_capture.add_log(f"❌ New Product Agent 실행 실패: {e}", "ERROR")
                                            analysis_data["new_product_result"] = {"activated": False, "error": str(e)}
                                            import traceback
                                            traceback.print_exc()
                                    else:
                                        log_capture.add_log("⚠️ NewProductAgent를 사용할 수 없음", "WARNING")
                                        new_product_result = {"activated": False, "reason": "Agent not available"}
                                        analysis_data["new_product_result"] = new_product_result
                                        
                                    
    

                                    # ===== 4단계: Langchain Consultation Chain 생성 =====
                                    # Langchain Consultation Chain 생성

                                    log_capture.add_log("Langchain Consultation Chain 생성 중...", "INFO")

                                    

                                    # MCP 검색 결과 txt 파일 읽기 (있으면)

                                    mcp_content = ""

                                    if "mcp_search_result" in analysis_data:
                                        mcp_file = analysis_data["mcp_search_result"].get("output_path") or analysis_data["mcp_search_result"].get("file")
                                        if mcp_file and Path(mcp_file).exists():

                                            try:

                                                with open(mcp_file, 'r', encoding='utf-8') as f:

                                                    mcp_content = f.read()

                                                log_capture.add_log(f"MCP 검색 결과 로드 완료: {len(mcp_content)} bytes", "DEBUG")

                                            except Exception as e:

                                                log_capture.add_log(f"MCP 파일 읽기 실패: {e}", "WARNING")

                                    

                                    chain, memory = create_consultation_chain(store_code, merged_data, merged_md, mcp_content)

                                    

                                    if chain and memory:

                                        log_capture.add_log("상담 체인 생성 완료", "SUCCESS")

                                        st.session_state.consultation_chain = chain

                                        st.session_state.consultation_memory = memory

                                        st.session_state.merged_data = merged_data

                                        st.session_state.merged_md = merged_md

                                        st.session_state.consultation_mode = True

                                        

                                        st.session_state.messages.append({

                                            "role": "assistant",

                                            "content": "✅ 상담 준비 완료! 마케팅 전략, MCP 검색, 크롤링 결과를 바탕으로 무엇이든 물어보세요. 📊"
                                        })

                                        st.success("✅ 상담 모드가 활성화되었습니다!")

                                        st.rerun()

                                    else:

                                        log_capture.add_log("상담 체인 생성 실패", "ERROR")

                                        st.error("상담 체인 생성에 실패했습니다.")

                                else:

                                    log_capture.add_log("통합 파일을 찾을 수 없습니다.", "ERROR")

                                    st.error(f"통합 파일을 찾을 수 없습니다.")

                            except Exception as e:

                                log_capture.add_log(f"상담 시스템 초기화 실패: {e}", "ERROR")

                                st.error(f"상담 시스템 초기화 실패: {e}")

                                import traceback

                                traceback.print_exc()

                    else:

                        log_capture.add_log("AI Agents가 로드되지 않았습니다. 기본 모드로 진행합니다.", "WARN")

                        st.warning("AI Agents가 로드되지 않았습니다. 기본 모드로 진행합니다.")

            else:

                st.info("✅ 상담 모드 활성화됨 - 자유롭게 질문하세요!")

            

            # 대화 초기화 버튼 추가

            col1, col2, col3 = st.columns([1, 1, 1])

            with col2:

                if st.button("🔄 대화 초기화", type="secondary", help="새로운 상점 코드로 분석을 시작합니다"):

                    # 세션 상태 초기화

                    for key in list(st.session_state.keys()):

                        if key not in ["log_data", "analysis_progress"]:

                            del st.session_state[key]

                    st.rerun()

            

            # 탭으로 상세 결과 표시 (시각화 탭 제거)

            tab1, tab2, tab3, tab4, tab5, tab6, tab7= st.tabs([

                "개요", "고객 분석", "이동 패턴", "지역 분석", "상권 분석", "마케팅", "신메뉴 추천"

            ])

            


            with tab1:
                display_store_overview(analysis_data)
                
                # JSON 다운로드 섹션 추가
                st.markdown("---")
                with st.expander("    📥 참고 데이터 다운로드 및 확인", expanded=True):
                    st.markdown("### 📊 이 탭에서 참고한 데이터")
                    
                    json_files = [
                        ("전체 분석 결과", "analysis_result.json", "모든 분석 결과를 통합한 종합 리포트"),
                        ("종합 분석 요약", "comprehensive_analysis.json", "각 분석의 핵심 요약 및 평가 점수"),
                        ("매장 분석 리포트", "store_analysis_report.json", "매장의 고객 분포, 매출 트렌드, 재방문율 분석"),
                        ("통합 분석 리포트", "merged_analysis_full.json", "AI 상담에서 참고하는 전체 데이터")
                    ]
                    
                    for name, file, desc in json_files:
                        file_path = Path(analysis_data.get("analysis_dir", "")) / file
                        if file_path.exists():
                            with open(file_path, 'r', encoding='utf-8') as f:
                                json_data = f.read()
                            
                            import json as json_lib
                            json_obj = json_lib.loads(json_data)
                            
                            st.markdown(f"**📄 {name}**")
                            st.caption(desc)
                            
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.download_button(
                                    label=f"📥 다운로드",
                                    data=json_data,
                                    file_name=file,
                                    mime="application/json",
                                    key=f"download_tab1_{file}",
                                    use_container_width=True
                                )
                            with col2:
                                # expander 중첩 방지를 위해 버튼으로 변경
                                if st.button(f"📄 {file} 미리보기", key=f"preview_tab1_{file}"):
                                    st.json(json_obj)
                            st.divider()

            with tab2:
                display_customer_analysis(analysis_data)
                
                # 고객 분석 JSON 다운로드
                st.markdown("---")
                with st.expander("            📥 참고 데이터 다운로드 및 확인", expanded=True):
                    st.markdown("### 📊 이 탭에서 참고한 데이터")
                    
                    file_path = Path(analysis_data.get("analysis_dir", "")) / "store_analysis_report.json"
                    if file_path.exists():
                        with open(file_path, 'r', encoding='utf-8') as f:
                            json_data = f.read()
                        
                        import json as json_lib
                        json_obj = json_lib.loads(json_data)
                        
                        st.markdown("**📄 매장 분석 리포트**")
                        st.caption("고객 분포, 연령/성별 분석, 재방문율, 고객 타입별 분석 데이터")
                        
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.download_button(
                                label="📥 다운로드",
                                data=json_data,
                                file_name="store_analysis_report.json",
                                mime="application/json",
                                key="download_tab2_store",
                                use_container_width=True
                            )
                        with col2:
                            # expander 중첩 방지를 위해 버튼으로 변경
                            if st.button("📄 store_analysis_report.json 미리보기", key="preview_tab2_store"):
                                st.json(json_obj)

            with tab3:
                display_mobility_analysis(analysis_data)
                
                # 이동 패턴 JSON 다운로드


            with tab4:
                display_panorama_analysis(analysis_data)
                
                # 파노라마 분석 JSON 다운로드
                st.markdown("---")
                with st.expander("     📥 참고 데이터 다운로드 및 확인", expanded=True):
                    st.markdown("### 📊 이 탭에서 참고한 데이터")
                    
                    if "panorama_analysis" in analysis_data and analysis_data.get("panorama_analysis"):
                        import json as json_lib
                        json_obj = analysis_data["panorama_analysis"]
                        json_data = json_lib.dumps(json_obj, ensure_ascii=False, indent=2)
                        
                        st.markdown("**📄 파노라마 분석 데이터**")
                        st.caption("주변 지역 특성, 상권 환경, 상업적 특성 분석 (스트리트뷰 이미지 기반)")
                        
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.download_button(
                                label="📥 다운로드",
                                data=json_data,
                                file_name="panorama_analysis.json",
                                mime="application/json",
                                key="download_tab4_panorama",
                                use_container_width=True
                            )
                        with col2:
                            # expander 중첩 방지를 위해 버튼으로 변경
                            if st.button("📄 panorama_analysis.json 미리보기", key="preview_tab4_panorama"):
                                st.json(json_obj)

            
            with tab5:
                st.markdown("#### 🏪 상권 분석(서울시 상권분석 서비스 데이터 크롤링)")
                if "marketplace_analysis" in analysis_data:
                    marketplace_data = analysis_data["marketplace_analysis"]
                    
                    if isinstance(marketplace_data, dict):
                        # 기본 정보
                        st.markdown("##### 📋 기본 정보")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("상권명", marketplace_data.get( "N/A"))
                        with col2:
                            st.metric("총 페이지", marketplace_data.get("총_페이지", "N/A"))
                        with col3:
                            st.metric("추출 페이지", marketplace_data.get("추출_페이지", "N/A"))
                        with col4:
                            analysis_date = marketplace_data.get("분석일시", "N/A")
                            if analysis_date and isinstance(analysis_date, str):
                                analysis_date = analysis_date.split("T")[0] if "T" in analysis_date else analysis_date
                            st.metric("분석일시", analysis_date)
                        
                        # 데이터 배열 처리
                        if "데이터" in marketplace_data and isinstance(marketplace_data["데이터"], list):
                            # 표지를 제외한 데이터만 필터링
                            for page_item in marketplace_data["데이터"]:
                                item_type = page_item.get("유형", "")
                                
                                # 표지 제외
                                if item_type == "표지":
                                    continue
                                
                                st.markdown("---")
                                
                                # 페이지 정보
                                page_num = page_item.get("페이지", "?")
                                title = page_item.get("제목", "")
                                
                                # 페이지 제목
                                if title:
                                    st.markdown(f"### 📄 페이지 {page_num}: {title}")
                                else:
                                    st.markdown(f"### 📄 페이지 {page_num}")
                                
                                # 설명이 있으면 표시
                                if "설명" in page_item and page_item["설명"]:
                                    st.markdown("**💬 설명**")
                                    for desc in page_item["설명"]:
                                        st.write(f"- {desc}")
                                
                                # 비교 정보가 있으면 테이블로 표시
                                if "비교" in page_item and page_item["비교"]:
                                    st.markdown("**📊 비교 정보**")
                                    comp_data = []
                                    for comp in page_item["비교"]:
                                        comp_data.append({
                                            "기준": comp.get("기준", ""),
                                            "변화": f"{comp.get('변화', '')} {comp.get('단위', '')}"
                                        })
                                    st.table(pd.DataFrame(comp_data))
                                
                                # 점포수 정보
                                if "점포수" in page_item and isinstance(page_item["점포수"], dict):
                                    store_info = page_item["점포수"]
                                    if "값" in store_info:
                                        st.metric("점포수", f"{store_info['값']:,}{store_info.get('단위', '개')}")
                                
                                # 폐업수 정보
                                if "페업수" in page_item and isinstance(page_item["페업수"], dict):
                                    close_info = page_item["페업수"]
                                    if "값" in close_info:
                                        st.metric("폐업수", f"{close_info.get('값', 0):,}{close_info.get('단위', '개')}")
                    else:
                        st.json(marketplace_data)
                else:
                    st.info("상권 분석 데이터가 없습니다.")
            with tab6:
                st.markdown("#### 📈 마케팅 분석")
                if "marketing_analysis" in analysis_data:
                    marketing_data = analysis_data["marketing_analysis"]
                    
                    # formatted_output이 있으면 먼저 표시하고 계속 진행
                    if isinstance(marketing_data, dict) and "formatted_output" in marketing_data and marketing_data.get("formatted_output"):
                        st.markdown(marketing_data["formatted_output"])
                        st.markdown("---")
                        st.markdown("## 📊 상세 분석 데이터")
                    
                    # 구조화된 데이터를 파싱하여 표시
                    if isinstance(marketing_data, dict):
                        
                        # ========== 1. 위험 진단 (Risk Diagnosis) ==========// ... existing code (lines 4895)
                      # ========== 1. 위험 진단 (Risk Diagnosis) - persona_analysis.core_insights.risk_diagnosis 우선 사용 ==========
                        # 먼저 persona_analysis.core_insights.risk_diagnosis에서 가져오기 시도
                        risk_data = None
                        # ========== 1. 위험 진단 (Risk Diagnosis) - persona_analysis.core_insights.risk_diagnosis 사용 ==========
                        if "persona_analysis" in marketing_data and isinstance(marketing_data.get("persona_analysis"), dict):
                            persona = marketing_data["persona_analysis"]
                            if "core_insights" in persona and isinstance(persona.get("core_insights"), dict):
                                if "risk_diagnosis" in persona["core_insights"]:
                                    risk_data = persona["core_insights"]["risk_diagnosis"]
                                    
                                    try:
                                        st.markdown("### ▲ 위험 진단 (Risk Diagnosis)")
                                        
                                        # 전체 위험 수준
                                        risk_level = risk_data.get('overall_risk_level', 'N/A')
                                        risk_emoji = "🔴" if risk_level in ["위험", "높음"] else "🟡" if risk_level == "보통" else "🟢"
                                        st.markdown(f"**전체 위험 수준:** {risk_emoji} **{risk_level}**")
                                        
                                        # 위험 요소 개수 표시
                                        if "table_data" in risk_data and risk_data.get("table_data"):
                                            table_data = risk_data["table_data"]
                                            if isinstance(table_data, list) and len(table_data) > 0:
                                                risk_codes = [r.get('code', '') for r in table_data if isinstance(r, dict) and r.get('code')]
                                                st.write(f"이 매장에서 파악된 위험 요소는 {', '.join(risk_codes)}로 {len(risk_codes)}개의 요소가 있습니다.")
                                        
                                        st.markdown("---")
                                        st.markdown("### ■ 위험 요소 상세 (Detailed Risk Factors)")
                                        
                                        # table_data 구조
                                        if "table_data" in risk_data and isinstance(risk_data.get("table_data"), list) and len(risk_data["table_data"]) > 0:
                                            table_data = risk_data["table_data"]
                                            # 테이블 헤더
                                            cols = st.columns([1, 3, 2, 2, 2])
                                            with cols[0]:
                                                st.markdown("**코드**")
                                            with cols[1]:
                                                st.markdown("**의미**")
                                            with cols[2]:
                                                st.markdown("**수준**")
                                            with cols[3]:
                                                st.markdown("**점수**")
                                            with cols[4]:
                                                st.markdown("**우선순위**")
                                            
                                            st.divider()
                                            
                                            # 테이블 데이터
                                            for idx, risk_item in enumerate(table_data):
                                                if isinstance(risk_item, dict):
                                                    cols = st.columns([1, 3, 2, 2, 2])
                                                    with cols[0]:
                                                        st.write(risk_item.get('code', 'N/A'))
                                                    with cols[1]:
                                                        st.write(risk_item.get('meaning', risk_item.get('name', 'N/A')))  # 'meaning' 우선 사용
                                                    with cols[2]:
                                                        st.write(risk_item.get('level', 'N/A'))
                                                    with cols[3]:
                                                        st.write(risk_item.get('score', 'N/A'))
                                                    with cols[4]:
                                                        st.write(risk_item.get('priority', 'N/A'))
                                                    
                                                    # description과 evidence를 표 아래에 추가로 표시
                                                    if idx == 0:
                                                        st.markdown("---")
                                                    
                                                    if risk_item.get('description') or risk_item.get('evidence'):
                                                        with st.expander(f"**{risk_item.get('code', 'N/A')} 상세 정보**", expanded=True):
                                                            if risk_item.get('description'):
                                                                st.write(f"**설명:** {risk_item.get('description')}")
                                                            if risk_item.get('evidence'):
                                                                st.write(f"**근거:** {risk_item.get('evidence')}")
                                                            if risk_item.get('chart_type'):
                                                                st.caption(f"📊 차트: {risk_item.get('chart_title', 'N/A')} - {risk_item.get('chart_description', 'N/A')}")
                                                    
                                                    if idx < len(table_data) - 1:
                                                        st.divider()
                                            
                                            # 요약 및 상세 분석 (토글로 표시)
                                            st.markdown("---")
                                            if "summary" in risk_data:
                                                with st.expander("                   위험 분석 요약", expanded=True):
                                                    st.write(risk_data['summary'])
                                            
                                            # detailed_analysis가 있으면 표시
                                            if "detailed_analysis" in risk_data:
                                                with st.expander("                 위험 요소 상세 분석", expanded=True):
                                                    st.write(risk_data['detailed_analysis'])
                                    except Exception as e:
                                        st.error(f"위험 진단 로드 오류: {str(e)}")
                        
                        # ========== 2. 요약 인사이트 (Overall Conclusion) ==========
                        if "persona_analysis" in marketing_data and marketing_data.get("persona_analysis"):
                            try:
                                persona = marketing_data["persona_analysis"]
                                
                                if "core_insights" in persona and "persona" in persona["core_insights"]:
                                    insights = persona["core_insights"]["persona"]
                                    
                                    st.markdown("---")
                                    st.markdown("### ■ 요약 인사이트")
                                    
                                    # Summary 표시
                                    if "summary" in insights:
                                        st.write(insights["summary"])
                                    
                            except Exception as e:
                                st.error(f"종합 결론 로드 오류: {str(e)}")
                    
                        
                        # ========== 7. 다음 단계 제안 (Next Step Proposals) ==========
                        if "recommendations" in marketing_data and marketing_data.get("recommendations"):
                            try:
                                st.markdown("---")
                                st.markdown("### ■ 다음 단계 제안 (Next Step Proposals)")
                                rec = marketing_data["recommendations"]
                                
                                if isinstance(rec, dict):
                                    if "immediate_actions" in rec and rec.get("immediate_actions"):
                                        for i, action in enumerate(rec["immediate_actions"], 1):
                                            if action:
                                                st.write(f"**{i}. {action}**")
                                    
                                    if "short_term_goals" in rec and rec.get("short_term_goals"):
                                        st.markdown("---")
                                        st.markdown("**단기 목표:**")
                                        for goal in rec["short_term_goals"]:
                                            if goal:
                                                st.write(f"  - {goal}")
                                    
                                    if "long_term_strategy" in rec and rec.get("long_term_strategy"):
                                        st.markdown("---")
                                        st.markdown("**장기 전략:**")
                                        for strategy in rec["long_term_strategy"]:
                                            if strategy:
                                                st.write(f"  - {strategy}")
                            except Exception as e:
                                st.error(f"다음 단계 제안 로드 오류: {e}")
                        
                        # ========== 8. SNS 콘텐츠 (옵션) ==========
                        if "social_content" in marketing_data and marketing_data.get("social_content"):
                            try:
                                with st.expander("                            📱 SNS 콘텐츠 및 프로모션 텍스트", expanded=True):
                                    social = marketing_data["social_content"]
                                    
                                    if "instagram_posts" in social and social.get("instagram_posts"):
                                        st.markdown("**📸 인스타그램 포스트:**")
                                        for i, post in enumerate(social["instagram_posts"], 1):
                                            if isinstance(post, dict):
                                                st.markdown(f"**포스트 {i}:** {post.get('title', 'N/A')}")
                                                st.write(post.get('content', 'N/A'))
                                                if post.get('hashtags'):
                                                    st.caption(f"해시태그: {', '.join(post.get('hashtags', [])[:5])}")
                                                st.divider()
                                    
                                    if "facebook_posts" in social and social.get("facebook_posts"):
                                        st.markdown("**👥 페이스북 포스트:**")
                                        for i, post in enumerate(social["facebook_posts"], 1):
                                            if isinstance(post, dict):
                                                st.markdown(f"**포스트 {i}:** {post.get('title', 'N/A')}")
                                                st.write(post.get('content', 'N/A'))
                                                if post.get('call_to_action'):
                                                    st.caption(f"CTA: {post.get('call_to_action')}")
                                                st.divider()
                                    
                                    if "promotion_texts" in social and social.get("promotion_texts"):
                                        st.markdown("**📧 프로모션 텍스트:**")
                                        for promo in social["promotion_texts"]:
                                            if isinstance(promo, dict):
                                                st.markdown(f"**{promo.get('type', 'N/A')}:**")
                                                st.write(f"제목: {promo.get('title', 'N/A')}")
                                                st.write(f"내용: {promo.get('content', 'N/A')}")
                                                if promo.get('discount'):
                                                    st.caption(f"할인: {promo.get('discount')}")
                                                st.divider()
                            except Exception as e:
                                st.error(f"SNS 콘텐츠 로드 오류: {e}")
                        
                        # ========== 9. 전체 JSON 데이터 (백업) ==========
                        with st.expander("📄 전체 마케팅 데이터 (JSON 원본)", expanded=False):
                            st.json(marketing_data)
                    else:
                        st.json(marketing_data)
                else:
                    st.info("마케팅 분석 데이터가 없습니다.")

               
                with tab7:
                    st.markdown("#### 🍽️ 신메뉴 추천(카페,디저트류 매장 한정)")
                    if "new_product_result" in analysis_data:
                        new_product_data = analysis_data["new_product_result"]
                        
                        # 신메뉴 추천 요약 정보 표시
                        if isinstance(new_product_data, dict):
                            if "proposals" in new_product_data and len(new_product_data["proposals"]) > 0:
                                st.markdown("##### 🍽️ 추천 메뉴")
                                
                                # insight 표시 (있으면)
                                if "insight" in new_product_data and new_product_data["insight"]:
                                    with st.expander("📊 추천 근거 (인사이트)", expanded=False):
                                        st.markdown(new_product_data["insight"].get("summary", "인사이트 없음"))
                                
                                for i, proposal in enumerate(new_product_data["proposals"][:3], 1):
                                    with st.container():
                                        st.markdown(f"### 추천 메뉴 {i}")
                                        
                                        # 기본 정보
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.write(f"**메뉴명:** {proposal.get('menu_name', 'N/A')}")
                                            st.write(f"**카테고리:** {proposal.get('category', 'N/A')}")
                                        with col2:
                                            if "target" in proposal:
                                                target = proposal["target"]
                                                gender = target.get('gender', 'N/A')
                                                ages = target.get('ages', [])
                                                st.write(f"**타겟 고객:** {gender}")
                                                if ages:
                                                    st.write(f"**연령대:** {', '.join(ages)}")
                                        
                                        st.divider()
                                        
                                        # 근거 데이터 (evidence)
                                        if "evidence" in proposal:
                                            with st.expander("📈 추천 근거 (데이터)", expanded=True):
                                                evidence = proposal["evidence"]
                                                st.write(f"**키워드:** {evidence.get('keyword', 'N/A')}")
                                                st.write(f"**순위:** {evidence.get('rank', 'N/A')}위")
                                                st.write(f"**카테고리:** {evidence.get('category', 'N/A')}")
                                                if "rationale" in evidence:
                                                    st.write(f"**이유:** {evidence['rationale']}")
                                                st.caption(f"데이터 출처: {evidence.get('data_source', 'N/A')}")
                                        
                                        # 데이터 근거 (data_backing)
                                        if "data_backing" in proposal:
                                            with st.expander("📊 상세 분석", expanded=False):
                                                backing = proposal["data_backing"]
                                                st.write(f"**고객 적합도:** {backing.get('customer_fit', 'N/A')}")
                                                st.write(f"**트렌드 점수:** {backing.get('trend_score', 'N/A')}")
                                                st.write(f"**시장 격차:** {backing.get('market_gap', 'N/A')}")
                                        
                                        # 전체 제안문 (template_ko)
                                        if "template_ko" in proposal:
                                            with st.expander("📝 전체 제안문", expanded=False):
                                                st.markdown(proposal["template_ko"])
                                        
                                        st.markdown("---")
                                
                                st.success(f"총 {len(new_product_data['proposals'])}개의 메뉴가 추천되었습니다.")
                            else:
                                st.warning("추천 메뉴가 없습니다.")
                                if "activated" in new_product_data and not new_product_data.get("activated"):
                                    st.info(f"비활성화 사유: {new_product_data.get('reason', 'N/A')}")
                                else:
                                    st.json(new_product_data)
                        else:
                            st.json(new_product_data)
                    else:
                        st.info("신메뉴 추천 데이터가 없습니다.")

            
    

    else:

        # 초기 상태

        st.info("👈 왼쪽에서 상점 코드를 입력하세요!")

        

        # 기존 분석 결과가 있는 상점 코드들을 간단히 표시
        output_dir = Path("open_sdk/output")

        existing_analyses = []

        

        if output_dir.exists():

            for analysis_folder in output_dir.iterdir():

                if analysis_folder.is_dir() and analysis_folder.name.startswith("analysis_"):

                    # 폴더명에서 상점 코드 추출 (analysis_XXXXX_YYYYMMDD_HHMMSS 형식)

                    parts = analysis_folder.name.split("_")

                    if len(parts) >= 2:

                        store_code = parts[1]

                        # analysis_result.json 파일이 있는지 확인

                        result_file = analysis_folder / "analysis_result.json"

                        if result_file.exists():

                            # 날짜를 YYYY-MM-DD 형식으로 포맷
                            try:
                                if len(parts) >= 3:
                                    date_str = parts[2]  # YYYYMMDD
                                    if len(date_str) == 8:
                                        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                                    else:
                                        formatted_date = "N/A"
                                else:
                                    formatted_date = "N/A"
                            except:
                                formatted_date = "N/A"
                            
                            existing_analyses.append({

                                "store_code": store_code,

                                "analysis_date": formatted_date
                            })

        
