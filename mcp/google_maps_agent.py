"""
Google Maps Agent using MCP + LangChain + Gemini 2.5 Flash

주소나 매장명을 입력받아 Google Maps를 통해 리뷰 및 매장 정보를 제공하는 AI 에이전트
"""

import os
import json
import anyio
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# LangChain & MCP
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from langchain_core.messages import SystemMessage, HumanMessage


class GoogleMapsAgent:
    """
    Gemini 2.5 Flash + MCP Google Maps를 활용한 장소 검색 에이전트
    """
    
    def __init__(self):
        """
        에이전트 초기화
        - 환경 변수 로드
        - Gemini 2.5 Flash (OpenAI SDK) 설정
        - MCP Google Maps 서버 설정
        """
        # 환경 변수 로드
        load_dotenv()
        
        # API 키 확인
        self.google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        if not self.google_maps_api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY가 .env 파일에 설정되지 않았습니다.")
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY가 .env 파일에 설정되지 않았습니다.")
        
        # Gemini 2.5 Flash 설정 (OpenAI SDK 호환 모드)
        # Google AI Studio의 OpenAI 호환 엔드포인트 사용
        self.llm = ChatOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=self.google_api_key,
            model="gemini-2.0-flash-exp",  # Gemini 2.5 Flash
            temperature=0.3,
            max_tokens=2000,
        )
        
        # MCP Google Maps 서버 파라미터 설정
        self.maps_server = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-google-maps"],
            env={"GOOGLE_MAPS_API_KEY": self.google_maps_api_key}
        )
        
        print("✅ Google Maps Agent 초기화 완료")
        print(f"🤖 모델: Gemini 2.5 Flash")
        print(f"🗺️  MCP Google Maps 서버 준비됨\n")
    
    def search_place(self, query: str) -> str:
        """
        장소 검색 및 상세 정보 조회
        
        Args:
            query: 검색할 장소명 또는 주소 (예: "강남역 스타벅스", "서울시 강남구 역삼동")
            
        Returns:
            검색 결과 및 상세 정보를 포함한 텍스트
        """
        system_prompt = """당신은 Google Maps 정보를 활용하는 전문 어시스턴트입니다.

사용자가 장소명이나 주소를 입력하면 **반드시 다음 순서로 작업**하세요:

1. **먼저 maps_search_places로 장소를 검색**하여 place_id를 찾습니다.
2. **그 다음 maps_place_details로 상세 정보를 조회**합니다. (필수!)

최종 응답에는 다음 정보를 **모두** 포함해주세요:

📍 **기본 정보**
   - 장소명
   - 주소 (도로명주소)
   - 위치 (위도/경도)
   - 카테고리/업종

⭐ **평가 정보**
   - 평점 (별점/5.0)
   - 리뷰 개수
   - **모든 리뷰 전체 내용** (한글로 번역, 요약하지 말고 각 리뷰를 있는 그대로 출력)

📝 **리뷰 분석**
   - 👍 **장점**: 리뷰에서 언급된 긍정적인 점들을 구체적으로 나열
   - 👎 **단점**: 리뷰에서 언급된 부정적인 점들을 구체적으로 나열

🕐 **운영 정보**
   - 영업시간 (오늘 기준, 요일별 전체)
   - 현재 영업 중인지 여부
   - 연락처 (전화번호)
   - 웹사이트 (있는 경우)

💰 **가격대**
   - 가격대 정보 (있는 경우)

🏪 **추가 정보**
   - 편의시설 (주차, 와이파이 등)
   - 특징 및 인기 메뉴 (리뷰에서 추출)

**중요: 
1. 리뷰는 절대 요약하지 말고, 모든 리뷰의 전체 텍스트를 한글로 번역하여 그대로 나열하세요.
2. 영어나 다른 언어 리뷰는 반드시 한글로 번역하세요.
3. 리뷰 분석 섹션에서는 모든 리뷰를 종합하여 장점과 단점을 각각 구체적으로 나열하세요.**

검색 결과가 여러 개인 경우, 평점이 높고 리뷰가 많은 상위 3개를 추천하되, 
각각에 대해 place_details를 호출하여 상세 정보를 제공하세요.

정보는 한국어로 명확하고 읽기 쉽게 정리해주세요."""

        user_message = f"'{query}'에 대한 매장 정보와 리뷰를 찾아주세요. 반드시 place_details를 호출하여 영업시간, 연락처, **모든 리뷰 전체 내용(한글로 번역, 요약 없이)**을 가져오고, 리뷰 분석(장점/단점)도 포함하세요."
        
        result = self._query_google_maps(system_prompt, user_message)
        return result
    
    def query(self, question: str) -> str:
        """
        자유로운 형식의 질문 처리
        
        Args:
            question: 사용자 질문 (예: "명동에서 평점 좋은 한식당 추천해줘")
            
        Returns:
            답변 텍스트
        """
        system_prompt = """당신은 Google Maps 데이터를 활용하여 장소 추천과 정보를 제공하는 AI 어시스턴트입니다.

**작업 순서 (필수):**
1. maps_search_places로 장소 검색
2. 각 결과에 대해 maps_place_details로 상세 정보 조회
3. 모든 정보를 종합하여 응답

사용자의 질문을 이해하고 적절한 장소를 검색하여 다음과 같이 응답하세요:

📍 **검색 결과 요약**
- 검색한 지역과 조건
- 찾은 장소 개수

⭐ **추천 장소** (평점 순)
1. **[장소명]** - ⭐ [평점]/5.0 ([리뷰수] 리뷰)
   - 📍 주소
   - 🕐 영업시간 (오늘 기준 + 요일별 전체)
   - 📞 연락처
   - 💰 가격대
   - 💬 대표 특징 및 인기 메뉴
   - 📝 **전체 리뷰 내용** (한글로 번역, 요약하지 말고 모든 리뷰를 있는 그대로 출력)
   - 📊 **리뷰 분석**
     - 👍 장점: [구체적으로 나열]
     - 👎 단점: [구체적으로 나열]
   
2. [반복...]

💡 **추천 이유**
- 각 장소의 특징과 추천 포인트

**중요: 
1. 리뷰는 절대 요약하지 말고, 각 리뷰의 전체 텍스트를 한글로 번역하여 그대로 나열하세요.
2. 영어나 다른 언어 리뷰는 반드시 한글로 번역하세요.
3. 리뷰 분석에서는 모든 리뷰를 종합하여 장점과 단점을 각각 구체적으로 나열하세요.**

응답은 친절하고 읽기 쉽게 이모지와 함께 제공해주세요.
반드시 place_details를 호출하여 영업시간, 연락처 등 상세 정보를 포함하세요."""

        result = self._query_google_maps(system_prompt, question)
        return result
    
    def _query_google_maps(self, system_prompt: str, user_message: str) -> str:
        """
        내부 메서드: MCP Google Maps 도구를 사용하여 LLM 쿼리 실행
        
        Args:
            system_prompt: 시스템 프롬프트
            user_message: 사용자 메시지
            
        Returns:
            LLM 응답
        """
        async def _inner():
            # MCP 클라이언트 연결
            async with stdio_client(self.maps_server) as (read, write):
                async with ClientSession(read, write) as session:
                    # 세션 초기화
                    await session.initialize()
                    
                    # MCP 도구 로드
                    tools = await load_mcp_tools(session)
                    
                    print(f"📦 로드된 도구: {[tool.name for tool in tools]}")
                    
                    # ReAct 에이전트 생성
                    agent = create_react_agent(self.llm, tools)
                    
                    # 메시지 구성
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_message)
                    ]
                    
                    # 에이전트 실행
                    print("\n🔍 검색 중...\n")
                    response = await agent.ainvoke({"messages": messages})
                    
                    # 최종 응답 추출
                    final_message = response["messages"][-1]
                    return final_message.content
        
        # 비동기 함수 실행
        return anyio.run(_inner)
    
    def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """
        특정 장소의 상세 정보 조회 (Place ID 기반)
        
        Args:
            place_id: Google Maps Place ID
            
        Returns:
            장소 상세 정보 딕셔너리
        """
        query = f"Place ID '{place_id}'의 모든 상세 정보를 JSON 형식으로 제공해주세요."
        
        async def _inner():
            async with stdio_client(self.maps_server) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await load_mcp_tools(session)
                    agent = create_react_agent(self.llm, tools)
                    
                    response = await agent.ainvoke({"messages": query})
                    final_message = response["messages"][-1]
                    
                    # JSON 파싱 시도
                    try:
                        return json.loads(final_message.content)
                    except:
                        return {"raw_response": final_message.content}
        
        return anyio.run(_inner)


def main():
    """
    메인 함수: 사용 예시
    """
    print("=" * 60)
    print("Google Maps Agent with Gemini 2.5 Flash + MCP")
    print("=" * 60)
    
    try:
        # 에이전트 초기화
        agent = GoogleMapsAgent()
        
        # 예시 1: 특정 장소 검색
        print("\n" + "=" * 60)
        print("예시 1: 특정 매장 검색")
        print("=" * 60)
        result1 = agent.search_place("강남역 스타벅스")
        print(result1)
        
        # 예시 2: 자연어 질문
        print("\n" + "=" * 60)
        print("예시 2: 자연어 질문")
        print("=" * 60)
        result2 = agent.query("서울 명동에서 평점 4.5 이상인 한식당 3곳 추천해줘")
        print(result2)
        
        # 예시 3: 지역 기반 검색
        print("\n" + "=" * 60)
        print("예시 3: 지역 카페 검색")
        print("=" * 60)
        result3 = agent.query("홍대입구역 근처 조용한 카페 추천해줘. 콘센트 많고 와이파이 잘 되는 곳으로")
        print(result3)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
