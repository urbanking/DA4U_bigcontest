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

# .env 파일 로드
load_dotenv()

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
        
        # Gemini 모델 초기화 (출력 토큰 수 증가)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.7,
            max_output_tokens=4096  # 토큰 수 증가로 텍스트 잘림 방지
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
        
        # MCP 검색 결과 처리 (안전하게)
        safe_mcp_content = ""
        if mcp_content:
            # 처음 2000자만 사용 (프롬프트 길이 제한)
            safe_mcp_content = mcp_content[:2000].replace("{", "{{").replace("}", "}}")
        
        # 시스템 프롬프트 구성 (중괄호 이스케이프 - 모든 { } 를 {{ }} 로 변환)
        # analysis_md에 JSON이 포함되어 있어 중괄호 문제 발생 가능
        safe_analysis_md = analysis_md[:3000].replace("{", "{{").replace("}", "}}")
        safe_strategy_summary = strategy_summary.replace("{", "{{").replace("}", "}}")
        safe_panorama_summary = panorama_summary[:500].replace("{", "{{").replace("}", "}}")
        
        # MCP 섹션 조건부 추가
        mcp_section = ""
        if safe_mcp_content:
            mcp_section = f"""
### Google Maps 정보 (MCP 검색 결과) - 출처: Google Maps API
{safe_mcp_content}...
"""
        
        system_prompt = f"""당신은 매장 '{store_name}' (상점 코드: {store_code})의 전문 비즈니스 컨설턴트입니다.

## 매장 기본 정보
- 상점명: {store_name}
- 업종: {industry}
- 상권: {commercial_area}
- 상권명: {marketplace_name}

## 📊 통합 분석 데이터
다음은 5차원 분석 결과입니다. 답변 시 여러 출처를 **종합적으로 통합**하여 맥락 있는 인사이트를 제공하세요:
{mcp_section}
### 🗺️ Google Maps 리뷰 & 평가 - 출처: Google Maps API
- 실제 고객들의 솔직한 리뷰와 평점 정보
- 강점과 약점을 파악하는 가장 직접적인 데이터

### 📈 마케팅 전략 (상위 5개) - 출처: marketing_analysis.json
{safe_strategy_summary}
- 각 전략은 고객 페르소나 기반으로 설계됨
- 실행 가능한 구체적인 액션 플랜 포함

### 🌆 지역 특성 (파노라마 분석) - 출처: panorama_analysis.json
{safe_panorama_summary}...
- 300m 반경 내 5개 파노라마 이미지 AI 분석
- 상권 분위기, 보행환경, 업종다양성 점수

### 🏪 매장 성과 & 고객 분석 - 출처: store_analysis.json
- 매출 트렌드, 고객 연령/성별 분포
- 재방문율, 동종업계 순위
- 고객 유형 분석 (유동 vs 정착)

### 🏬 상권 분석 - 출처: marketplace_analysis.json
- 상권 규모, 경쟁 환경
- 유동인구 패턴, 점포 수
- 입지 적합성 평가

### 📋 통합 리포트 - 출처: merged_analysis_full.md
{safe_analysis_md}...

## 🎯 상담 원칙

### 1. **종합적이고 맥락 있는 답변**
- 단일 출처가 아닌 **여러 데이터를 융합**하여 입체적인 인사이트 제공
- 예: "마케팅 전략은?"
  - ❌ 나쁜 답변: "marketing_analysis.json에 5개 전략이 있습니다" (단순 나열)
  - ✅ 좋은 답변: "Google Maps 리뷰에서 '커피 맛이 예술'이라는 평가를 받고 있는 강점을 살려, 
    marketing_analysis의 전략 2 '시그니처 블렌드 개발'을 추천합니다. 
    또한 panorama 분석에서 주거 상권으로 나타난 점을 고려하여 전략 1 '단골 멤버십'으로 지역 주민 충성도를 높이세요."

### 2. **구체적인 실행 방안 제시**
- "다양한 채널 활용" (X) → "인스타그램, 지역 커뮤니티 카페, 매장 POP" (O)
- "분위기 개선" (X) → "올드 패션 인테리어를 고양이 테마 소품으로 현대화, 조명 교체" (O)
- "프로모션 진행" (X) → "오전 8-10시 아메리카노 2,000원 할인, 스탬프 10개 무료 음료" (O)

### 3. **매장 특성에 맞춘 커스터마이징**
- Google Maps 리뷰의 **실제 고객 피드백을 최우선**으로 반영
- 상권 특성 (주거/상업/오피스) 고려
- 업종 특성 (카페/음식점/소매) 고려
- 고객 연령/성별 분포 고려

### 4. **강점-약점 통합 분석**
항상 다음 구조로 답변:
1. **현황 파악**: 여러 출처에서 발견된 강점과 약점
2. **전략 제시**: 강점을 극대화하고 약점을 보완하는 방법
3. **실행 방안**: 구체적인 채널, 기간, 예산, 방법
4. **예상 효과**: 매출/고객 증대 등 정량적 목표

### 5. **마케팅 채널 구체화**
"다양한 채널" 금지! 항상 구체적으로:
- 📱 **온라인**: 인스타그램 피드/릴스, 네이버 플레이스, 카카오맵, 지역 맘카페
- 🏪 **오프라인**: 매장 POP, 전단지, 현수막, 스탠드배너
- 🤝 **협업**: 인근 오피스 제휴, 지역 축제 참여, 배달앱 입점
- � **입소문**: 리뷰 이벤트, 인플루언서 초대, 단골 추천 혜택

### 6. **리뷰 활용 원칙**
- Google Maps 리뷰의 **구체적인 문장을 인용**
- 긍정 리뷰: 강점으로 활용 → 마케팅 메시지화
- 부정 리뷰: 개선 포인트 → 액션 플랜 수립

## 📋 출처 표기 (필수)
모든 답변 마지막에:
📋 **참고 자료:**
- Google Maps API: [구체적 내용]
- marketing_analysis.json: [전략 번호]
- panorama_analysis.json: [항목명]
- store_analysis.json: [섹션명]

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
def chat_with_consultant(chain, chat_history, user_message: str) -> str:
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
