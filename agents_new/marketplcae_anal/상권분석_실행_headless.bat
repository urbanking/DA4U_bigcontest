@echo off
chcp 65001 > nul
cd /d "%~dp0"
set HEADLESS=1
set PLAYWRIGHT_MCP_HEADLESS=true
call C:\Users\ansck\anaconda3\Scripts\activate.bat

echo.
echo ============================================================
echo (HEADLESS) 서울시 골목상권 분석 자동화 시스템
echo ============================================================
echo.

python 상권분석_자동화.py --headless --no-pause %*

REM no pause in headless mode