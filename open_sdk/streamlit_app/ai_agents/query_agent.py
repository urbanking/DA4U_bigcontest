"""
Query Classification Agent using OpenAI Agents SDK
사용자 입력을 상점 코드와 일반 질문으로 분류
"""
from agents import Agent, Runner
import re
from typing import Dict, Any
import os

# OpenAI API 설정
from dotenv import load_dotenv
load_dotenv()  # .env 파일 로드

# API 키 직접 설정
openai_key = os.getenv("OPENAI_API_KEY", "")
if openai_key:
    os.environ["OPENAI_API_KEY"] = openai_key
    print(f"[OK] OpenAI API Key loaded: {openai_key[:10]}...")
else:
    print("[ERROR] OPENAI_API_KEY not found in environment")

# Query Classifier Agent
query_classifier_agent = Agent(
    name="Query Classifier",
    model="gpt-4o",  # OpenAI GPT-4o
    instructions="""
    You are a query classifier agent. Your job is to analyze user input and classify it.
    
    Classification types:
    1. STORE_CODE: A 10-character alphanumeric code (e.g., 000F03E44A)
    2. GENERAL_QUERY: Any other question or conversation
    
    Always respond in JSON format:
    {
        "type": "STORE_CODE" or "GENERAL_QUERY",
        "value": "the input value",
        "confidence": 0.0-1.0
    }
    """,
    output_type=dict
)

async def classify_query(user_input: str) -> Dict[str, Any]:
    """
    사용자 입력을 분류합니다.
    
    Args:
        user_input: 사용자가 입력한 텍스트
        
    Returns:
        분류 결과 딕셔너리
    """
    try:
        # 빠른 정규식 체크
        store_code_pattern = r'^[A-Z0-9]{10}$'
        if re.match(store_code_pattern, user_input.strip()):
            return {
                "type": "STORE_CODE",
                "value": user_input.strip(),
                "confidence": 1.0
            }
        
        # Agent를 사용한 분류
        result = await Runner.run(query_classifier_agent, user_input)
        return result.final_output
        
    except Exception as e:
        print(f"[ERROR] Query classification failed: {e}")
        # 폴백: 기본적으로 일반 질문으로 처리
        return {
            "type": "GENERAL_QUERY",
            "value": user_input,
            "confidence": 0.5
        }

def classify_query_sync(user_input: str) -> Dict[str, Any]:
    """동기 버전"""
    try:
        store_code_pattern = r'^[A-Z0-9]{10}$'
        if re.match(store_code_pattern, user_input.strip()):
            return {
                "type": "STORE_CODE",
                "value": user_input.strip(),
                "confidence": 1.0
            }
        
        result = Runner.run_sync(query_classifier_agent, user_input)
        return result.final_output
        
    except Exception as e:
        print(f"[ERROR] Query classification failed: {e}")
        return {
            "type": "GENERAL_QUERY",
            "value": user_input,
            "confidence": 0.5
        }

def extract_store_code(text: str) -> str:
    """텍스트에서 상점 코드를 추출"""
    store_code_pattern = r'[A-Z0-9]{10}'
    match = re.search(store_code_pattern, text)
    return match.group() if match else None

