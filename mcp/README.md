# Google Maps Agent with MCP + LangChain + Gemini 2.5 Flash

LangChain + MCP Server를 활용하여 Gemini 2.5 Flash가 Google Maps 정보를 검색하고 리뷰 및 매장 정보를 제공하는 AI 에이전트입니다.

## 주요 기능

- 📍 **주소/매장명 기반 검색**: 자연어로 장소를 검색
- ⭐ **리뷰 정보 제공**: 평점, 리뷰 개수, 사용자 평가
- 🏪 **상세 매장 정보**: 영업시간, 연락처, 주소 등
- 🤖 **Gemini 2.5 Flash 사용**: OpenAI SDK 호환 모드로 Google의 최신 모델 활용

## 설치 방법

### 1. Node.js 설치 (MCP 서버용)
MCP Google Maps 서버는 Node.js 기반으로 실행됩니다.

```bash
# Node.js LTS 버전 설치 확인
node --version
npm --version
```

### 2. Python 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 만들고 API 키를 설정합니다:

```bash
copy .env.example .env
```

`.env` 파일 수정:
```
GOOGLE_MAPS_API_KEY=여기에_구글맵스_API_키_입력
GOOGLE_API_KEY=여기에_구글_제미나이_API_키_입력
```

#### API 키 발급 방법

**Google Maps API Key:**
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 생성 또는 선택
3. "API 및 서비스" → "라이브러리"로 이동
4. 다음 API 활성화:
   - Places API (New)
   - Places API
   - Geocoding API
   - Directions API
5. "API 및 서비스" → "사용자 인증 정보"에서 API 키 생성

**Google AI API Key (Gemini):**
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. "Get API Key" 클릭하여 발급

## 사용 방법

### 기본 실행

```bash
python google_maps_agent.py
```

### 사용 예시

```python
from google_maps_agent import GoogleMapsAgent

# 에이전트 초기화
agent = GoogleMapsAgent()

# 매장 검색
result = agent.search_place("강남역 스타벅스")
print(result)

# 또는 특정 질문
result = agent.query("서울 명동에 있는 평점 좋은 한식당 추천해줘")
print(result)
```

## 코드 구조

```
mcp/
├── google_maps_agent.py    # 메인 에이전트 코드
├── requirements.txt         # Python 패키지 의존성
├── .env                     # 환경 변수 (직접 생성)
├── .env.example            # 환경 변수 예시
└── README.md               # 이 파일
```

## 주요 기능 설명

### 1. MCP Google Maps 연동
- `@modelcontextprotocol/server-google-maps`를 통해 Google Maps API 호출
- 장소 검색, 상세 정보 조회, 지오코딩 등 지원

### 2. LangChain Agent
- ReAct 패턴 기반 에이전트
- 사용자 질문을 분석하여 적절한 도구 선택 및 실행

### 3. Gemini 2.5 Flash
- OpenAI SDK 호환 모드로 실행
- 빠른 응답 속도와 높은 정확도

## 문제 해결

### npx 명령어를 찾을 수 없음
Node.js가 제대로 설치되었는지 확인하고 PATH에 추가되어 있는지 확인하세요.

### API 키 오류
`.env` 파일이 올바르게 생성되었는지, API 키가 유효한지 확인하세요.

### MCP 서버 연결 실패
방화벽 설정을 확인하고, Node.js가 정상적으로 실행되는지 확인하세요.

## 참고 자료

- [MCP Google Maps 심층 분석](https://skywork.ai/skypage/ko/mcp-server-google-maps)
- [Inferless MCP Google Maps Tutorial](https://docs.inferless.com/cookbook/google-map-agent-using-mcp)
- [LangChain MCP Adapters](https://python.langchain.com/docs/integrations/tools/mcp)
