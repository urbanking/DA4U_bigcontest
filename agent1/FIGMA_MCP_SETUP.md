# Figma와 Cursor MCP 연동 설정 가이드

이 문서는 Figma와 Cursor를 MCP(Model-Context-Protocol)를 통해 연동하는 방법을 설명합니다.

## 1단계: 필요한 도구 설치

### 1.1 Figma Desktop App
- [Figma Desktop App 다운로드](https://www.figma.com/downloads/)
- 설치 후 Figma 계정으로 로그인

### 1.2 Cursor IDE
- [Cursor IDE 다운로드](https://cursor.sh/)
- 설치 완료

### 1.3 Figma 계정
- [Figma 계정 생성](https://www.figma.com/)
- Dev Mode 접근 권한 확인

### 1.4 Bun 런타임 환경
```powershell
# Windows에서 Bun 설치
powershell -c "irm bun.sh/install.ps1 | iex"

# 설치 확인
bun --version
```

## 2단계: Figma에서 Dev Mode MCP 서버 활성화

1. **Figma Desktop App 실행**
   - 연동할 디자인 파일 열기

2. **메인 메뉴 접근**
   - 화면 왼쪽 상단의 Figma 로고(메인 메뉴) 클릭

3. **Preferences 메뉴로 이동**
   - Preferences (기본 설정) 메뉴 선택

4. **Dev Mode MCP Server 활성화**
   - "Enable Dev Mode MCP Server" 옵션 체크

## 3단계: Cursor에서 MCP 설정

### 3.1 MCP 설정 파일 생성
`mcp_config.json` 파일이 이미 생성되어 있습니다.

### 3.2 Figma Access Token 설정
1. [Figma 개발자 페이지](https://www.figma.com/developers/api#authentication)에서 Personal Access Token 생성
2. 환경변수 설정:
   ```cmd
   set FIGMA_ACCESS_TOKEN=your_token_here
   ```
   또는 `.env` 파일에 추가:
   ```
   FIGMA_ACCESS_TOKEN=your_token_here
   ```

### 3.3 Cursor 설정
1. Cursor에서 Settings 열기 (Ctrl+,)
2. "MCP" 검색
3. MCP 설정 파일 경로 지정: `C:\agent1\mcp_config.json`

## 4단계: 연동 테스트

### 4.1 기본 연결 테스트
```bash
# 간단한 테스트 실행
python test_figma_mcp_simple.py

# 또는 상세한 테스트 실행
python test_figma_mcp.py
```

### 4.2 테스트 스크립트 설명
- `test_figma_mcp_simple.py`: 기본적인 MCP 서버 테스트
- `test_figma_mcp.py`: 상세한 Figma API 호출 테스트

### 4.3 테스트 전 준비사항
1. Figma Access Token 설정
2. 테스트할 Figma 파일 키 준비
3. Python 의존성 설치 확인

## 5단계: 프로젝트 통합

### 5.1 Figma MCP 클라이언트 생성
`backend/mcp/figma_client.py` 파일을 생성하여 Figma MCP 기능을 프로젝트에 통합합니다.

### 5.2 사용 가능한 기능들
- 디자인 파일 정보 가져오기
- 컴포넌트 정보 추출
- 디자인 토큰 추출
- 스크린샷 생성
- 디자인 변경사항 추적

## 문제 해결

### 일반적인 문제들
1. **Bun이 인식되지 않는 경우**
   - 터미널을 재시작하거나 PATH 환경변수 확인

2. **Figma Access Token 오류**
   - 토큰이 올바르게 설정되었는지 확인
   - 토큰 권한이 충분한지 확인

3. **MCP 서버 연결 실패**
   - Figma Desktop App이 실행 중인지 확인
   - Dev Mode MCP Server가 활성화되었는지 확인

## 다음 단계

1. Figma Access Token 설정
2. Cursor에서 MCP 설정 적용
3. 테스트 스크립트 실행
4. 프로젝트에 Figma MCP 클라이언트 통합
