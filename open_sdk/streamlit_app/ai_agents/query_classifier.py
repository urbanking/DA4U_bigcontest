"""
Query Classifier using Langchain + Gemini
사용자 질의 의도를 파악하는 분류기
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

# .env 파일 로드
load_dotenv()

# Gemini API Key 확인
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("[ERROR] GEMINI_API_KEY not found in environment")

def classify_query_sync(user_query: str) -> dict:
    """
    사용자 질의를 분류합니다.
    
    Args:
        user_query: 사용자 입력 텍스트
        
    Returns:
        dict: {
            "intent": "store_code_query" | "general_consultation" | "restart_analysis",
            "store_code": str | None,
            "confidence": float
        }
    """
    try:
        # Gemini 모델 초기화
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.1
        )
        
        # 시스템 프롬프트
        system_prompt = """당신은 사용자 질의 의도를 분석하는 AI입니다.

사용자 입력을 다음 3가지 카테고리로 분류하세요:

1. **store_code_query**: 10자리 상점 코드가 포함된 경우
   - 예: "000F03E44A", "002816BA73", "1234567890"
   - 상점 코드는 정확히 10자리의 영문+숫자 조합입니다
   
2. **general_consultation**: 분석 결과에 대한 질문
   - 예: "마케팅 전략이 뭐야?", "매장 이름이 뭐야?", "고객 분석 보여줘"
   - 이미 분석된 결과에 대한 후속 질문
   
3. **restart_analysis**: 새로운 분석을 원하는 경우
   - 예: "다른 매장 분석해줘", "처음부터 다시", "새로 시작"

응답 형식 (JSON):
{
    "intent": "store_code_query" | "general_consultation" | "restart_analysis",
    "store_code": "추출된 상점 코드 (없으면 null)",
    "confidence": 0.0~1.0
}
"""
        
        # 메시지 구성
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"사용자 입력: {user_query}")
        ]
        
        # LLM 호출
        response = llm.invoke(messages)
        
        # 응답 파싱
        import json
        import re
        
        # JSON 추출
        json_match = re.search(r'\{[^}]+\}', response.content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            # JSON 형식이 아닌 경우 기본값 반환
            result = {
                "intent": "general_consultation",
                "store_code": None,
                "confidence": 0.5
            }
        
        print(f"[Query Classifier] Intent: {result['intent']}, Store Code: {result.get('store_code')}")
        return result
        
    except Exception as e:
        print(f"[ERROR] Query classification failed: {e}")
        import traceback
        traceback.print_exc()
        
        # 폴백: 간단한 정규식 매칭
        import re
        store_code_match = re.search(r'[A-Z0-9]{10}', user_query)
        
        if store_code_match:
            return {
                "intent": "store_code_query",
                "store_code": store_code_match.group(),
                "confidence": 0.8
            }
        else:
            return {
                "intent": "general_consultation",
                "store_code": None,
                "confidence": 0.5
            }
