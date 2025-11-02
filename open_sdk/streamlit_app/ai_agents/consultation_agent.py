"""
Consultation Agent using Langchain + Gemini
대화형 상담 에이전트 (ConversationBufferMemory 사용)
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory


# Langfuse tracing 추가 (올바른 방식)
try:
    from langfuse import observe
    from langfuse.openai import openai as langfuse_openai
    LANGFUSE_AVAILABLE = True
    print("[OK] Langfuse initialized successfully")
except ImportError:
    print("[WARN] Langfuse not available - tracing disabled")
    LANGFUSE_AVAILABLE = False
    langfuse_openai = None

# 환경 변수 로더
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from env_loader import load_env
load_env()

# UTF-8 강제 설정 (Windows 환경) - LogCapture와 충돌 방지
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # LogCapture 객체인 경우 무시
        pass

# Gemini API Key 확인
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("[ERROR] GEMINI_API_KEY not found in environment")


def load_agent_results(store_code: str) -> dict:
    """
    에이전트 결과 JSON 파일들을 로드하여 파싱
    
    Args:
        store_code: 매장 코드
        
    Returns:
        dict: 파싱된 에이전트 결과들
    """
    results = {
        "marketing_result": None,
        "new_product_result": None
    }
    
    try:
        from pathlib import Path
        
        # output 폴더에서 해당 store_code의 최신 분석 폴더 찾기
        output_dir = Path(__file__).parent.parent.parent / "output"
        store_folders = sorted(
            [f for f in output_dir.glob(f"analysis_{store_code}_*") if f.is_dir()],
            key=lambda x: x.name,
            reverse=True
        )
        
        if store_folders:
            latest_folder = store_folders[0]
            
            # Marketing Agent 결과 로드
            marketing_file = latest_folder / "marketing_result.json"
            if marketing_file.exists():
                with open(marketing_file, 'r', encoding='utf-8') as f:
                    results["marketing_result"] = json.load(f)
                print(f"[DEBUG] Marketing result loaded: {marketing_file.name}")
            
            # New Product Agent 결과 로드
# 86-90번째 줄 변경
            # New Product Agent 결과 로드
            new_product_file = latest_folder / "new_product_result.json"
            if new_product_file.exists():
                with open(new_product_file, 'r', encoding='utf-8') as f:
                    results["new_product_result"] = json.load(f)
                print(f"[DEBUG] New Product result loaded: {new_product_file.name}")
            else:
                # analysis_ 폴더에 없으면 naver_datalab_ 폴더에서 찾기
                datalab_folders = sorted(
                    [f for f in output_dir.glob("naver_datalab_*") if f.is_dir()],
                    key=lambda x: x.name,
                    reverse=True
                )
                
                for datalab_folder in datalab_folders:
                    new_product_file = datalab_folder / f"{store_code}_new_product_result.json"
                    if new_product_file.exists():
                        with open(new_product_file, 'r', encoding='utf-8') as f:
                            results["new_product_result"] = json.load(f)
                        print(f"[DEBUG] New Product result loaded from datalab: {new_product_file.name}")
                        break
    except Exception as e:
        print(f"[WARN] Failed to load agent results: {e}")
    
    return results

def load_sns_segment_data() -> dict:
    """
    segment_sns.json 데이터를 로드하여 연령대별 SNS 채널 정보 반환
    
    Returns:
        dict: 연령대별 SNS 채널 데이터
    """
    try:
        from pathlib import Path
        
        # segment_sns.json 파일 경로
        sns_file = Path(__file__).parent.parent.parent.parent / "data" / "segment_sns.json"
        
        if sns_file.exists():
            with open(sns_file, 'r', encoding='utf-8') as f:
                sns_data = json.load(f)
            print(f"[DEBUG] SNS segment data loaded: {sns_file.name}")
            return sns_data
        else:
            print(f"[WARN] SNS segment file not found: {sns_file}")
            return {}
            
    except Exception as e:
        print(f"[WARN] Failed to load SNS segment data: {e}")
        return {}

def get_age_based_sns_recommendations(age_groups: list, sns_data: dict) -> str:
    """
    연령대별 SNS 채널 추천 정보 생성
    
    Args:
        age_groups: 타겟 연령대 리스트 (예: ["20대", "30대"])
        sns_data: segment_sns.json 데이터
        
    Returns:
        str: 연령대별 SNS 채널 추천 정보
    """
    if not sns_data or "age_top5_channels" not in sns_data:
        return "SNS 채널 데이터 없음"
    
    recommendations = []
    age_channels = sns_data["age_top5_channels"]
    
    for age_group in age_groups:
        age_key = f"연령-{age_group}"
        if age_key in age_channels:
            channels = age_channels[age_key]
            age_info = f"**{age_group}**: "
            top_channels = []
            
            for channel in channels[:3]:  # 상위 3개만
                channel_name = channel["channel"]
                usage_percent = channel["usage_percent"]
                trend = channel["trend_label"]
                top_channels.append(f"{channel_name}({usage_percent}%, {trend})")
            
            age_info += " / ".join(top_channels)
            recommendations.append(age_info)
    
    if recommendations:
        return "\n".join(recommendations)
    else:
        return "해당 연령대 SNS 데이터 없음"


def analyze_flyer_marketing_potential(store_data: dict, panorama_data: dict) -> dict:
    """
    파노라마 데이터와 매장 데이터를 분석하여 전단지 마케팅 적합성 판단
    
    Args:
        store_data: 매장 분석 데이터
        panorama_data: 파노라마 분석 데이터
        
    Returns:
        dict: 전단지 마케팅 추천 결과
    """
    # 매장 페르소나 분석
    customer_analysis = store_data.get("customer_analysis", {})
    age_distribution = customer_analysis.get("age_group_distribution", {})
    
    # 고령층 비율 계산 (50대 이상)
    senior_ratio = (
        age_distribution.get("50대", 0) + 
        age_distribution.get("60대 이상", 0)
    )
    
    # 신규 고객 비율
    customer_type_analysis = customer_analysis.get("customer_type_analysis", {})
    new_customer_ratio = customer_type_analysis.get("new_customers", {}).get("ratio", 0)
    
    # 상권 분석
    commercial_area_analysis = store_data.get("commercial_area_analysis", {})
    commercial_area = commercial_area_analysis.get("commercial_area", "")
    
    # 페르소나 판정
    is_senior_heavy = senior_ratio >= 30  # 50대 이상 30% 이상
    is_low_new_customer = new_customer_ratio <= 15  # 신규 고객 15% 이하
    is_residential = "아파트" in commercial_area or "주거" in commercial_area or "단지" in commercial_area
    
    # 파노라마 데이터에서 상권 특성 추출
    panorama_summary = panorama_data.get("synthesis", {})
    area_character = panorama_summary.get("area_summary", {}).get("overall_character", "")
    dominant_zone = panorama_summary.get("area_summary", {}).get("dominant_zone_type", "")
    
    # 전단지 마케팅 적합성 판단
    needs_flyer_marketing = is_senior_heavy and is_low_new_customer and is_residential
    
    if not needs_flyer_marketing:
        return {
            "recommended": False,
            "reason": "온라인 마케팅이 더 효과적입니다. 젊은 고객층이 많아 SNS 마케팅을 추천합니다.",
            "alternative": "인스타그램, 페이스북 등 SNS 마케팅 전략을 추천합니다.",
            "persona_analysis": {
                "senior_ratio": senior_ratio,
                "new_customer_ratio": new_customer_ratio,
                "commercial_area": commercial_area,
                "is_senior_heavy": is_senior_heavy,
                "is_low_new_customer": is_low_new_customer,
                "is_residential": is_residential
            }
        }
    
    # 전단지 마케팅 추천 위치들 (파노라마 분석 기반)
    recommended_locations = []
    
    # 파노라마 분석에서 추출한 상권 특성에 따른 위치 추천
    if "주거" in area_character or "아파트" in area_character:
        recommended_locations.extend([
            {
                "location": "아파트 정문 북측 보도",
                "position": "경비실 유리면에서 오른쪽 2m, 벽면쪽 0.6m",
                "time_slot": "16-19시",
                "reason": "앉아 쉬는 보호자·어르신 대기 많음(체류성↑) + 밝고 반사 적어 대화/읽기 쉬움",
                "cautions": "문 전면 금지, 유모차 동선 주의"
            },
            {
                "location": "동네 병원 앞 차양 아래",
                "position": "차양 기둥과 1m 이격, 벽면쪽 0.5m",
                "time_slot": "09-11시",
                "reason": "병원·약국 대기 의자(정지 시간) → 설명 들을 여유 있음",
                "cautions": "진입동선/휠체어 방해 금지"
            }
        ])
    
    if "공원" in area_character or "산책" in area_character:
        recommended_locations.append({
            "location": "공원 입구 그늘 면",
            "position": "입구에서 2m 이격, 나무 그늘 아래 1m",
            "time_slot": "16-19시",
            "reason": "산책 귀가 동선 + 그늘에서 편안한 대화 가능",
            "cautions": "산책로 차단 금지, 운동하는 사람들 주의"
        })
    
    # 기본 추천 위치 (상권 특성과 관계없이)
    if not recommended_locations:
        recommended_locations = [
            {
                "location": "버스쉘터 측면 벤치 끝단",
                "position": "벤치 끝단 옆 0.5m, 깔때기 동선 측면",
                "time_slot": "16-19시",
                "reason": "버스 대기 시간(4초 이상) → 높은 주목도 + 메시지 이해 시간 확보",
                "cautions": "탑승문 전면 금지, 대기줄 방해 주의"
            },
            {
                "location": "동네 마트 계산대 보이는 출입부",
                "position": "출입구에서 1.5m 이격, 유리면 옆 0.8m",
                "time_slot": "09-11시",
                "reason": "쇼핑 후 휴식 시간 + 계산대 대기 중 자연스러운 접촉",
                "cautions": "출입구 차단 금지, 장바구니 동선 주의"
            }
        ]
    
    # 업종별 스크립트
    store_overview = store_data.get("store_overview", {})
    industry = store_overview.get("industry", "기본")
    
    scripts = {
        "카페": [
            "동네 카페 새로 오픈했어요. 어르신 세트 할인권 드릴게요. 여기 QR로 안내됩니다.",
            "맛있는 커피와 디저트로 모시겠습니다. 어르신들께 특별 할인 쿠폰 드려요.",
            "편안한 분위기에서 차 한 잔 어떠세요? 신규 오픈 기념 쿠폰 드립니다."
        ],
        "식료품": [
            "신선한 재료로 만든 건강한 음식입니다. 어르신들께 특별 할인 드려요.",
            "동네 식료품점에서 신선한 채소와 과일을 만나보세요. 할인 쿠폰 드립니다."
        ]
    }
    
    industry_scripts = scripts.get(industry, scripts["카페"])
    
    # 스크립트를 각 위치에 추가
    import random
    for location in recommended_locations:
        location["script"] = random.choice(industry_scripts)
    
    return {
        "recommended": True,
        "persona_analysis": {
            "senior_ratio": senior_ratio,
            "new_customer_ratio": new_customer_ratio,
            "commercial_area": commercial_area,
            "is_senior_heavy": is_senior_heavy,
            "is_low_new_customer": is_low_new_customer,
            "is_residential": is_residential
        },
        "panorama_insights": {
            "area_character": area_character,
            "dominant_zone": dominant_zone
        },
        "why_flyer_effective": f"고령층 비율 {senior_ratio:.1f}% + 신규 고객 비율 {new_customer_ratio:.1f}% + 주거형 상권으로 오프라인 접촉이 효과적",
        "recommended_locations": recommended_locations[:3],  # 상위 3개만
        "general_guidelines": [
            "체류성 40점: 벤치/그늘(+10), 대기 흔적(+10), 유효폭≥2.5m(+8), 소음 낮음(+12)",
            "가독성 30점: 적정 조도(+12), 글레어 낮음(+6), 시야 차단물 없음(+12)",
            "안전 20점: 출입구·계단·차량동선과 이격(+12), 충돌 위험 없음(+8)",
            "고령친화 10점: 의자·난간·평탄 포장 확인(+10)",
            "70점↑ 우선 추천 / 60-69 조건부(시간대 제한) / 59↓ 제외",
            "오전 9-11시: 병원/약국, 시장 입구, 경로당 주변",
            "오후 4-7시: 아파트 정문, 공원 입구, 학원가 보호자 대기 구역"
        ]
    }


def load_merged_analysis(analysis_dir: str) -> tuple:
    """
    통합 분석 파일 (JSON + MD) 로드
    
    Args:
        analysis_dir: 분석 결과 디렉토리
        
    Returns:
        tuple: (merged_json_data: dict, merged_md_content: str)
    """
    try:
        analysis_path = Path(analysis_dir)
        
        # JSON 파일 로드
        merged_json_file = analysis_path / "merged_analysis_full.json"
        with open(merged_json_file, 'r', encoding='utf-8') as f:
            merged_json = json.load(f)
        
        # MD 파일 로드
        merged_md_file = analysis_path / "merged_analysis_full.md"
        with open(merged_md_file, 'r', encoding='utf-8') as f:
            merged_md = f.read()
        
        print(f"[OK] Merged analysis loaded: JSON={len(str(merged_json))} chars, MD={len(merged_md)} chars")
        
        return merged_json, merged_md
        
    except Exception as e:
        print(f"[ERROR] Failed to load merged analysis: {e}")
        return None, None


def create_consultation_chain(store_code: str, analysis_data: dict, analysis_md: str, mcp_content: str = ""):
    """
    Langchain 기반 상담 체인 생성
    
    Args:
        store_code: 상점 코드
        analysis_data: 통합 분석 JSON 데이터
        analysis_md: 통합 분석 MD 텍스트
        mcp_content: Google Maps MCP 검색 결과 (txt)
        
    Returns:
        tuple: (chain, chat_history)
    """
    try:
        print(f"[DEBUG] Creating consultation chain for store {store_code}")
        
        # Gemini 모델 초기화 (출력 토큰 수 대폭 증가)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.7,
            max_output_tokens=14192  # 토큰 수 대폭 증가로 텍스트 잘림 방지
        )
        
        # 메모리 초기화 (InMemoryChatMessageHistory)
        chat_history = InMemoryChatMessageHistory()
        
        # 분석 데이터에서 핵심 정보 추출
        store_name = analysis_data.get("store_analysis", {}).get("store_overview", {}).get("name", "N/A")
        industry = analysis_data.get("store_analysis", {}).get("store_overview", {}).get("industry", "N/A")
        commercial_area = analysis_data.get("store_analysis", {}).get("store_overview", {}).get("commercial_area", "N/A")
        
        # 재방문율 데이터 명시적으로 추출
        store_analysis = analysis_data.get("store_analysis", {})
        customer_analysis = store_analysis.get("customer_analysis", {})
        customer_type_analysis = customer_analysis.get("customer_type_analysis", {})
        returning_customers = customer_type_analysis.get("returning_customers", {})
        returning_customer_ratio = returning_customers.get("ratio", "N/A")
        returning_customer_trend = returning_customers.get("trend", "N/A")
        
        new_customers = customer_type_analysis.get("new_customers", {})
        new_customer_ratio = new_customers.get("ratio", "N/A")
        new_customer_trend = new_customers.get("trend", "N/A")
        
        # 에이전트 결과 로드
        agent_results = load_agent_results(store_code)   
        
        # SNS 세그먼트 데이터 로드
        sns_data = load_sns_segment_data()
        
        # 마케팅 전략 추출 (JSON 파일에서 로드)
        marketing_strategies = []
        marketing_personas = []
        marketing_risks = []
        if agent_results.get("marketing_result"):
            marketing_data = agent_results["marketing_result"]
            marketing_strategies = marketing_data.get("marketing_strategies", [])
            marketing_personas = marketing_data.get("personas", [])
            marketing_risks = marketing_data.get("risk_analysis", {}).get("detected_risks", [])
        else:
            # 기존 방식 (fallback)
            marketing_data = analysis_data.get("marketing_analysis", {})
            marketing_strategies = marketing_data.get("marketing_strategies", [])
            marketing_personas = marketing_data.get("personas", [])
            marketing_risks = marketing_data.get("risk_analysis", {}).get("detected_risks", [])
        
        # 마케팅 전략 간소화 (프롬프트 길이 제한)
        strategy_summary = "\n".join([
            f"- {i+1}. **{s.get('name', 'N/A')}**: {s.get('description', 'N/A')[:100]}..."
            for i, s in enumerate(marketing_strategies[:3])
        ]) if marketing_strategies else "마케팅 전략 정보 없음"
        
        # 페르소나 정보 간소화 및 SNS 채널 추천 생성
        persona_summary = ""
        sns_recommendations = ""
        
        if marketing_personas:
            persona_details = []
            age_groups = []
            
            for p in marketing_personas[:2]:
                age_range = p.get('age_range', 'N/A')
                persona_info = f"- **{p.get('name', 'N/A')}** ({age_range}, {p.get('gender', 'N/A')}): {p.get('characteristics', 'N/A')[:80]}..."
                persona_details.append(persona_info)
                
                # 연령대 추출 (예: "20-30대" -> ["20대", "30대"])
                if age_range and age_range != 'N/A':
                    if "20대" in age_range:
                        age_groups.append("20대")
                    if "30대" in age_range:
                        age_groups.append("30대")
                    if "40대" in age_range:
                        age_groups.append("40대")
                    if "50대" in age_range:
                        age_groups.append("50대")
                    if "60대" in age_range:
                        age_groups.append("60대")
                    if "70대" in age_range:
                        age_groups.append("70대 이상")
            
            persona_summary = "\n".join(persona_details)
            
            # 중복 제거 후 SNS 채널 추천 생성
            unique_age_groups = list(set(age_groups))
            if unique_age_groups and sns_data:
                sns_recommendations = get_age_based_sns_recommendations(unique_age_groups, sns_data)
        else:
            persona_summary = "페르소나 정보 없음"
        
        # 위험 분석 정보 간소화
        risk_summary = "\n".join([
            f"- **{r.get('code', 'N/A')}**: {r.get('name', 'N/A')} ({r.get('level', 'N/A')}, {r.get('score', 'N/A')}/10) - {r.get('evidence', 'N/A')[:60]}..."
            for r in marketing_risks[:3]
        ]) if marketing_risks else "위험 분석 정보 없음"


        
        # 신제품 제안 추출 (JSON 파일에서 로드)
        new_product_proposals = []
        new_product_insights = {}
        if agent_results.get("new_product_result") and agent_results["new_product_result"].get("activated"):
            new_product_data = agent_results["new_product_result"]
            new_product_proposals = new_product_data.get("proposals", [])
            new_product_insights = new_product_data.get("insight", {})
        
        # 신제품 제안 간소화
        new_product_summary = "\n".join([
            f"- {i+1}. **{p.get('menu_name', 'N/A')}** ({p.get('category', 'N/A')}) - 타겟: {p.get('target', {}).get('gender', 'N/A')} {', '.join(p.get('target', {}).get('ages', []))} - 키워드: {p.get('evidence', {}).get('keyword', 'N/A')}"
            for i, p in enumerate(new_product_proposals[:3])
        ]) if new_product_proposals else "신제품 제안 정보 없음"
        
        # 신제품 인사이트 간소화
        new_product_insight_summary = f"고객: {new_product_insights.get('gender_summary', 'N/A')}, {new_product_insights.get('age_summary', 'N/A')}" if new_product_insights else "신제품 인사이트 정보 없음"
        
        # 상권 분석 추출
        marketplace_name = analysis_data.get("marketplace_analysis", {}).get("상권명", "N/A")
        
        # 파노라마 분석 추출
        panorama_summary = analysis_data.get("panorama_analysis", {}).get("synthesis", {}).get("final_recommendation", "N/A")
        
        # 전단지 마케팅 분석은 질문 처리 시에만 조건부로 실행
        # (상담 체인 생성 시에는 실행하지 않음)
        
        # MCP 검색 결과 처리 (안전하게)
        safe_mcp_content = ""
        if mcp_content:
            # 처음 2000자만 사용 (프롬프트 길이 제한)
            safe_mcp_content = mcp_content[:2000].replace("{", "{{").replace("}", "}}")
        
        # 시스템 프롬프트 구성 (중괄호 이스케이프 - 모든 { } 를 {{ }} 로 변환)
        # analysis_md에 JSON이 포함되어 있어 중괄호 문제 발생 가능
        # 시스템 프롬프트 구성 (중괄호 이스케이프 - 모든 { } 를 {{ }} 로 변환)
        # analysis_md에 JSON이 포함되어 있어 중괄호 문제 발생 가능
        safe_analysis_md = analysis_md[:3000].replace("{", "{{").replace("}", "}}")
        safe_strategy_summary = strategy_summary.replace("{", "{{").replace("}", "}}")
        safe_persona_summary = persona_summary.replace("{", "{{").replace("}", "}}")
        safe_risk_summary = risk_summary.replace("{", "{{").replace("}", "}}")
        safe_panorama_summary = panorama_summary[:500].replace("{", "{{").replace("}", "}}")
        safe_new_product_summary = new_product_summary.replace("{", "{{").replace("}", "}}")
        safe_new_product_insight = new_product_insight_summary.replace("{", "{{").replace("}", "}}")
        safe_sns_recommendations = sns_recommendations.replace("{", "{{").replace("}", "}}")
        
        # 재방문율 정보 생성
        revisit_info = f"재방문 고객 비율: {returning_customer_ratio}% (트렌드: {returning_customer_trend}), 신규 고객 비율: {new_customer_ratio}% (트렌드: {new_customer_trend})"
        safe_revisit_info = revisit_info.replace("{", "{{").replace("}", "}}")
        # MCP 섹션 조건부 추가
        mcp_section = ""
        if safe_mcp_content:
            mcp_section = f"""
