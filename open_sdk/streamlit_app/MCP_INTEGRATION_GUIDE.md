# MCP 매장 검색 통합 가이드

## 개요
Streamlit 앱에 Google Maps MCP를 이용한 매장 검색 기능이 통합되었습니다.

## 작동 방식

### 1. 사용자 입력
- Streamlit 앱에서 **10자리 매장 코드** 입력 (예: `000F03E44A`)

### 2. 자동 실행 흐름
```
매장 코드 입력
    ↓
기존 분석 실행 (5차원 분석)
    ↓
"💬 상담 시작" 버튼 클릭
    ↓
통합 분석 파일 로드
    ↓
New Product Agent 실행 (네이버 크롤링)
    ↓
⭐ MCP를 통한 Google Maps 검색 ⭐ (여기서 실행!)
    ↓
결과를 output 폴더에 txt 파일로 저장
    ↓
Langchain Consultation Chain 생성
    ↓
상담 모드 활성화
```

### 3. 검색 쿼리 우선순위
1. **매칭_상호명 + 매칭_주소** (가장 높은 우선순위)
2. **입력_가맹점명 + 입력_주소**
3. **입력_주소만**

## 파일 구조

### 핵심 파일
```
open_sdk/streamlit_app/
├── app.py                          # Streamlit 메인 앱 (MCP 통합됨)
└── utils/
    ├── __init__.py                 # StoreSearchProcessor export
    └── store_search_processor.py   # MCP 검색 로직
```

### 의존성
```
agents_new/google_map_mcp/
└── google_maps_agent.py            # GoogleMapsAgent 클래스
```

### 데이터
```
data/
└── matched_store_results.csv       # 매장 정보 CSV
```

### 출력
```
open_sdk/streamlit_app/output/
└── {매장코드}_{타임스탬프}.txt     # MCP 검색 결과
```

## 사용 예시

### 1. Streamlit 앱에서 사용
```bash
cd c:\ㅈ\DA4U\bigcontest_ai_agent\open_sdk\streamlit_app
streamlit run app.py
```

1. 앱 시작
2. 채팅창에 매장 코드 입력: `000F03E44A`
3. 자동으로 MCP 검색 실행
4. "✅ MCP 매장 검색 완료!" 메시지 확인
5. 기존 분석 계속 진행

### 2. 단독 테스트
```bash
cd c:\ㅈ\DA4U\bigcontest_ai_agent\open_sdk\streamlit_app\utils
python store_search_processor.py
```

## 코드 예시

### StoreSearchProcessor 사용
```python
from utils.store_search_processor import StoreSearchProcessor
from pathlib import Path

# CSV 경로
csv_path = Path("data/matched_store_results.csv")

# 프로세서 생성
processor = StoreSearchProcessor(csv_path=str(csv_path))

# 매장 검색 및 저장
result = processor.search_and_save_store("000F03E44A")

if result["success"]:
    print(f"검색 성공! 저장 파일: {result['file']}")
else:
    print(f"검색 실패: {result['error']}")
```

### 반환값 구조
```python
{
    "success": True,              # 성공 여부
    "store_code": "000F03E44A",   # 매장 코드
    "file": "path/to/output.txt", # 저장 파일 경로
    "result": "검색 결과 텍스트"   # Google Maps 검색 결과
}
```

## 통합 코드 위치

### app.py 수정 내역
1. **Line ~2173**: Agent 사용 시 MCP 검색 추가
2. **Line ~2287**: Agent 미사용 시 MCP 검색 추가

```python
# MCP 매장 검색 실행
try:
    from utils.store_search_processor import StoreSearchProcessor
    csv_path = Path(__file__).parent.parent.parent / "data" / "matched_store_results.csv"
    
    if csv_path.exists():
        with st.spinner(f"🔍 MCP로 매장 '{store_code}' 정보를 검색 중..."):
            processor = StoreSearchProcessor(csv_path=str(csv_path))
            mcp_result = processor.search_and_save_store(store_code)
            
            if mcp_result.get("success"):
                output_file = mcp_result.get("file", "")
                st.success(f"✅ MCP 매장 검색 완료! 결과: {output_file}")
                print(f"[MCP] 매장 검색 성공: {store_code} -> {output_file}")
except Exception as e:
    print(f"[MCP ERROR] 매장 검색 오류: {e}")
```

## 주요 메서드

### `search_and_save_store(store_code: str)`
특정 매장 코드에 대해 MCP 검색을 실행하고 결과를 txt 파일로 저장

**Args:**
- `store_code`: 10자리 매장 코드 (예: "000F03E44A")

**Returns:**
```python
{
    "success": bool,         # 성공 여부
    "store_code": str,       # 매장 코드
    "file": str,            # 저장 파일 경로
    "result": str,          # 검색 결과 텍스트
    "error": str            # (실패 시) 에러 메시지
}
```

## 트러블슈팅

### Import Error
```
ImportError: cannot import name 'GoogleMapsAgent'
```
**해결:** `__init__.py` 파일들이 올바르게 생성되었는지 확인
- `bigcontest_ai_agent/__init__.py`
- `agents_new/__init__.py`
- `agents_new/google_map_mcp/__init__.py`
- `open_sdk/__init__.py`
- `open_sdk/streamlit_app/utils/__init__.py`

### CSV Not Found
```
⚠️ CSV 파일을 찾을 수 없습니다
```
**해결:** `data/matched_store_results.csv` 파일 존재 확인

### MCP Agent 초기화 실패
```
Google Maps Agent가 초기화되지 않았습니다
```
**해결:**
1. `google_maps_agent.py`의 MCP 서버 경로 확인
2. npm으로 `@modelcontextprotocol/server-google-maps` 설치 확인
3. `GOOGLE_MAPS_API_KEY` 환경변수 설정 확인

## 변경 사항 요약

### 추가된 파일
- ✅ `store_search_processor.py`: MCP 검색 로직
- ✅ `MCP_INTEGRATION_GUIDE.md`: 이 문서

### 수정된 파일
- ✅ `app.py`: MCP 검색 통합 (2곳)
- ✅ `utils/__init__.py`: StoreSearchProcessor export

### 삭제된 기능
- ❌ 앱 시작 시 모든 매장 배치 검색 (초기 구현)
  - 이유: 사용자가 입력한 단일 매장 코드만 검색하는 것이 올바른 동작

## 다음 단계

1. **테스트**: 실제 매장 코드로 end-to-end 테스트
2. **최적화**: 검색 결과 캐싱 (동일 매장 재검색 방지)
3. **UI 개선**: MCP 검색 결과를 Streamlit UI에 표시
4. **에러 핸들링**: 더 상세한 에러 메시지 및 복구 로직

## 참고 문서
- `agents_new/google_map_mcp/google_maps_agent.py`: GoogleMapsAgent 구현
- `data/matched_store_results.csv`: CSV 파일 형식
- Model Context Protocol: https://modelcontextprotocol.io
