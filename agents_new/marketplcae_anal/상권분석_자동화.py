"""
서울시 골목상권 분석 자동화 스크립트
주소를 입력하면 자동으로 bat 파일을 수정하고 상권분석을 실행합니다.
"""

import os
import sys
import subprocess
from pathlib import Path

def 주소_정리(주소):
    """주소를 파일명으로 사용 가능한 형태로 변환"""
    # 공백 제거 및 특수문자 처리
    파일명 = 주소.replace(" ", "").replace(",", "").replace("-", "")
    return 파일명

def md파일_업데이트(주소, 업종="외식업", 반경="500M", headless: bool = False):
    """
    GEMINI.md 파일의 예시 주소를 업데이트합니다.
    
    Args:
        주소: 서울시 주소
        업종: 분석 업종
        반경: 분석 반경
    """
    # 프로젝트 폴더 기준 경로로 변경
    current_dir = Path(__file__).parent
    md_파일경로 = current_dir / ".gemini" / "GEMINI.md"
    
    if not md_파일경로.exists():
        print(f"[WARN] MD file not found: {md_파일경로}")
        print(f"[INFO] Skipping MD file update (optional)")
        return True  # Not critical
    
    파일명 = 주소_정리(주소)
    
    # GEMINI.md 파일 템플릿
    md_내용 = f"""# 서울시 골목상권 분석 자동화

## 프로젝트 설명

서울시 골목상권 분석 사이트(https://golmok.seoul.go.kr)에서 Playwright MCP를 사용하여 자동으로 상권분석 리포트를 생성하고 캡처하는 도구입니다.

## 실행 방법

### gemini1.bat 실행

배치 파일을 더블클릭하여 자동화된 상권분석을 수행합니다.

```batch
gemini1.bat  # 일반 실행 (브라우저 표시)
상권분석_실행_headless.bat  # 헤드리스 실행 (브라우저 미표시)
```

## 작동 과정

1. **브라우저 시작**: 새로운 브라우저 세션으로 Playwright MCP 실행
2. **사이트 접속**: https://golmok.seoul.go.kr/owner/owner.do
3. **주소 입력**: {주소}
4. **다음 버튼 클릭**
5. **업종 선택**: {업종} 선택
6. **다음 버튼 클릭**
7. **분석영역 설정**:
   - 반경/다각형 클릭
   - {반경} 선택
   - 적용 버튼 클릭
8. **분석 실행**: 분석하기 버튼 클릭
9. **결과 캡처**: 화면 오른편의 분석레포트 캡처 및 PNG로 저장
10. **PDF 출력**: 문의번호 옆옆에 있는 프린트 모양의 출력 버튼 클릭
11. **PDF 저장**: 출력 페이지에서 왼쪽 위 2번째에 있는 PDF 저장 버튼 클릭
12. **대기**: 40초 기다림 (PDF 생성 완료 대기)

헤드리스 모드: {"사용" if headless else "미사용"}

## 출력 파일

분석이 완료되면 다음과 같은 형식으로 파일들이 저장됩니다:

### PNG 스크린샷

- **파일명 예시**: `{파일명}_상권분석레포트.png`
- **저장 위치**: 프로젝트 폴더 (`.playwright-mcp` 폴더)

### PDF 리포트

- **파일명**: 브라우저 다운로드 폴더에 자동 저장
- **저장 위치**: 프로젝트 폴더(.상권분석리포트 폴더)
- **대기 시간**: PDF 생성 완료까지 40초 소요

## 사용 예시

### Python 스크립트로 실행
```bash
python 상권분석_자동화.py "{주소}" {업종} {반경}
```

### 다른 주소로 분석하기

gemini1.bat 파일을 편집하여 주소를 변경할 수 있습니다:

```batch
gemini --yolo -p "새로운 브라우저 세션으로 시작하고 play wrights mcp를 사용해서 @https://golmok.seoul.go.kr/owner/owner.do 들어가 [원하는주소]로 상권분석을 해줘..."
```

### 설정 변경 가능 항목

- **주소**: {주소} → 다른 서울시 주소
- **업종**: {업종} → 외식업, 서비스업, 소매업
- **반경**: {반경} → 300M, 500M, 1000M

## 주요 파일

- `상권분석_자동화.py`: 주소 입력받아 자동으로 bat 파일 및 md 파일 업데이트
- `gemini1.bat`: 상권분석 자동화 실행 배치 파일
- `gemini_간단명확.bat`: 간단한 명령 실행용 배치 파일
- `gemini_JSON추출.bat`: JSON 데이터 추출용 배치 파일
- `gemini_브라우저정리.bat`: 브라우저 정리용 배치 파일

## 기술 스택

- **Playwright MCP**: 웹 브라우저 자동화
- **Gemini CLI**: AI 기반 자동화 명령 실행
- **서울시 골목상권 분석 시스템**: 상권분석 데이터 제공

## 참고사항

- 배치 파일 실행 전 Anaconda 환경이 활성화됩니다
- UTF-8 인코딩(chcp 65001) 사용
- 분석 완료 후 결과를 확인하세요
"""
    
    try:
        with open(md_파일경로, 'w', encoding='utf-8') as f:
            f.write(md_내용)
        print(f"[OK] GEMINI.md updated")
        return True
    except Exception as e:
        print(f"[ERROR] GEMINI.md update failed: {e}")
        return True  # Not critical