### Google Maps 정보 (MCP 검색 결과) - 출처: Google Maps API
{safe_mcp_content}...
"""
        
        system_prompt = f"""당신은 매장 '{store_name}' (업종: {industry}, 상권: {commercial_area})의 전문 비즈니스 컨설턴트입니다.

## 📊 핵심 분석 데이터 (JSON 기반)
{mcp_section}
### 📈 마케팅 전략 - marketing_result.json
{safe_strategy_summary}

### 👥 고객 페르소나 - marketing_result.json  
{safe_persona_summary}

### 📱 SNS 채널 추천 - segment_sns.json 참고
{safe_sns_recommendations}

### ⚠️ 위험 분석 - marketing_result.json
{safe_risk_summary}

**위험 코드 정의 (R1-R10 )**:
- R1: 신규유입 급감 (신규 고객 유입이 급격히 감소)
- R2: 재방문율 동일 업종 비해 저하 (평균 대비 3% 이상 낮음)
- R3: 장기매출침체 (10일 이상 매출 정체)
- R4: 단기매출하락 (15% 이상 급격 하락)
- R5: 배달매출하락 (10% 이상 감소)
- R6: 취소율 급등 (0.7% 이상 증가)
- R7: 핵심연령괴리 (핵심 고객 연령층과 8% 이상 괴리)
- R8: 시장부적합 (시장 적합도 점수 70점 이상)
- R9: 상권해지위험 (상권 내 경쟁력 약화, 평균+1.5σ 이상)
- R10: 재방문율 낮음 (재방문율 30% 이하)

