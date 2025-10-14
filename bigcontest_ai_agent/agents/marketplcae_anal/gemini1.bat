@echo off
chcp 65001 > nul
cd /d "C:\ㅈ\DA4U\bigcontest_ai_agent\agents\marketplcae_anal"
call C:\Users\ansck\anaconda3\Scripts\activate.bat
echo.
echo ============================================================
echo Gemini CLI - Marketplace Analysis
echo ============================================================
echo.
echo Address: 뚝섬역
echo Industry: 외식업
echo Radius: 500M
echo.

gemini --yolo -p "새로운 브라우저 세션으로 시작하고  play wrights mcp를 사용해서 @https://golmok.seoul.go.kr/owner/owner.do 들어가  browser_press_key "Escape" 뚝섬역 로 상권분석을 해줘 그리고 아래 다음 버튼을 클릭 외식업을 선택해 그리고 다음을 눌러 
그리고 분석영역에서 반경/다각형을 클릭 500M를 선택 아래 적용 버튼을 누르고 분석하기 버튼, 그리고 화면 오른편에 분석레포트가 뜨는데 
그 화면을 캡쳐해서 저장해 파일명은 뚝섬역_상권분석레포트.png 로 저장해,png를 저장하고 그리고 그다음에 문의번호 옆옆에 프린트 모양의 출력 버튼을 클릭하고 출력 페이지에서 왼쪽 위 2번째 pdf저장 버튼을 눌러서 저장하고 40초 기다려 "

echo.
echo ============================================================
echo Complete!
echo ============================================================
echo.
echo PNG Location: C:\ㅈ\DA4U\bigcontest_ai_agent\agents\marketplcae_anal\.playwright-mcp
echo PDF Location: C:\ㅈ\DA4U\bigcontest_ai_agent\agents\marketplcae_anal\상권분석리포트
echo.
pause