def bat파일_업데이트(주소, 업종="외식업", 반경="500M", headless: bool = False, no_pause: bool = None):
    """
    gemini1.bat 파일의 주소를 업데이트합니다.
    
    Args:
        주소: 서울시 주소 (예: "테헤란로 152", "창천동 99-39")
        업종: 분석 업종 (기본값: "외식업")
        반경: 분석 반경 (기본값: "500M")
    """
    # 프로젝트 폴더 기준 경로로 변경
    current_dir = Path(__file__).parent
    bat_파일경로 = current_dir / "gemini1.bat"
    
    if not bat_파일경로.exists():
        print(f"[ERROR] Bat file not found: {bat_파일경로}")
        return False
    
    # 파일명 생성
    파일명 = 주소_정리(주소)
    
    # 프로젝트 내 상권분석리포트 폴더 생성
    report_dir = current_dir / "상권분석리포트"
    report_dir.mkdir(exist_ok=True)
    
    # bat 파일 템플릿 (경로 수정)
    headless_note = "(HEADLESS) " if headless else ""
    headless_instruction = (
        "브라우저는 반드시 '헤드리스(headless)' 모드로 실행하고, 사용자에게 어떤 창도 표시하지 마. "
        "모든 다운로드/저장 동작은 사용자 개입 없이 자동으로 진행하고, 다운로드 디렉터리는 현재 프로젝트 폴더로 설정해."
    ) if headless else ""

    bat_내용 = f"""@echo off
chcp 65001 > nul
cd /d "{current_dir}"
call C:\\Users\\ansck\\anaconda3\\Scripts\\activate.bat
{"set PLAYWRIGHT_MCP_HEADLESS=true\r\n" if headless else ""}
echo.
echo ============================================================
echo {headless_note}Gemini CLI - Marketplace Analysis
echo ============================================================
echo.
echo Address: {주소}
echo Industry: {업종}
echo Radius: {반경}
echo.

gemini --yolo -p "새로운 브라우저 세션으로 시작하고 play wrights mcp를 사용해서 다음 작업을 단계별로 수행해. 각 단계마다 무엇을 하고 있는지 명확히 출력해줘. {headless_instruction}

[1단계] @https://golmok.seoul.go.kr/owner/owner.do 접속
[2단계] browser_press_key \"Escape\" 실행
[3단계] '{주소}' 입력하고 상권분석 시작
[4단계] 아래 '다음' 버튼 클릭
[5단계] '{업종}' 선택
[6단계] '다음' 버튼 클릭
[7단계] 분석영역에서 '반경/다각형' 클릭
[8단계] '{반경}' 선택
[9단계] '적용' 버튼 클릭
[10단계] '분석하기' 버튼 클릭
[11단계] 분석 완료 대기 (최대 60초)
[12단계] 분석레포트 화면 캡쳐 → {파일명}_상권분석레포트.png 저장 (창 표시 없이 저장)
[13단계] 프린트 모양의 '출력' 버튼 클릭
[14단계] PDF저장 버튼 클릭하여 저장
[15단계] 40초 대기

각 단계를 실행하면서 '현재 [N단계] 수행 중: ...' 형식으로 출력해줘 "

echo.
echo ============================================================
echo Complete!
echo ============================================================
echo.
echo PNG Location: {current_dir}\\.playwright-mcp
echo PDF Location: {current_dir}\\상권분석리포트
echo.
"""

    # headless 모드에서는 pause 제거 (no_pause가 명시되면 우선 반영)
    if no_pause is None:
        no_pause = headless

    if not no_pause:
        bat_내용 = bat_내용 + "\r\npause"
    
    try:
        with open(bat_파일경로, 'w', encoding='utf-8') as f:
            f.write(bat_내용)
        print(f"[OK] bat file updated: {주소}")
        return True
    except Exception as e:
        print(f"[ERROR] bat update failed: {e}")
        return False

