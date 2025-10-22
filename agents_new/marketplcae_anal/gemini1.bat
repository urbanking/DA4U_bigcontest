@echo off
chcp 65001 > nul
cd /d "c:\ㅈ\DA4U\bigcontest_ai_agent\agents_new\marketplcae_anal"
call C:\Users\ansck\anaconda3\Scripts\activate.bat

echo.
echo ============================================================
echo Gemini CLI - Marketplace Analysis
echo ============================================================
echo.
echo Address: 서울특별시 성동구 왕십리로4가길 9
echo Industry: 외식업
echo Radius: 500M
echo.

gemini --yolo -p "새로운 브라우저 세션으로 시작하고 play wrights mcp를 사용해서 다음 작업을 단계별로 수행해. 각 단계마다 무엇을 하고 있는지 명확히 출력해줘. 

[1단계] @https://golmok.seoul.go.kr/owner/owner.do 접속
[2단계] browser_press_key "Escape" 실행
[3단계] '서울특별시 성동구 왕십리로4가길 9' 입력하고 상권분석 시작
[4단계] 아래 '다음' 버튼 클릭
[5단계] '외식업' 선택
[6단계] '다음' 버튼 클릭
[7단계] 분석영역에서 '반경/다각형' 클릭
[8단계] '500M' 선택
[9단계] '적용' 버튼 클릭
[10단계] '분석하기' 버튼 클릭
[11단계] 분석 완료 대기 (최대 60초)
[12단계] 분석레포트 화면 캡쳐 → 서울특별시성동구왕십리로4가길9_상권분석레포트.png 저장 (창 표시 없이 저장)
[13단계] 프린트 모양의 '출력' 버튼 클릭
[14단계] PDF저장 버튼 클릭하여 저장
[15단계] 40초 대기

각 단계를 실행하면서 '현재 [N단계] 수행 중: ...' 형식으로 출력해줘 "

echo.
echo ============================================================
echo Complete!
echo ============================================================
echo.
echo PNG Location: c:\ㅈ\DA4U\bigcontest_ai_agent\agents_new\marketplcae_anal\.playwright-mcp
echo PDF Location: c:\ㅈ\DA4U\bigcontest_ai_agent\agents_new\marketplcae_anal\상권분석리포트
echo.

pause