**위험 판단 원칙**:
- `risk_analysis.detected_risks` 배열에 나열된 위험만 언급하세요
- 감지된 위험 외에는 "양호"하다고 명시하세요

### 🍰 신제품 제안 - new_product_result.json

### 🍰 신제품 제안 - new_product_result.json
{safe_new_product_summary}

### 📊 신제품 인사이트 - new_product_result.json
{safe_new_product_insight}

### 🌆 지역 특성 - panorama_analysis.json
{safe_panorama_summary[:200]}...

### 🏪 매장 성과 - store_analysis.json
**중요**: 반드시 아래 재방문율 정보를 사용하세요.
{safe_revisit_info}
- 매출 트렌드, 고객 분포, 동종업계 순위

### 🏬 상권 분석 - 출처: marketplace_analysis.json
- 상권 규모, 경쟁 환경
- 유동인구 패턴, 점포 수
- 입지 적합성 평가

### 📋 통합 리포트 - 출처: merged_analysis_full.md
{safe_analysis_md}

### 📄 전단지 광고 위치 추천 - 출처: 파노라마 + 매장 데이터 분석
- 고령층이 많은 매장을 위한 오프라인 마케팅 전략
- 파노라마 이미지 분석을 통한 최적 배부 위치 제안
- 시간대별, 위치별 구체적인 실행 가이드
- *전단지 관련 질문 시 동적으로 분석 결과 제공*

