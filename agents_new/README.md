# 📊 데이터 분석 에이전트

상권 · 매장 · 이동 데이터 종합 분석 시스템

## 🎯 프로젝트 개요

이 프로젝트는 다양한 데이터 소스를 통합하여 상권 및 매장 분석을 자동화하는 AI 에이전트입니다.

**주요 기능:**
- 🏪 **Marketplace 분석**: 서울시 골목상권분석 시스템 자동 분석
- 🏞️ **Panorama 분석**: GPT-4o Vision을 활용한 거리 이미지 분석
- 🚶 **Mobility 분석**: 행정동별 이동 패턴 분석
- 🏬 **Store 분석**: 매장 고객 데이터 분석
- 🤖 **AI 종합 분석**: Gemini를 통한 인사이트 생성
- 🎨 **자동 시각화**: 차트 및 그래프 자동 생성

## 🚀 사용 방법

### 방법 1: 웹 버전 (권장) ✨

브라우저에서 클릭 몇 번으로 분석 완료!

```bash
# 1. 의존성 설치
pip install -r backend/requirements.txt

# 2. 서버 실행
python backend/api.py

# 3. 브라우저 접속
# → http://localhost:8000
```

**특징:**
- ✅ 사용자 친화적 UI
- ✅ 실시간 진행 상황 표시
- ✅ 결과 웹에서 바로 확인
- ✅ 파일 다운로드 클릭 한 번

📖 **자세한 가이드**: [`HOW_TO_RUN_WEB.md`](HOW_TO_RUN_WEB.md)

### 방법 2: CLI 버전 (개발자용)

터미널에서 직접 실행:

```bash
python ultra_simple_agent.py "왕십리역" "외식업"
```

📖 **자세한 가이드**: [`START_HERE_SIMPLE.md`](START_HERE_SIMPLE.md)

## 📁 프로젝트 구조

```
agents_new/
├── 🌐 웹 버전 (새로 추가!)
│   ├── backend/
│   │   ├── api.py              # FastAPI 서버
│   │   ├── agent_service.py    # WebSocket 연동
│   │   ├── requirements.txt
│   │   ├── run.bat            # Windows 실행 스크립트
│   │   └── README.md
│   ├── frontend/
│   │   ├── index.html         # 메인 UI
│   │   ├── app.js             # JavaScript
│   │   ├── style.css          # 스타일
│   │   └── README.md
│   └── HOW_TO_RUN_WEB.md      # 웹 버전 가이드
│
├── 💻 CLI 버전 (기존 유지)
│   ├── ultra_simple_agent.py   # 메인 에이전트
│   ├── visualize_mobility.py   # Mobility 시각화
│   ├── visualize_store.py      # Store 시각화
│   └── START_HERE_SIMPLE.md    # CLI 가이드
│
├── 🔧 유틸리티
│   ├── utils/
│   │   └── gemini_client.py    # Gemini API 클라이언트
│   ├── wrappers/
│   │   ├── data_loader.py      # 데이터 로더
│   │   └── marketplace_wrapper.py
│   └── requirements.txt        # Python 의존성
│
├── 📊 분석 모듈
│   ├── marketplcae_anal/       # 상권 분석
│   ├── panorama_img_anal/      # 파노라마 분석
│   └── store_agent/            # 매장 분석
│
└── 📂 데이터 & 결과
    ├── data outputs/           # 기존 분석 데이터
    └── test_output/            # 분석 결과 저장
```

## 🛠️ 기술 스택

### Backend
- Python 3.10+
- FastAPI (웹 프레임워크)
- WebSocket (실시간 통신)
- Google Gemini (AI 분석)
- OpenAI GPT-4o (이미지 분석)

### Frontend
- Vanilla JavaScript (의존성 없음!)
- HTML5 + CSS3
- WebSocket API

### 분석 도구
- Pandas (데이터 처리)
- Matplotlib (시각화)
- GeoPandas (지리 데이터)
- Playwright (브라우저 자동화)

## 📊 분석 프로세스

```
1. 실시간 분석 (3-5분)
   ├─ Marketplace: 골목상권분석 시스템 자동화
   └─ Panorama: 거리뷰 이미지 AI 분석

2. 데이터 복사 (10초)
   ├─ 상권 분석 데이터
   ├─ Mobility 데이터 (행정동별 이동)
   └─ Store 데이터 (매장 고객)

3. AI 종합 분석 (30초)
   └─ Gemini: 모든 데이터 종합 인사이트

4. 결과 저장 (5초)
   ├─ JSON (상세 데이터)
   └─ TXT (리포트)

5. 자동 시각화 (30초)
   ├─ Mobility 차트 (7개)
   └─ Store 차트 (8개)
```

