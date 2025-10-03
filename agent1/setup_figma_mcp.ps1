# Figma MCP 연동 설정 스크립트
# PowerShell에서 실행: .\setup_figma_mcp.ps1

Write-Host "=== Figma MCP 연동 설정을 시작합니다 ===" -ForegroundColor Green

# 1. Bun 설치 확인
Write-Host "`n1. Bun 설치 확인 중..." -ForegroundColor Yellow
try {
    $bunVersion = & bun --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Bun이 이미 설치되어 있습니다: $bunVersion" -ForegroundColor Green
    } else {
        throw "Bun이 설치되지 않음"
    }
} catch {
    Write-Host "❌ Bun이 설치되지 않았습니다. 설치를 시작합니다..." -ForegroundColor Red
    try {
        Invoke-Expression "irm bun.sh/install.ps1 | iex"
        Write-Host "✅ Bun 설치가 완료되었습니다." -ForegroundColor Green
    } catch {
        Write-Host "❌ Bun 설치에 실패했습니다. 수동으로 설치해주세요." -ForegroundColor Red
        Write-Host "설치 명령어: powershell -c `"irm bun.sh/install.ps1 | iex`"" -ForegroundColor Yellow
        exit 1
    }
}

# 2. Node.js 설치 확인
Write-Host "`n2. Node.js 설치 확인 중..." -ForegroundColor Yellow
try {
    $nodeVersion = & node --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Node.js가 이미 설치되어 있습니다: $nodeVersion" -ForegroundColor Green
    } else {
        throw "Node.js가 설치되지 않음"
    }
} catch {
    Write-Host "❌ Node.js가 설치되지 않았습니다." -ForegroundColor Red
    Write-Host "Node.js를 설치해주세요: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# 3. Figma MCP 서버 설치
Write-Host "`n3. Figma MCP 서버 설치 중..." -ForegroundColor Yellow
try {
    $figmaServerVersion = & npm list -g @figma/mcp-server 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Figma MCP 서버가 이미 설치되어 있습니다." -ForegroundColor Green
    } else {
        Write-Host "Figma MCP 서버를 설치합니다..." -ForegroundColor Yellow
        & npm install -g @figma/mcp-server
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Figma MCP 서버 설치가 완료되었습니다." -ForegroundColor Green
        } else {
            throw "Figma MCP 서버 설치 실패"
        }
    }
} catch {
    Write-Host "❌ Figma MCP 서버 설치에 실패했습니다." -ForegroundColor Red
    Write-Host "수동 설치 명령어: npm install -g @figma/mcp-server" -ForegroundColor Yellow
    exit 1
}

# 4. Python 의존성 설치
Write-Host "`n4. Python 의존성 설치 중..." -ForegroundColor Yellow
try {
    & pip install -r requirements_figma_mcp.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python 의존성 설치가 완료되었습니다." -ForegroundColor Green
    } else {
        Write-Host "❌ Python 의존성 설치에 실패했습니다." -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Python 의존성 설치 중 오류가 발생했습니다." -ForegroundColor Red
}

# 5. 환경변수 설정 안내
Write-Host "`n5. 환경변수 설정 안내" -ForegroundColor Yellow
Write-Host "다음 단계를 따라 Figma Access Token을 설정해주세요:" -ForegroundColor Cyan
Write-Host "1. https://www.figma.com/developers/api#authentication 에서 Personal Access Token 생성" -ForegroundColor White
Write-Host "2. 환경변수 설정:" -ForegroundColor White
Write-Host "   set FIGMA_ACCESS_TOKEN=your_token_here" -ForegroundColor Gray
Write-Host "3. 또는 .env 파일에 추가:" -ForegroundColor White
Write-Host "   FIGMA_ACCESS_TOKEN=your_token_here" -ForegroundColor Gray

# 6. Cursor 설정 안내
Write-Host "`n6. Cursor 설정 안내" -ForegroundColor Yellow
Write-Host "Cursor에서 다음 설정을 적용해주세요:" -ForegroundColor Cyan
Write-Host "1. Cursor 설정 열기 (Ctrl+,)" -ForegroundColor White
Write-Host "2. 'MCP' 검색" -ForegroundColor White
Write-Host "3. MCP 설정 파일 경로 지정: $PWD\mcp_config.json" -ForegroundColor White

# 7. 테스트 실행 안내
Write-Host "`n7. 테스트 실행" -ForegroundColor Yellow
Write-Host "설정이 완료되면 다음 명령어로 테스트할 수 있습니다:" -ForegroundColor Cyan
Write-Host "python test_figma_mcp.py" -ForegroundColor Gray

Write-Host "`n=== Figma MCP 연동 설정이 완료되었습니다 ===" -ForegroundColor Green
Write-Host "다음 단계:" -ForegroundColor Cyan
Write-Host "1. Figma Desktop App에서 Dev Mode MCP Server 활성화" -ForegroundColor White
Write-Host "2. Figma Access Token 설정" -ForegroundColor White
Write-Host "3. Cursor에서 MCP 설정 적용" -ForegroundColor White
Write-Host "4. 테스트 실행" -ForegroundColor White