## 🎯 상담 원칙

### 1. **실제 데이터 기반 답변 (헛소리 금지)**
- **반드시 위의 JSON 데이터를 근거로 답변**하세요
- 추측이나 일반론 금지 - 실제 분석 결과만 인용
- 문서명 + 섹션명 + 구체적 수치를 함께 제시
- 예: "신메뉴 제안은?"
  - ❌ "일반적으로 인기 있는 메뉴를 추천합니다" (근거 없음)
  - ✅ "new_product_result.json의 'proposals' 배열에서 '무화과 타르트'가 제안되었으며 (rank: 1, keyword: '무화과'), 
    타겟은 여성 10대, 20대, 30대입니다. 하지만 store_analysis.json의 'customer_analysis.customer_type_analysis'를 보면 
    남성 43.8%, 50대 비중이 크므로 이 불일치를 해결하기 위해 남성 고객층도 고려한 메뉴 보완이 필요합니다."

### 2. **구체적인 데이터 인용**
- **정확한 수치와 퍼센트**를 제시하세요
- **출처 파일명**을 명시하세요 (예: "marketing_result.json의 R2 위험 분석에 따르면...")
- **고객 리뷰의 실제 문장**을 인용하세요

### 3. **데이터 간 연관성 분석**
- 여러 JSON 파일의 데이터를 연결하여 분석하세요
- 예: "Google Maps 리뷰의 '커피가 고소하고 부드러워서 맛있어요' + marketing_result.json의 '시그니처 블렌드 개발' 전략 + 
  store_analysis.json의 재방문율 저하(R2) = 커피 전문성 강화로 재방문율 개선 필요"

