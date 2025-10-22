# 🚀 여기서 시작하세요!

## 📌 이 시스템은?

**주소를 입력하면 데이터 분석을 자동으로 해주는 AI 에이전트**

---

## ⚡ 가장 빠른 시작 (30초)

```bash
# 1. 환경 설정
pip install google-generativeai openai PyPDF2

# 2. 실행
python ultra_simple_agent.py "왕십리역" "외식업"

# 3. 결과 확인
# test_output/ 폴더에 결과 저장됨
```

**끝!**

---

## 🎯 선택하세요

### 옵션 1: 가장 간단 (추천!)

```bash
python ultra_simple_agent.py "주소" "업종"
```

- 파일 1개
- 모든 기능 포함
- 3-5분 완료

**가이드**: `ULTRA_SIMPLE_GUIDE.md`

---

### 옵션 2: LangGraph 버전 (고급)

```bash
python run_analysis.py "자연어 쿼리"
```

- 파일 7개
- 워크플로우 관리
- Review 포함

**가이드**: `AGENT_ARCHITECTURE.md`

---

## 📚 문서 선택 가이드

### 1. 빠르게 사용만 하고 싶다

→ `ULTRA_SIMPLE_GUIDE.md` (5분)

### 2. 전체 구조를 이해하고 싶다

→ `SIMPLE_STRUCTURE.md` (10분)

### 3. 깊이 이해하고 개발하고 싶다

→ `AGENT_ARCHITECTURE.md` (30분)

---

## 🏗️ 파일 맵

```
ultra_simple_agent.py          ← 🌟 시작은 여기!
├─ wrappers/
│  ├─ data_loader.py          ← 기존 데이터 로드
│  └─ marketplace_wrapper.py  ← Marketplace 실시간 분석
├─ panorama_img_anal/
│  └─ analyze_area_by_address.py  ← Panorama 실시간 분석
└─ utils/
   └─ gemini_client.py        ← Gemini API

test_output/                   ← 모든 결과 여기
```

---

## 🎮 사용 예제

```bash
# 왕십리역 카페
python ultra_simple_agent.py "왕십리역" "외식업"

# 성수역 편의점
python ultra_simple_agent.py "성수역" "소매업"

# 금호역 미용실
python ultra_simple_agent.py "금호역" "뷰티"
```

### 🧪 Mobility 데이터 테스트

```bash
# Mobility 데이터 로딩 확인
python test_mobility.py

# 결과 예시:
# 📍 테스트: 왕십리역
# ✓ 행정동 판단: 왕십리2동
# ✓ Mobility 데이터 로드 성공!
```

---

## 📊 실행 과정

```
입력: "왕십리역"
    ↓
┌──────────────────────┐
│ 1. Marketplace 실시간 │  3-4분
└──────────────────────┘
    ↓
┌──────────────────────┐
│ 2. Panorama 실시간    │  1-2분
└──────────────────────┘
    ↓
┌──────────────────────┐
│ 3. 기존 JSON 복사     │  1초
│   - 상권분석          │
│   - Mobility          │
│   - Store             │
└──────────────────────┘
    ↓
┌──────────────────────┐
│ 4. Gemini 종합 분석   │  10초
└──────────────────────┘
    ↓
┌──────────────────────┐
│ 5. 결과 저장          │  1초
│   - JSON              │
│   - TXT 리포트        │
└──────────────────────┘
    ↓
완료! (총 5분)
```

---

## ✅ 체크리스트

### 실행 전

- [ ] Python 설치됨
- [ ] `.env` 파일에 API 키 설정
- [ ] `data outputs/` 폴더 존재

### 실행 후

- [ ] `test_output/` 폴더에 파일 생성
- [ ] JSON 파일 확인
- [ ] TXT 리포트 읽기

---

## 💡 팁

### 빠른 테스트 (실시간 분석 건너뛰기)

```python
# ultra_simple_agent.py 수정
# _realtime_analysis() 부분 주석 처리하고
# 기존 데이터만 사용하면 즉시 완료!
```

### 비용 절감

```python
# Panorama 이미지 개수 줄이기
analyze_area_by_address(address, max_images=10)  # 20 → 10
```

---

## 🆘 도움말

문제가 생기면:

1. `ULTRA_SIMPLE_GUIDE.md` - 사용법
2. `SIMPLE_STRUCTURE.md` - 구조 이해
3. `AGENT_ARCHITECTURE.md` - 상세 설명

---

**지금 바로 실행해보세요!** 🎉

```bash
python ultra_simple_agent.py "왕십리역" "외식업"
```
