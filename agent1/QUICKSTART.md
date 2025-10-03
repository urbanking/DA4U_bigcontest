# 🚀 빠른 시작 가이드

## 📋 개요

이 가이드는 멀티 에이전트 상권 분석 시스템을 빠르게 설치하고 실행하는 방법을 안내합니다.

## ⚡ 5분 빠른 시작

### 1단계: 환경 준비

```bash
# Python 3.9+ 확인
python --version

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2단계: 의존성 설치

```bash
# 기본 의존성 설치
pip install -r requirements.txt

# 백엔드 의존성 설치
pip install -r requirements_backend.txt
```

### 3단계: 환경변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# OpenAI API 키 설정 (필수)
# .env 파일을 열어서 OPENAI_API_KEY 설정
echo "OPENAI_API_KEY=your_actual_api_key_here" >> .env
```

### 4단계: 시스템 실행

```bash
# FastAPI 서버 실행
cd backend/api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**새 터미널에서:**
```bash
# Streamlit 대시보드 실행
cd frontend
streamlit run streamlit_app.py --server.port 8501
```

### 5단계: 확인

- **API 서버**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **대시보드**: http://localhost:8501

## 🔧 상세 설치 가이드

### 시스템 요구사항

- **Python**: 3.9 이상
- **메모리**: 최소 4GB RAM
- **디스크**: 최소 2GB 여유 공간
- **네트워크**: 인터넷 연결 (OpenAI API 사용)

### 의존성 패키지

#### 핵심 패키지
```
fastapi==0.104.1
uvicorn==0.24.0
streamlit==1.28.1
langchain==0.1.0
langgraph==0.0.62
openai==1.3.0
```

#### 데이터 처리
```
pandas==2.1.3
numpy==1.24.3
plotly==5.17.0
sqlalchemy==2.0.23
```

#### 웹 스크래핑 & 컴퓨터 비전
```
selenium==4.15.2
beautifulsoup4==4.12.2
opencv-python==4.8.1.78
```

### 데이터베이스 설정 (선택사항)

```bash
# PostgreSQL 설치 (macOS)
brew install postgresql
brew services start postgresql

# PostgreSQL 설치 (Ubuntu)
sudo apt update
sudo apt install postgresql postgresql-contrib

# 데이터베이스 생성
createdb commercial_district_db

# 스키마 생성
psql -d commercial_district_db -f database/schema.sql
psql -d commercial_district_db -f database/memory_tables.sql
```

## 🧪 기본 테스트

### API 테스트

```bash
# API 서버 상태 확인
curl http://localhost:8000/

# 헬스 체크
curl http://localhost:8000/health

# 분석 요청 테스트
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"user_query": "왜 20대 고객이 줄어들고 있나요?", "user_id": "TEST_USER"}'
```

### Python 테스트

```python
import requests

# API 연결 테스트
response = requests.get("http://localhost:8000/")
print(response.json())

# 분석 요청 테스트
response = requests.post("http://localhost:8000/analyze", json={
    "user_query": "매출을 늘리기 위한 전략은?",
    "user_id": "TEST_USER_001"
})
print(response.json())
```

## 🎯 첫 번째 분석 실행

### Streamlit 대시보드 사용

1. **브라우저에서 http://localhost:8501 접속**
2. **분석 질문 입력**: "왜 20대 고객이 줄어들고 있나요?"
3. **분석 시작 버튼 클릭**
4. **결과 확인**: 
   - 실시간 분석 진행 상황
   - 각 에이전트별 결과
   - 마케팅 전략 제안
   - 실행 가능한 권장사항

### API 직접 호출

```python
import requests
import json

# 분석 요청
analysis_request = {
    "user_query": "경쟁사 대비 우리의 강점은 무엇인가요?",
    "user_id": "USER_001"
}

response = requests.post(
    "http://localhost:8000/analyze",
    json=analysis_request,
    timeout=60
)

if response.status_code == 200:
    result = response.json()
    print("분석 완료!")
    print(f"세션 ID: {result['session_id']}")
    print(f"상태: {result['status']}")
    print(f"결과: {result['message']}")
else:
    print(f"에러: {response.status_code}")
```

## 🔍 시스템 상태 확인

### API 엔드포인트 확인

```bash
# 기본 상태
curl http://localhost:8000/

# 헬스 체크
curl http://localhost:8000/health

# 에이전트 상태
curl http://localhost:8000/agents/status

# 사용자 히스토리 (사용자 ID 필요)
curl http://localhost:8000/user/USER_001/history
```

### 로그 확인

```bash
# FastAPI 로그 (터미널에서 확인)
# uvicorn 실행 시 실시간 로그 출력

# Streamlit 로그
# 브라우저 개발자 도구 콘솔에서 확인
```

## 🐛 문제 해결

### 자주 발생하는 문제

#### 1. 포트 충돌
```bash
# 포트 사용 중인 프로세스 확인
netstat -tulpn | grep :8000
netstat -tulpn | grep :8501

# 프로세스 종료
pkill -f uvicorn
pkill -f streamlit
```

#### 2. 의존성 문제
```bash
# 가상환경 재생성
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements_backend.txt
```

#### 3. OpenAI API 에러
```bash
# API 키 확인
echo $OPENAI_API_KEY

# .env 파일 확인
cat .env | grep OPENAI_API_KEY
```

#### 4. 데이터베이스 연결 실패
```bash
# PostgreSQL 서비스 상태 확인
pg_ctl status

# 연결 테스트
psql -h localhost -U postgres -d commercial_district_db
```

## 📈 다음 단계

### 1. 전문 에이전트 구현
- [구현 가이드](IMPLEMENTATION_GUIDE.md) 참조
- 각자 담당 에이전트 내부 로직 개발
- BaseAgent 클래스 상속하여 일관성 유지

### 2. 데이터베이스 연동
- PostgreSQL 설정 및 연결
- 메모리 시스템 구현
- 사용자 히스토리 저장

### 3. 고급 기능
- MCP Sequential Thinking 연동
- 평가 시스템 구현
- 실제 상권 데이터 분석

### 4. 프로덕션 배포
- [배포 가이드](DEPLOYMENT_GUIDE.md) 참조
- Docker 컨테이너화
- 클라우드 배포

## 🆘 도움말

### 문서
- [README.md](README.md): 프로젝트 개요
- [아키텍처 가이드](ARCHITECTURE_GUIDE.md): 시스템 구조
- [배포 가이드](DEPLOYMENT_GUIDE.md): 배포 방법
- [구현 가이드](IMPLEMENTATION_GUIDE.md): 개발 방법
- [시스템 상태](SYSTEM_STATUS.md): 현재 상태

### 지원
문제가 지속되면 다음을 확인하세요:
1. 시스템 요구사항 충족 여부
2. 환경변수 설정 정확성
3. 네트워크 연결 상태
4. 로그 파일의 에러 메시지

---

**🎉 축하합니다! 멀티 에이전트 상권 분석 시스템이 성공적으로 실행되었습니다!**