### 4. **위험 요소 기반 전략 수정**
- marketing_result.json의 위험 분석(R1-R10)을 반드시 언급하세요
- **중요**: 위의 "위험 코드 정의"를 참고하여, `risk_analysis.detected_risks` 배열에 나열된 위험만 언급하고, 나머지는 "양호"하다고 명시하세요
- 예: "현재         위험이 감지되었습니다. 나머지 위험 요소(언급되지 않은 R *)는 양호한 상태입니다."
- 각 위험 요소에 대한 구체적인 해결 방안을 제시하세요

### 5. **신제품 제안 시 필수 체크리스트**
- new_product_result.json의 기존 제안을 먼저 언급하세요
- store_analysis.json의 실제 고객 분포와 비교하세요
- 불일치가 있으면 구체적인 수치로 설명하고 보완 방안을 제시하세요
- marketing_result.json의 위험 요소와 연결하여 개선 효과를 설명하세요

### 6. **마케팅 채널 구체화**
"다양한 채널" 금지! 항상 구체적으로:
- 📱 **온라인**: 인스타그램 피드/릴스, 네이버 플레이스, 카카오맵, 지역 맘카페
- 🏪 **오프라인**: 매장 POP, 전단지, 현수막, 스탠드배너
- 🤝 **협업**: 인근 오피스 제휴, 지역 축제 참여, 배달앱 입점
- � **입소문**: 리뷰 이벤트, 인플루언서 초대, 단골 추천 혜택

