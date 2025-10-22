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

# .env 파일 로드
load_dotenv()

# UTF-8 강제 설정 (Windows 환경)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Gemini API Key 확인
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("[ERROR] GEMINI_API_KEY not found in environment")


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


def create_consultation_chain(store_code: str, analysis_data: dict, analysis_md: str):
    """
    Langchain 기반 상담 체인 생성
    
    Args:
        store_code: 상점 코드
        analysis_data: 통합 분석 JSON 데이터
        analysis_md: 통합 분석 MD 텍스트
        
    Returns:
        tuple: (chain, chat_history)
    """
    try:
        print(f"[DEBUG] Creating consultation chain for store {store_code}")
        
        # Gemini 모델 초기화
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.7,
            max_output_tokens=2048
        )
        
        # 메모리 초기화 (InMemoryChatMessageHistory)
        chat_history = InMemoryChatMessageHistory()
        
        # 분석 데이터에서 핵심 정보 추출
        store_name = analysis_data.get("store_analysis", {}).get("store_overview", {}).get("name", "N/A")
        industry = analysis_data.get("store_analysis", {}).get("store_overview", {}).get("industry", "N/A")
        commercial_area = analysis_data.get("store_analysis", {}).get("store_overview", {}).get("commercial_area", "N/A")
        
        # 마케팅 전략 추출
        marketing_strategies = analysis_data.get("marketing_analysis", {}).get("marketing_strategies", [])
        strategy_summary = "\n".join([
            f"- {i+1}. {s.get('name', 'N/A')}: {s.get('description', 'N/A')}"
            for i, s in enumerate(marketing_strategies[:5])
        ]) if marketing_strategies else "마케팅 전략 정보 없음"
        
        # 상권 분석 추출
        marketplace_name = analysis_data.get("marketplace_analysis", {}).get("상권명", "N/A")
        
        # 파노라마 분석 추출
        panorama_summary = analysis_data.get("panorama_analysis", {}).get("synthesis", {}).get("final_recommendation", "N/A")
        
        # 시스템 프롬프트 구성 (중괄호 이스케이프 - 모든 { } 를 {{ }} 로 변환)
        # analysis_md에 JSON이 포함되어 있어 중괄호 문제 발생 가능
        safe_analysis_md = analysis_md[:3000].replace("{", "{{").replace("}", "}}")
        safe_strategy_summary = strategy_summary.replace("{", "{{").replace("}", "}}")
        safe_panorama_summary = panorama_summary[:500].replace("{", "{{").replace("}", "}}")
        
        system_prompt = f"""당신은 매장 '{store_name}' (상점 코드: {store_code})의 전문 비즈니스 컨설턴트입니다.

## 매장 기본 정보
- 상점명: {store_name}
- 업종: {industry}
- 상권: {commercial_area}
- 상권명: {marketplace_name}

## 분석 데이터
다음은 매장에 대한 전체 분석 데이터입니다:

### 마케팅 전략 (상위 5개)
{safe_strategy_summary}

### 지역 특성 (파노라마 분석)
{safe_panorama_summary}...

### 전체 분석 리포트 (Markdown)
{safe_analysis_md}...

## 상담 지침
1. 데이터 기반 답변: 위 분석 데이터를 바탕으로 정확하고 구체적으로 답변하세요
2. 친절하고 전문적: 비즈니스 컨설턴트로서 친절하면서도 전문적인 톤을 유지하세요
3. 실행 가능한 조언: 막연한 조언이 아닌 실행 가능한 구체적인 방안을 제시하세요
4. 한국어 사용: 모든 답변은 한국어로 작성하세요
5. 질문 이해: 사용자의 질문 의도를 정확히 파악하고 맥락에 맞는 답변을 제공하세요
6. 데이터 없음 금지: "데이터가 없습니다"라는 답변은 최대한 지양하고, 제공된 데이터 내에서 최선의 답변을 제공하세요

## 예시 질문과 답변 스타일
- "매장 이름이 뭐야?" → "매장 이름은 {store_name} 입니다."
- "마케팅 전략은?" → 구체적인 전략 리스트 제공
- "어떤 업종이야?" → "{industry} 업종으로 분류됩니다."
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


def chat_with_consultant(chain, chat_history, user_message: str) -> str:
    """
    상담 체인과 대화
    
    Args:
        chain: Langchain Runnable (Prompt | LLM)
        chat_history: InMemoryChatMessageHistory 인스턴스
        user_message: 사용자 메시지
        
    Returns:
        str: AI 응답
    """
    try:
        print(f"[DEBUG] User: {user_message}")
        
        # 기존 대화 기록 가져오기
        history_messages = chat_history.messages
        
        # 체인 실행 (chat_history와 input 전달)
        response = chain.invoke({
            "chat_history": history_messages,
            "input": user_message
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
