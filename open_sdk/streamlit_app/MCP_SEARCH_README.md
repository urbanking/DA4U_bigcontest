# MCP 매장 검색 기능 가이드

## 📋 개요

Streamlit 앱 시작 시 `matched_store_results.csv` 파일의 모든 매장 정보를 Google Maps MCP를 통해 자동으로 검색하고 결과를 txt 파일로 저장하는 기능입니다.

## 🚀 작동 방식

### 1. 앱 시작 시 자동 실행
- Streamlit 앱이 처음 실행되면 자동으로 MCP 매장 검색이 시작됩니다
- 최초 1회만 실행되며, 이후에는 세션이 유지되는 동안 다시 실행되지 않습니다
- 검색 결과는 `open_sdk/output/store_mcp_searches/` 폴더에 저장됩니다

### 2. 검색 프로세스
1. `matched_store_results.csv` 파일 로드
2. 각 매장에 대해 Google Maps MCP를 통해 검색 수행
3. 검색 결과를 개별 txt 파일로 저장
4. 전체 요약을 JSON 파일로 저장

### 3. 출력 파일
- **개별 매장 정보**: `{매장코드}_{타임스탬프}.txt`
- **전체 요약**: `summary_{타임스탬프}.json`

## 📁 파일 구조

```
open_sdk/
├── streamlit_app/
│   ├── app.py                    # 메인 앱 (MCP 검색 초기화 추가됨)
│   └── utils/
│       └── store_search_processor.py  # MCP 검색 프로세서
└── output/
    └── store_mcp_searches/       # 검색 결과 저장 폴더
        ├── {매장코드}_{타임스탬프}.txt
        ├── {매장코드}_{타임스탬프}.txt
        └── summary_{타임스탬프}.json
```

## 🔧 설정

### 검색 매장 수 제한
기본적으로 테스트를 위해 처음 10개 매장만 검색합니다. 전체 매장을 검색하려면:

**app.py의 2143번째 줄 근처에서 수정**:
```python
# 현재 (처음 10개만)
results = processor.process_all_stores(limit=10, save_progress=True)

# 전체 매장 검색으로 변경
results = processor.process_all_stores(limit=None, save_progress=True)
```

### 자동 검색 비활성화
앱 시작 시 자동 검색을 비활성화하려면:

**app.py의 2140번째 줄 근처를 주석 처리**:
```python
# MCP 매장 검색 초기화 비활성화
# if not st.session_state.mcp_search_initialized:
#     ...
```

## 📊 검색 결과 형식

### 개별 매장 txt 파일 예시
```
================================================================================
매장 코드: 000F03E44A
검색 쿼리: 육육면관 대한민국 서울특별시 성동구 왕십리로4가길 9
검색 시간: 2025-10-23T15:30:45
================================================================================

✅ 검색 성공

검색 결과:
--------------------------------------------------------------------------------
📍 기본 정보
   - 장소명: 육육면관
   - 주소: 대한민국 서울특별시 성동구 왕십리로4가길 9
   - 위치: 37.5454055, 127.0463356
   - 카테고리: restaurant, food

⭐ 평가 정보
   - 평점: 4.3/5.0
   - 리뷰 개수: 20개
   - 리뷰 전체 내용: ...

📝 리뷰 분석
   - 👍 장점: ...
   - 👎 단점: ...

🕐 운영 정보
   - 영업시간: ...
   - 연락처: ...
--------------------------------------------------------------------------------
```

### 요약 JSON 파일 예시
```json
{
  "total": 10,
  "success_count": 8,
  "failed_count": 2,
  "results": [
    {
      "store_code": "000F03E44A",
      "status": "success",
      "file": "c:/path/to/output/000F03E44A_20251023_153045.txt"
    },
    {
      "store_code": "002816BA73",
      "status": "failed",
      "error": "No results found"
    }
  ]
}
```

## 🛠️ 수동 실행 (테스트)

프로세서를 직접 실행하여 테스트할 수 있습니다:

```bash
# 프로젝트 루트에서
cd open_sdk/streamlit_app/utils
python store_search_processor.py
```

## 📋 요구 사항

### 환경 변수 (.env)
```env
# Google Maps API 키
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Google AI API 키 (Gemini)
GOOGLE_API_KEY=your_google_api_key
```

### 필수 패키지
```
langchain-mcp-adapters
langchain-openai
mcp
anyio
python-dotenv
pandas
```

## 🎯 사용 시나리오

### 1. 최초 앱 실행
```
1. Streamlit 앱 실행
2. MCP 매장 검색 자동 시작
3. 진행 상황 표시
4. 완료 메시지 표시
5. 검색 결과 통계 표시
```

### 2. 검색 결과 확인
```
1. 앱 좌측 상단 "🔍 MCP 매장 검색 결과" 확장
2. 총 매장, 성공, 실패 수 확인
3. output/store_mcp_searches/ 폴더에서 상세 결과 확인
```

## 🔍 검색 우선순위

매장 검색 시 다음 순서로 쿼리를 생성합니다:

1. **매칭된 상호명 + 매칭된 주소**
   ```
   예: "육육면관 대한민국 서울특별시 성동구 왕십리로4가길 9"
   ```

2. **입력 매장명 + 입력 주소**
   ```
   예: "육육** 서울특별시 성동구 왕십리로4가길 9"
   ```

3. **주소만**
   ```
   예: "서울특별시 성동구 왕십리로4가길 9"
   ```

## 🚨 문제 해결

### Q: MCP 검색이 실행되지 않아요
**A**: 다음 사항을 확인하세요:
1. `.env` 파일에 `GOOGLE_MAPS_API_KEY`와 `GOOGLE_API_KEY`가 설정되어 있는지
2. `matched_store_results.csv` 파일이 `data/` 폴더에 있는지
3. 브라우저 콘솔이나 터미널에 에러 메시지가 있는지

### Q: 검색이 너무 느려요
**A**: `limit` 파라미터를 조정하세요:
```python
# 테스트용: 처음 5개만
results = processor.process_all_stores(limit=5, save_progress=True)

# 전체 검색 (느림)
results = processor.process_all_stores(limit=None, save_progress=True)
```

### Q: 이미 검색한 결과를 다시 검색하고 싶어요
**A**: 세션 상태를 초기화하세요:
```python
# Streamlit 앱 재시작 또는
# 브라우저에서 페이지 새로고침 (Ctrl + R)
```

## 📝 주의사항

1. **API 사용량**: Google Maps API와 Gemini API 사용량에 주의하세요
2. **처리 시간**: 전체 매장 검색 시 오래 걸릴 수 있습니다 (4000+ 매장)
3. **에러 처리**: 일부 매장 검색 실패 시에도 계속 진행됩니다
4. **파일 크기**: 검색 결과 txt 파일이 많이 생성될 수 있습니다

## 🔗 관련 파일

- `open_sdk/streamlit_app/app.py` - 메인 앱
- `open_sdk/streamlit_app/utils/store_search_processor.py` - MCP 검색 프로세서
- `agents_new/google_map_mcp/google_maps_agent.py` - Google Maps Agent
- `data/matched_store_results.csv` - 매장 데이터
- `open_sdk/output/store_mcp_searches/` - 검색 결과 저장 폴더

## 📧 문의

문제가 발생하거나 개선 사항이 있으면 이슈를 등록해주세요.
