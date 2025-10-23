"""
간소화된 상담 에이전트 - segment_sns.json 통합 및 프롬프트 최적화
"""
import json
from pathlib import Path
from typing import Dict, Any, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langfuse.decorators import observe
import os
from dotenv import load_dotenv

load_dotenv()
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
            new_product_file = latest_folder / "new_product_result.json"
            if new_product_file.exists():
                with open(new_product_file, 'r', encoding='utf-8') as f:
                    results["new_product_result"] = json.load(f)
                print(f"[DEBUG] New Product result loaded: {new_product_file.name}")
                
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
        sns_file = Path(__file__).parent.parent.parent / "data" / "segment_sns.json"
        
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

def create_consultation_chain(store_code: str, analysis_data: Dict[str, Any], analysis_md: str, mcp_content: str) -> Tuple[RunnableWithMessageHistory, BaseChatMessageHistory]:
    """
    간소화된 Langchain Consultation Chain 생성
    """
    try:
        print(f"[DEBUG] Creating consultation chain for store {store_code}")
        
        # Gemini 모델 초기화 (출력 토큰 수 대폭 증가)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.7,
            max_output_tokens=8192  # 토큰 수 대폭 증가로 텍스트 잘림 방지
        )
        
        # 메모리 초기화
        chat_history = InMemoryChatMessageHistory()
        
        # 분석 데이터에서 핵심 정보 추출
        store_name = analysis_data.get("store_analysis", {}).get("store_overview", {}).get("name", "N/A")
        industry = analysis_data.get("store_analysis", {}).get("store_overview", {}).get("industry", "N/A")
        commercial_area = analysis_data.get("store_analysis", {}).get("store_overview", {}).get("commercial_area", "N/A")
        
        # 에이전트 결과 로드
        agent_results = load_agent_results(store_code)
        
        # SNS 세그먼트 데이터 로드
        sns_data = load_sns_segment_data()
        
        # 마케팅 전략 간소화
        marketing_strategies = []
        if agent_results.get("marketing_result"):
            marketing_strategies = agent_results["marketing_result"].get("marketing_strategies", [])
        else:
            marketing_strategies = analysis_data.get("marketing_analysis", {}).get("marketing_strategies", [])
        
        strategy_summary = "\n".join([
            f"- {i+1}. **{s.get('name', 'N/A')}**: {s.get('description', 'N/A')[:80]}..."
            for i, s in enumerate(marketing_strategies[:3])
        ]) if marketing_strategies else "마케팅 전략 정보 없음"
        
        # 페르소나 정보 및 SNS 채널 추천 생성
        persona_summary = ""
        sns_recommendations = ""
        
        if agent_results.get("marketing_result"):
            marketing_personas = agent_results["marketing_result"].get("personas", [])
        else:
            marketing_personas = analysis_data.get("marketing_analysis", {}).get("personas", [])
        
        if marketing_personas:
            persona_details = []
            age_groups = []
            
            for p in marketing_personas[:2]:
                age_range = p.get('age_range', 'N/A')
                persona_info = f"- **{p.get('name', 'N/A')}** ({age_range}, {p.get('gender', 'N/A')}): {p.get('characteristics', 'N/A')[:60]}..."
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
        
        # 신제품 제안 간소화
        new_product_proposals = []
        if agent_results.get("new_product_result") and agent_results["new_product_result"].get("activated"):
            new_product_proposals = agent_results["new_product_result"].get("proposals", [])
        
        new_product_summary = "\n".join([
            f"- {i+1}. **{p.get('menu_name', 'N/A')}** ({p.get('category', 'N/A')}) - 타겟: {p.get('target', {}).get('gender', 'N/A')} {', '.join(p.get('target', {}).get('ages', []))}"
            for i, p in enumerate(new_product_proposals[:3])
        ]) if new_product_proposals else "신제품 제안 정보 없음"
        
        # 파노라마 분석 간소화
        panorama_summary = analysis_data.get("panorama_analysis", {}).get("synthesis", {}).get("final_recommendation", "N/A")
        
        # MCP 검색 결과 처리
        safe_mcp_content = ""
        if mcp_content:
            safe_mcp_content = mcp_content[:1000].replace("{", "{{").replace("}", "}}")
        
        # 시스템 프롬프트 간소화
        system_prompt = f"""당신은 매장 '{store_name}' (업종: {industry}, 상권: {commercial_area})의 전문 비즈니스 컨설턴트입니다.

## 📊 핵심 분석 데이터
{safe_mcp_content}

### 📈 마케팅 전략
{strategy_summary}

### 👥 고객 페르소나
{persona_summary}

### 📱 SNS 채널 추천 (segment_sns.json 참고)
{sns_recommendations}

### 🍰 신제품 제안
{new_product_summary}

### 🌆 지역 특성
{panorama_summary[:150]}...

## 💡 답변 가이드라인
- **JSON 데이터 기반**으로 정확한 근거를 제시하세요
- **실행 가능한 조언**을 구체적으로 제공하세요  
- **이전 대화를 기억**하고 연속적으로 답변하세요
- **관련 없는 메뉴 제안 금지** - 실제 데이터에 근거한 제안만 하세요
- **SNS 채널 추천 시** segment_sns.json 데이터를 참고하여 연령대별 사용률과 트렌드를 명시하세요

## 📱 SNS 채널 추천 가이드라인
- 마케팅 채널 관련 질문 시 **segment_sns.json 데이터를 반드시 참고**하세요
- 연령대별 사용률과 트렌드 변화를 구체적으로 제시하세요
- 예: "20대 고객에게는 인스타그램(87.4%, 대폭 상승)을 추천합니다. segment_sns.json 참고"

## 🚫 금지 사항
- 추측성 답변, 데이터 없는 정보 제시 금지
- 민감한 경영 정보 직접 언급 금지
"""
        
        # 프롬프트 템플릿 구성
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        # Chain 생성
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
    상담 체인과 대화 (간소화 버전)
    """
    try:
        print(f"[DEBUG] User: {user_message}")
        
        # 기존 대화 기록 가져오기
        history_messages = chat_history.messages
        
        # 체인 실행
        response = chain.invoke({
            "chat_history": history_messages,
            "input": user_message
        })
        
        # 대화 기록에 추가
        chat_history.add_user_message(user_message)
        chat_history.add_ai_message(response.content)
        
        return response.content
    except Exception as e:
        print(f"[ERROR] Error during chat_with_consultant: {e}")
        import traceback
        traceback.print_exc()
        return f"죄송합니다. 상담 중 오류가 발생했습니다: {str(e)}"