### 7. **답변 구조 (필수)**
1. **현재 상황**: JSON 데이터에서 확인된 실제 상황
2. **문제점**: 데이터 간 불일치나 위험 요소
3. **해결 방안**: 구체적인 전략과 실행 방법
4. **근거**: 어떤 JSON 파일의 어떤 데이터를 근거로 했는지 명시
5. **예상 효과**: 정량적 목표와 개선 지표

### 8. **전단지 광고 전략 (고령층 타겟)**
고객이 "전단지", "오프라인 마케팅", "배부", "광고 위치" 등을 언급하면:
- **페르소나 분석**: 고령층 비율, 신규 고객 비율, 상권 특성 확인
- **위치 추천**: 파노라마 분석 기반 구체적인 배부 위치 제시
- **시간대 가이드**: 오전 9-11시, 오후 4-7시 등 최적 시간대 안내
- **스크립트 제공**: 고령층에게 효과적인 대화 스크립트 제시
- **주의사항**: 법적 제약, 민원 방지, 안전 수칙 안내
- **대안 제시**: 전단지가 부적합한 경우 온라인 마케팅 대안 제시

## 📋 출처 표기 (필수)
모든 답변 마지막에:
📋 **참고 자료:**
- Google Maps API: [구체적 내용]
- marketing_analysis.json: [전략 번호]
- panorama_analysis.json: [항목명]
- store_analysis.json: [섹션명]
- 전단지 위치 추천: [파노라마 + 매장 데이터 분석]

