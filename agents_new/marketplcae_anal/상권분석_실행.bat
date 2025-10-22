@echo off
chcp 65001 > nul
cd /d "C:\상권분석"
call C:\Users\ansck\anaconda3\Scripts\activate.bat

echo.
echo ============================================================
echo 🏪 서울시 골목상권 분석 자동화 시스템
echo ============================================================
echo.

python 상권분석_자동화.py

pause