**총 소요 시간: 약 4-6분**

## 🎨 결과 예시

### 생성되는 파일들

```
test_output/
├── final_analysis_20251015_133108.json    # AI 종합 분석
├── final_report_20251015_133108.txt       # 텍스트 리포트
├── marketplace_report_20251015_133622.png # 상권 분석 레포트
├── marketplace_report_20251015_133622.pdf # PDF 버전
├── panorama_20251015_133655.json          # 파노라마 분석
├── 상권분석_20251015_133108.json          # 상권 데이터
├── mobility_20251015_133108.json          # 이동 데이터
├── store_20251015_133108.json             # 매장 데이터
├── mobility_viz_*/                         # Mobility 차트 7개
└── store_viz_*/                            # Store 차트 8개
```

### AI 분석 결과 예시

```json
{
  "핵심_인사이트": [
    "현대적 상업 건물과 교통량이 많은 도로가 특징",
    "개발 잠재력이 높은 지역",
    "초기 투자 시 리스크 고려 필요"
  ],
  "강점": [
    "현대적 상업 건물의 존재",
    "교통량이 많은 도로로 인한 접근성",
    "개발 잠재력이 높은 지역"
  ],
  "추천사항": [
    "소규모 투자로 시작하여 점진적 확장",
    "지역 커뮤니티와의 협력 강화",
    "초기 마케팅 전략 수립"
  ]
}
```

## 🔑 환경 설정

### 1. API 키 설정

`.env` 파일 생성:

```bash
# Gemini API (필수)
GOOGLE_API_KEY=your_gemini_api_key

# OpenAI API (Panorama 분석용, 필수)
OPENAI_API_KEY=your_openai_api_key

# Kakao API (선택, 주소 검색 정확도 향상)
KAKAO_REST_API_KEY=your_kakao_api_key
```

### 2. 의존성 설치

#### CLI 버전
```bash
pip install -r requirements.txt
```

#### 웹 버전 (추가)
```bash
pip install -r backend/requirements.txt
```

## 📖 문서

- 🌐 **웹 버전 가이드**: [`HOW_TO_RUN_WEB.md`](HOW_TO_RUN_WEB.md)
- 💻 **CLI 버전 가이드**: [`START_HERE_SIMPLE.md`](START_HERE_SIMPLE.md)
- 🔧 **Backend API**: [`backend/README.md`](backend/README.md)
- 🎨 **Frontend**: [`frontend/README.md`](frontend/README.md)

## 🆚 CLI vs Web 비교

| 기능 | CLI 버전 | Web 버전 |
|------|----------|----------|
| **실행** | `python ultra_simple_agent.py '왕십리역'` | 브라우저 클릭 |
| **진행 상황** | 터미널 텍스트 | 실시간 UI + 진행바 |
| **결과 확인** | JSON 파일 열기 | 웹에서 즉시 표시 |
| **다운로드** | 폴더에서 찾기 | 버튼 클릭 |
| **사용 대상** | 개발자 | 일반 사용자 |
| **코드 재사용** | ✅ 100% | ✅ 100% |

## 🎯 사용 사례

### 1. 창업 컨설팅
- 특정 지역의 상권 분석
- 업종별 성공 가능성 평가
- 경쟁 환경 분석

### 2. 부동산 투자
- 지역 발전 가능성 평가
- 상권 활성화 지표 분석
- 임대료 적정성 판단

### 3. 마케팅 전략
- 타겟 고객 분석
- 최적 입지 선정
- 경쟁사 분석

## 🤝 기여

이 프로젝트는 Big Contest AI Agent 프로젝트의 일부입니다.

## 📄 라이선스

이 프로젝트는 내부 사용 목적으로 제작되었습니다.

## 🎉 시작하기

### 웹 버전 (초간단!)

```bash
# 1. 백엔드 의존성 설치
pip install -r backend/requirements.txt

# 2. 서버 시작
cd backend
python api.py

# 3. 브라우저 열기
# → http://localhost:8000
```

### CLI 버전 (개발자용)

```bash
# 의존성 설치
pip install -r requirements.txt

# 분석 실행
python ultra_simple_agent.py "왕십리역" "외식업"
```

---

💡 **Tip**: 웹 버전이 더 사용하기 쉽습니다! CLI는 기존 코드 100% 유지되므로 개발자는 계속 사용 가능합니다.

