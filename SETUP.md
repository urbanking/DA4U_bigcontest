# BigContest AI Agent - 설치 및 실행 가이드

## 📦 설치

### 1. Python 환경 설정
```bash
# Python 3.10+ 권장
python --version
```

### 2. 의존성 설치
```bash
# 프로젝트 루트에서 실행
pip install -r requirements.txt
```

### 3. 환경변수 설정
`.env` 파일이 프로젝트 루트에 있는지 확인:
- `GEMINI_API_KEY`: Gemini API 키
- `Google_Map_API_KEY`: Google Maps API 키
- `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`: Langfuse 모니터링 (선택)
- 기타 경로는 상대경로로 자동 설정됨

## 🚀 실행

### Streamlit 앱 실행
```bash
cd open_sdk/streamlit_app
streamlit run app.py
```

### 브라우저 접속
- 자동으로 열리지 않으면: http://localhost:8501

## 📁 프로젝트 구조

```
bigcontest_ai_agent/
├── requirements.txt          # 전체 의존성
├── .env                      # 환경변수 (상대경로 사용)
├── data/                     # 데이터 파일
│   └── matched_store_results.csv
├── agents_new/               # AI 에이전트
│   ├── google_map_mcp/      # Google Maps MCP
│   ├── marketing_agent/     # 마케팅 에이전트
│   ├── new_product_agent/   # 신제품 에이전트
│   ├── panorama_img_anal/   # 파노라마 분석
│   └── store_agent/         # 매장 분석
├── open_sdk/
│   └── streamlit_app/       # Streamlit UI
│       ├── app.py           # 메인 앱
│       ├── ai_agents/       # AI 상담 에이전트
│       │   ├── consultation_agent.py
│       │   └── query_classifier.py
│       └── utils/           # 유틸리티
│           └── store_search_processor.py
└── output/                  # 분석 결과 출력
    └── store_mcp_searches/  # MCP 검색 결과
```

## 🔧 주요 기능

### 1. 매장 분석 (5차원)
- Store Agent: 매장 성과 분석
- Marketing Agent: 마케팅 전략
- New Product Agent: 신메뉴 추천
- Panorama Analysis: 지역 특성
- Marketplace Analysis: 상권 분석

### 2. Google Maps MCP 검색
- 매장 리뷰, 평점, 영업시간
- 자동으로 txt 파일로 저장
- AI 상담에서 활용

### 3. AI 상담
- 분석 결과 기반 질의응답
- Google Maps 정보 통합
- Langfuse 모니터링

## 🛠️ 기술 스택

- **AI/LLM**: Gemini 2.5 Flash, OpenAI SDK
- **Framework**: LangChain, Streamlit
- **Monitoring**: Langfuse
- **Geospatial**: Geopandas, Folium
- **Visualization**: Plotly, Matplotlib, Seaborn

## 📝 사용 방법

1. **매장 코드 입력** (10자리)
   - 예: `000F03E44A`

2. **5차원 분석 대기** (3-5분)
   - Store, Marketing, New Product, Panorama, Marketplace

3. **상담 시작 버튼 클릭**
   - MCP 검색 자동 실행
   - New Product Agent 실행

4. **AI 상담 질문**
   - "매장 리뷰 분석해줘"
   - "영업시간은?"
   - "마케팅 전략은?"

## ⚠️ 주의사항

- 모든 경로는 **상대경로** 사용
- `.env` 파일 확인 필수
- Python 3.10+ 권장
- Gemini API 키 필요

## 🐛 문제 해결

### Import Error
```bash
# Python path 확인
python -c "import sys; print(sys.path)"
```

### API Key Error
```bash
# .env 파일 확인
cat .env | grep API_KEY
```

### Streamlit Error
```bash
# 캐시 삭제
streamlit cache clear
```

## 📞 문의

- GitHub: urbanking/DA4U_bigcontest
- Branch: chanwoo