def bat파일_실행():
    """
    gemini1.bat 파일을 실행하고 실시간 로그 출력
    """
    current_dir = Path(__file__).parent
    bat_파일경로 = current_dir / "gemini1.bat"
    
    if not bat_파일경로.exists():
        print(f"[ERROR] Bat file not found: {bat_파일경로}")
        return False
    
    print("[START] Executing gemini1.bat...\n")
    print("=" * 60)
    print("Playwright Page Automation Log (Real-time)")
    print("=" * 60)
    
    try:
        # bat 파일 실행 (실시간 출력)
        process = subprocess.Popen(
            str(bat_파일경로),
            shell=True,
            cwd=str(current_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        # 실시간 출력 (이모지 제거 - Windows 콘솔 호환)
        for line in process.stdout:
            line = line.strip()
            if line:
                # 주요 단계 강조
                if "골목상권" in line or "선택" in line or "클릭" in line or "저장" in line:
                    print(f"  >> {line}")
                elif "error" in line.lower() or "failed" in line.lower():
                    print(f"  [ERROR] {line}")
                elif "success" in line.lower() or "완료" in line or "OK" in line:
                    print(f"  [OK] {line}")
                elif "단계" in line:
                    print(f"  [STEP] {line}")
                else:
                    print(f"  {line}")
        
        process.wait()
        
        print("\n" + "=" * 60)
        if process.returncode == 0:
            print("[OK] bat file execution completed!")
            return True
        else:
            print(f"[WARN] bat file returned code: {process.returncode}")
            return True  # 일부 실패해도 파일이 생성되었을 수 있음
            
    except Exception as e:
        print(f"[ERROR] Execution failed: {e}")
        return False

def 상권분석_실행(주소, 업종="외식업", 반경="500M"):
    """
    상권분석을 실행합니다.
    
    Args:
        주소: 서울시 주소
        업종: 분석 업종 (외식업, 서비스업, 소매업)
        반경: 분석 반경 (300M, 500M, 1000M)
    """
    print("\n" + "="*60)
    print("Seoul Marketplace Analysis Automation")
    print("="*60)
    print(f"Address: {주소}")
    print(f"Industry: {업종}")
    print(f"Radius: {반경}")
    print("="*60 + "\n")
    
    # 1. bat 파일 업데이트
    print("[Step 1] Updating gemini1.bat...")
    # headless 여부는 환경변수 또는 기본 False
    headless_env = os.environ.get("HEADLESS", "0")
    headless = headless_env == "1"

    if not bat파일_업데이트(주소, 업종, 반경, headless=headless):
        return
    
    # 2. md 파일 업데이트
    print("[Step 2] Updating GEMINI.md...")
    md파일_업데이트(주소, 업종, 반경, headless=headless)  # Optional
    
    print("\n" + "="*60)
    
    # 3. bat 파일 실행
    print("[Step 3] Executing gemini1.bat...\n")
    bat파일_실행()

def main():
    """메인 함수"""
    print("\n" + "="*60)
    print("Seoul Marketplace Analysis Automation System")
    print("="*60 + "\n")
    
    # 명령줄 인자가 있으면 사용
    # 간단한 인자 파서 (주소/업종/반경 + 옵션)
    args = sys.argv[1:]
    headless = False
    no_pause = None
    # 옵션 추출
    filtered = []
    for a in args:
        if a in ("--headless", "-H"):
            headless = True
        elif a == "--no-pause":
            no_pause = True
        else:
            filtered.append(a)

    if len(filtered) > 0:
        주소 = filtered[0]
        업종 = filtered[1] if len(filtered) > 1 else "외식업"
        반경 = filtered[2] if len(filtered) > 2 else "500M"
    else:
        # 대화형 입력
        print("Address (ex: 테헤란로 152, 창천동 99-39)")
        주소 = input("Address: ").strip()
        
        if not 주소:
            print("[ERROR] Please enter address")
            return
        
        print("\nIndustry (default: 외식업)")
        print("   1. 외식업")
        print("   2. 서비스업")
        print("   3. 소매업")
        업종_선택 = input("Select (1-3, Enter=외식업): ").strip()
        
        업종_맵 = {"1": "외식업", "2": "서비스업", "3": "소매업", "": "외식업"}
        업종 = 업종_맵.get(업종_선택, "외식업")
        
        print("\nRadius (default: 500M)")
        print("   1. 300M")
        print("   2. 500M")
        print("   3. 1000M")
        반경_선택 = input("Select (1-3, Enter=500M): ").strip()
        
        반경_맵 = {"1": "300M", "2": "500M", "3": "1000M", "": "500M"}
        반경 = 반경_맵.get(반경_선택, "500M")
    
    # HEADLESS 환경변수로 하위 로직에 전달
    if headless:
        os.environ["HEADLESS"] = "1"
    # 상권분석 실행
    상권분석_실행(주소, 업종, 반경)

if __name__ == "__main__":
    main()