### 9. **문서 내용 상세 설명 (신규 추가)**
데이터를 참조할 때는 파일명뿐만 아니라 **구체적인 내용과 의미**를 설명하세요:

예시 1:
- ❌ 나쁜 답변: "marketing_result.json을 보면..."
- ✅ 좋은 답변: "marketing_result.json의 '마케팅 전략 2: 계절별 시그니처 메뉴 개발' 분석에 따르면, 
  '일상 속 작은 여유' 콘셉트로 계절 재료를 활용한 한정판 메뉴를 추천하고 있습니다. 
  이 전략은 매장의 재방문율 저하(R2 위험)를 해결하기 위한 핵심 방안 중 하나로 제시되었습니다."

예시 2:
- ❌ 나쁜 답변: "store_analysis.json의 고객 분석을 보면..."
- ✅ 좋은 답변: "store_analysis.json의 'customer_type_analysis' 섹션을 보면, 
  재방문 고객 비율이 [실제 수치]%로 나타났습니다. 이는 한식 업종 평균 재방문율([업종 평균]%)과 비교하여 
  [차이]%p [낮음/높음] 수치로, [R2 위험 요소 감지 여부]를 알 수 있습니다. 
  또한 'customer_type_analysis'의 'new_customers' 비율은 [신규 고객 비율]%로 나타나 신규 고객 유입도 [개선 필요/양호]합니다."

예시 3:
- ❌ 나쁜 답변: "위험 진단에 R2가 있습니다."
- ✅ 좋은 답변: "marketing_result.json의 'risk_analysis.detected_risks' 배열에서 R2 위험이 감지되었습니다. 
  R2는 '재방문율 저하' 위험으로, 재방문율이 업종 평균 대비 3% 이상 하락했을 때 트리거됩니다. 
  현재 매장의 재방문율은 [실제 수치]%로 한식 업종 평균([업종 평균]%)보다 [차이]%p [낮음/높음]아 [높은 우선순위/보통 우선순위]로 분류되었으며, 
  가중치 [가중치]점, 영향도 점수(impact_score) [영향도]점이 부여되었습니다. 
  완화 전략으로는 [완화 전략 목록]이 제안되었습니다."
### 10. **점수 및 위험 계산 로직 설명 (신규 추가)**
사용자가 점수나 위험에 대해 질문할 때는 **계산 방식과 근거**를 명확히 설명하세요:

**마케팅 위험 점수 (Risk Score) 계산:**
- 각 위험 코드(R1-R10)는 고유한 가중치(threshold_value)와 영향도 점수(impact_score)를 가집니다
- 실제 점수는 (심각도 × 가중치)로 계산되며, 최대 100점입니다
- 예: R2(재방문율 저하)의 점수 계산: |[재방문율] - [업종 평균]| × 5 = [계산된 점수]점
- **중요**: 위의 "매장 성과" 섹션에 제공된 실제 재방문율 값을 사용하세요!

