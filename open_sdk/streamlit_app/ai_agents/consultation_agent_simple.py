"""
간소화된 상담 에이전트 - 프롬프트 길이 최적화
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
import sys

# 환경 변수 로더
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from env_loader import load_env
load_env()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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

def create_consultation_chain(store_code: str, analysis_data: Dict[str, Any], analysis_md: str, mcp_content: str) -> Tuple[RunnableWithMessageHistory, BaseChatMessageHistory]:
    """
    간소화된 Langchain Consultation Chain 생성
    """
    try:
        print(f"[DEBUG] Creating consultation chain for store {store_code}")
        
        # Gemini 모델 초기화 (출력 토큰 수 증가)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.7,
            max_output_tokens=8192  # 토큰 수 대폭 증가
        )
        
        # 메모리 초기화
        chat_history = InMemoryChatMessageHistory()
        
        # 분석 데이터에서 핵심 정보 추출
        store_name = analysis_data.get("store_analysis", {}).get("store_overview", {}).get("name", "N/A")
        industry = analysis_data.get("store_analysis", {}).get("store_overview", {}).get("industry", "N/A")
        commercial_area = analysis_data.get("store_analysis", {}).get("store_overview", {}).get("commercial_area", "N/A")
        
        # 에이전트 결과 로드
        agent_results = load_agent_results(store_code)
        
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

### 🍰 신제품 제안
{new_product_summary}

### 🌆 지역 특성
{panorama_summary[:150]}...

## 💡 답변 가이드라인
- **JSON 데이터 기반**으로 정확한 근거를 제시하세요
- **실행 가능한 조언**을 구체적으로 제공하세요  
- **이전 대화를 기억**하고 연속적으로 답변하세요
- **관련 없는 메뉴 제안 금지** - 실제 데이터에 근거한 제안만 하세요

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
