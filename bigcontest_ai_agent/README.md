# BigContest AI Agent

LangGraph 기반 멀티에이전트 가게 분석 시스템

## 📋 프로젝트 개요

이 프로젝트는 LangGraph를 활용한 멀티에이전트 시스템으로, 가게의 상권, 업종, 접근성 등을 종합적으로 분석하고 맞춤형 마케팅 전략을 제안합니다.

## 🏗️ 아키텍처

```
bigcontest_ai_agent/
│
├── backend/                    # ⚙️ FastAPI 서버
│   ├── core/                   # 핵심 설정 및 유틸리티
│   ├── routers/                # API 라우터
│   ├── services/               # 비즈니스 로직
│   ├── models/                 # ORM 모델
│   └── schemas/                # Pydantic 스키마
│
├── agents/                     # 🧠 LangGraph 기반 에이전트
│   ├── langgraph_workflows/    # 워크플로우 정의
│   ├── store_agent/            # 가게 분석 에이전트
│   ├── marketing_agent/        # 마케팅 전략 에이전트
│   └── orchestrator/           # 전체 오케스트레이터
│
├── frontend/                   # 🌐 Streamlit 프론트엔드
│   ├── pages/                  # 페이지 컴포넌트
│   ├── components/             # UI 컴포넌트
│   └── utils/                  # 유틸리티
│
├── configs/                    # ⚙️ 설정 파일
├── outputs/                    # 📦 결과 저장
└── tests/                      # ✅ 테스트 스위트
```

## 🚀 주요 기능

### 🏪 Store Report
- 상권 분석 (Commercial Analysis)
- 업종 분석 (Industry Analysis)
- 접근성 분석 (Accessibility Analysis)
- 이동데이터 분석 (Mobility Analysis)

### 📈 Metrics Dashboard
- **CVI** (Commercial Viability Index): 상권 활성도 지수
- **ASI** (Accessibility Score Index): 접근성 지수
- **SCI** (Store Competitiveness Index): 점포 경쟁력 지수
- **GMI** (Growth & Market Index): 성장 및 시장 지수

### 🩺 Diagnostic Report
- 지표 기반 문제 진단
- 심각도별 이슈 분류 (Critical, Warning, Info)
- 개선 권고사항 제시

### 💡 Marketing Strategy
- 인사이트 추출 (SWOT 분석)
- 타깃 고객 세그먼트 식별
- 맞춤형 마케팅 전략 제안
- KPI 효과 예측

## 🛠️ 설치 및 실행

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Mac/Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 필요한 환경 변수를 설정하세요:

```bash
# .env.example을 복사
cp .env.example .env

# .env 파일을 수정하여 API 키 등을 입력
```

### 3. 데이터베이스 설정

```bash
# PostgreSQL 데이터베이스 생성
createdb bigcontest_db

# 마이그레이션 실행 (선택사항)
alembic upgrade head
```

### 4. 서버 실행

#### FastAPI 백엔드 실행
```bash
cd bigcontest_ai_agent
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### Streamlit 프론트엔드 실행
```bash
cd bigcontest_ai_agent/frontend
streamlit run Home.py --server.port 8501
```

## 📡 API 엔드포인트

### Store Report
- `GET /api/store/{store_code}` - 가게 리포트 조회
- `POST /api/store/{store_code}/generate` - 가게 리포트 생성

### Metrics
- `GET /api/metrics/{store_code}` - 지표 조회
- `POST /api/metrics/{store_code}/calculate` - 지표 계산

### Diagnostic
- `GET /api/diagnostic/{store_code}` - 진단 결과 조회
- `POST /api/diagnostic/{store_code}/diagnose` - 진단 실행

### Marketing
- `GET /api/marketing/{store_code}` - 마케팅 전략 조회
- `POST /api/marketing/{store_code}/generate` - 마케팅 전략 생성

### Orchestrator
- `POST /api/run/{store_code}` - 전체 파이프라인 실행
- `GET /api/run/{store_code}/status` - 파이프라인 상태 조회

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest

# 커버리지 포함
pytest --cov=agents --cov=backend

# 특정 테스트 파일 실행
pytest tests/test_store_agent.py
```

## 📝 설정 파일

### configs/weights.yml
지표 가중치 설정

### configs/thresholds.yml
경고 임계값 설정

### configs/prescriptions.yml
지표별 개선 액션 매핑

### configs/langgraph.yml
LangGraph 워크플로우 설정

### configs/paths.yml
파일 경로 설정

## 🔄 워크플로우

### Store Workflow
```
리포트 생성 → 지표 계산 → 진단 실행
```

### Marketing Workflow
```
인사이트 추출 → 타깃 매칭 → 전략 생성 → KPI 예측
```

### Orchestrator Workflow
```
Store Workflow → Marketing Workflow → 결과 통합
```

## 📂 출력 파일

### outputs/reports/
- `store_report_{store_code}.json`

### outputs/metrics/
- `store_metrics_{store_code}.json`

### outputs/diagnostics/
- `store_diagnostic_{store_code}.json`

### outputs/marketing/
- `marketing_strategy_report_{store_code}.json`

## 🤝 기여

이 프로젝트는 BigContest AI Agent 프로젝트의 일환으로 개발되었습니다.

## 📄 라이선스

MIT License

## 📧 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

---

Made with ❤️ by BigContest Team