**전체 위험 수준 (Overall Risk Level) 결정:**
- 위험 점수들의 평균을 계산합니다
- 평균 80점 이상: 위험(Critical)
- 평균 60-79점: 높음(High)
- 평균 40-59점: 보통(Medium)
- 평균 40점 미만: 낮음(Low)

**매장 성과 점수 (Store Performance Score) 계산:**
- CVI(Commercial Viability Index): 상업적 생존 가능성 지수
- ASI(Accessibility Score Index): 접근성 지수
- SCI(Store Competitiveness Index): 매장 경쟁력 지수
- GMI(Growth & Market Index): 성장 및 시장 지수
- 각 지표는 0-100점 범위로 계산되며, 전체 점수는 4개 지표의 평균입니다

**등급(Grade) 산정:**
- 95점 이상: A+
- 90-94점: A
- 85-89점: B+
- 80-84점: B
- 75-79점: C+
- 70-74점: C
- 60-69점: D
- 60점 미만: F

## 🗣️ 답변 스타일
- 친절하지만 전문적
- 구체적이고 실용적
- 여러 데이터를 자연스럽게 통합
- 실행 가능한 액션 아이템 제시
"""
        
        # 프롬프트 템플릿 구성
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        # Chain 생성 (최신 Langchain 방식)
        chain = prompt_template | llm
        
        print(f"[OK] Consultation chain created successfully")
        return chain, chat_history
        
    except Exception as e:
        print(f"[ERROR] Failed to create consultation chain: {e}")
        import traceback
        traceback.print_exc()
        return None, None


@observe()
def chat_with_consultant(chain, chat_history, user_message: str, store_data: dict = None, panorama_data: dict = None) -> str:
    """
    상담 체인과 대화 (Langfuse tracing 포함)
    
    Args:
        chain: Langchain Runnable (Prompt | LLM)
        chat_history: InMemoryChatMessageHistory 인스턴스
        user_message: 사용자 메시지
        
    Returns:
        str: AI 응답
    """
    try:
        print(f"[DEBUG] User: {user_message}")
        
        # 전단지 관련 질문인지 확인
        flyer_keywords = ["전단지", "오프라인", "배부", "광고", "전단", "배포", "홍보"]
        is_flyer_question = any(keyword in user_message.lower() for keyword in flyer_keywords)
        
        # 전단지 관련 질문이 있고 데이터가 있으면 동적 분석 수행
        flyer_analysis = ""
        if is_flyer_question and store_data and panorama_data:
            print(f"[DEBUG] 전단지 관련 질문 감지 - 동적 분석 실행")
            flyer_recommendation = analyze_flyer_marketing_potential(store_data, panorama_data)
            
            if flyer_recommendation.get("recommended", False):
                persona = flyer_recommendation['persona_analysis']
                panorama_insights = flyer_recommendation['panorama_insights']
                
                flyer_analysis = f"""

### 📄 전단지 광고 위치 추천 (고령층 타겟)
**매장 페르소나:** 고령층 {persona['senior_ratio']:.1f}% + 신규고객 {persona['new_customer_ratio']:.1f}% + {persona['commercial_area']}
**파노라마 분석:** {panorama_insights['area_character'][:100]}...

**전단지가 효과적인 이유:** {flyer_recommendation['why_flyer_effective']}

**추천 위치:**
"""
                for i, location in enumerate(flyer_recommendation['recommended_locations'], 1):
                    flyer_analysis += f"""
{i}. **{location['location']}**
   - 서 있을 위치: {location['position']}
   - 시간대: {location['time_slot']}
   - 효과적 이유: {location['reason']}
   - 스크립트: "{location['script']}"
   - 주의사항: {location['cautions']}
"""
            else:
                flyer_analysis = f"""

### 📄 전단지 광고 추천 결과
{flyer_recommendation.get('reason', '전단지 광고가 적합하지 않습니다.')}
**대안:** {flyer_recommendation.get('alternative', '온라인 마케팅을 추천합니다.')}
"""
        
        # 기존 대화 기록 가져오기
        history_messages = chat_history.messages
        
        # 체인 실행 (chat_history와 input 전달)
        # 전단지 분석 결과가 있으면 사용자 메시지에 추가
        enhanced_message = user_message
        if flyer_analysis:
            enhanced_message = f"{user_message}\n\n{flyer_analysis}"
        
        response = chain.invoke({
            "chat_history": history_messages,
            "input": enhanced_message
        })
        
        # 대화 기록에 추가
        chat_history.add_user_message(user_message)
        chat_history.add_ai_message(response.content)
        
        print(f"[DEBUG] AI: {response.content[:100]}...")
        
        return response.content
        
    except Exception as e:
        print(f"[ERROR] Chat failed: {e}")
        import traceback
        traceback.print_exc()
        return f"죄송합니다. 오류가 발생했습니다: {str(e)}"
