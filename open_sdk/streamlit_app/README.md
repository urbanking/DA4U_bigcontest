# BigContest AI Agent - Streamlit App

## 개요
OpenAI Agents SDK를 활용한 5차원 매장 분석 및 AI 상담 시스템

## 주요 기능

### 1. Query Classification (입력 분류)
- **Query Agent** 사용
- 10자리 상점 코드 자동 인식
- 일반 질문과 코드 입력 구분

### 2. 5차원 분석
- **Store Agent**: 매장 종합 분석
- **Marketing Agent**: 마케팅 전략 생성
- **Mobility**: 이동 패턴 분석
- **Panorama**: 지역 환경 분석 (AI 비전)
- **Marketplace**: 상권 분석

### 3. 시각화
- 각 탭(고객분석, 이동분석, 파노라마 등)에 차트/이미지 자동 연결
- 공간 분석 지도 표시
- 파노라마 이미지 갤러리

### 4. AI Consultation (상담)
- **Consultation Agent** 사용
- SQLiteSession으로 대화 기록 유지
- 모든 분석 결과를 통합하여 컨텍스트로 제공
- Gemini 2.5 Flash 모델 사용

## 실행 방법

```bash
# Streamlit 실행
streamlit run open_sdk/streamlit_app/app.py --server.port 8517
```

## 워크플로우

```
1. 사용자 접속
2. 상점 코드 입력 (예: 000F03E44A)
3. Query Agent가 입력 분류
4. 5차원 분석 실행 (3-5분 소요)
   - Store Agent
   - Marketing Agent
   - Mobility
   - Panorama
   - Marketplace
5. 결과 표시 (탭별로 구분)
   - 개요
   - 고객 분석 + 차트
   - 이동 패턴 + 차트
   - 지역 분석 + 파노라마 이미지
   - 상권 분석
   - 마케팅 전략
   - 시각화 종합
6. 💬 상담 시작 버튼 클릭
7. Consultation Agent 활성화
8. 자유로운 질의응답
```

## 기술 스택
- **Streamlit**: 웹 UI
- **OpenAI Agents SDK**: Query Agent, Consultation Agent
- **Gemini 2.5 Flash**: LLM 모델
- **SQLiteSession**: 대화 기록 유지
- **Matplotlib + Noto Sans KR**: 한글 차트

## 폴더 구조
```
open_sdk/streamlit_app/
├── app.py                  # 메인 앱
├── ai_agents/             # AI Agents
│   ├── __init__.py
│   ├── query_agent.py     # Query Classifier
│   └── consultation_agent.py  # Consultation Agent
├── sessions/              # SQLite 세션 DB
└── README.md
```

## 환경 변수
- `GEMINI_API_KEY`: Gemini API 키
- `GOOGLE_MAPS_API_KEY`: Google Maps API 키 (지오코딩)

## 주의사항
- 분석은 약 3-5분 소요
- 상담 모드는 분석 완료 후 활성화
- 모든 결과는 `open_sdk/output` 폴더에 저장

