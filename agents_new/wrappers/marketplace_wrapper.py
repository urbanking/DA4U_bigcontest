"""
Marketplace Analysis Wrapper
주의: 기존 폴더 구조 보존, bat 파일 조심히 다룸
"""
import os
import sys
import asyncio
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class MarketplaceWrapper:
    """
    Wrapper for marketplace analysis automation
    
    주의사항:
    - 기존 폴더 구조 절대 변경 금지
    - bat 파일 실행은 subprocess로 신중히 처리
    - Gemini CLI 터미널 실행 대기
    - 결과 파일 polling으로 완료 감지
    """
    
    def __init__(self):
        """Initialize marketplace wrapper"""
        self.root = os.getenv("MARKETPLACE_ANALYSIS_ROOT", "c:\\상권분석")
        self.bat_path = os.getenv("MARKETPLACE_BAT_PATH", "c:\\상권분석\\gemini1.bat")
        self.output_path = os.getenv("MARKETPLACE_OUTPUT_PATH", "c:\\상권분석\\상권분석리포트")
        
        # Verify paths exist
        if not Path(self.root).exists():
            print(f"[Marketplace] Warning: Root directory not found: {self.root}")
    
    def _update_bat_file(self, address: str, industry: str = "외식업", radius: str = "500M") -> bool:
        """Update bat file directly (without using marketplcae_anal module)"""
        try:
            파일명 = address.replace(" ", "").replace(",", "").replace("-", "")
            
            # 저장 경로 명시 (test_output 폴더로 직접 저장)
            save_dir = Path(__file__).parent.parent / "test_output"
            save_dir.mkdir(parents=True, exist_ok=True)
            저장경로 = str(save_dir).replace("\\", "\\\\")
            
            bat_content = f"""@echo off
chcp 65001 > nul
cd /d "C:\\상권분석"
call C:\\Users\\ansck\\anaconda3\\Scripts\\activate.bat
echo.
echo ============================================================
echo Marketplace Analysis
echo ============================================================
echo.
echo Address: {address}
echo Industry: {industry}
echo Radius: {radius}
echo Save Path: {저장경로}
echo.

gemini --yolo -p "새로운 브라우저 세션으로 시작하고 play wrights mcp를 사용해서 @https://golmok.seoul.go.kr/owner/owner.do 들어가 {address} 로 상권분석을 해줘 그리고 아래 다음 버튼을 클릭 {industry}을 선택해 그리고 다음을 눌러 
그리고 분석영역에서 반경/다각형을 클릭 {radius}를 선택 아래 적용 버튼을 누르고 분석하기 버튼, 그리고 화면 오른편에 분석레포트가 뜨는데 
그 화면을 캡쳐해서 {저장경로} 폴더에 저장해 파일명은 {파일명}_상권분석레포트.png 로 저장해, png를 저장하고 그리고 그다음에 문의번호 옆옆에 프린트 모양의 출력 버튼을 클릭하고 출력 페이지에서 왼쪽 위 2번째 pdf저장 버튼을 눌러서 {저장경로} 폴더에 저장하고 40초 기다려"

echo.
echo ============================================================
echo Complete!
echo ============================================================
pause"""
            
            with open(self.bat_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)
            
            print(f"[Marketplace] Bat file updated - Save path: {저장경로}")
            return True
            
        except Exception as e:
            print(f"[Marketplace] Bat update failed: {e}")
            return False
    
    async def analyze(
        self,
        address: str,
        industry: str = "외식업",
        radius: str = "500M",
        timeout_seconds: int = 480  # 8분 (Chrome 자동화는 5-7분 소요)
    ) -> Dict[str, Any]:
        """
        Run marketplace analysis by executing Python script directly
        
        Args:
            address: Address to analyze
            industry: Industry type (외식업, 서비스업, 소매업)
            radius: Analysis radius (300M, 500M, 1000M)
            timeout_seconds: Maximum wait time
            
        Returns:
            Analysis result dict
        """
        print(f"[Marketplace] Starting analysis for {address}")
        
        try:
            # Execute Python script directly (간단!)
            script_path = Path(__file__).parent.parent / "marketplcae_anal" / "상권분석_자동화.py"
            
            print(f"[Marketplace] Executing: {script_path.name}")
            print(f"[Marketplace] This will take 3-5 minutes (Gemini CLI + browser automation)")
            
            # Build args with headless by default (can override via HEADLESS=0)
            import subprocess as sp
            headless_env = os.getenv("HEADLESS", "0")  # 기본값: 헤드리스 해제
            headless = headless_env == "1"

            args = [
                "python",
                str(script_path),
            ]
            if headless:
                args += ["--headless", "--no-pause"]
            args += [address, industry, radius]

            # Run Python script with real-time output
            # Child env: only set headless-related vars if explicitly enabled
            child_env = {**os.environ}
            if headless:
                child_env.update({
                    "HEADLESS": "1",
                    "PLAYWRIGHT_MCP_HEADLESS": "true",
                })

            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=child_env,
                creationflags=sp.CREATE_NO_WINDOW if hasattr(sp, 'CREATE_NO_WINDOW') else 0
            )
            
            # 실시간 로그 캡처 (이모지 제거)
            async def read_stream(stream, prefix):
                """실시간으로 stdout/stderr 읽기"""
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    decoded_line = line.decode('utf-8', errors='ignore').strip()
                    if decoded_line:
                        # 단계 로그 강조
                        if "단계" in decoded_line:
                            print(f"[Marketplace] >> {decoded_line}")
                        else:
                            print(f"[Marketplace] {prefix} {decoded_line}")
            
            try:
                # stdout, stderr 동시에 읽기
                await asyncio.wait_for(
                    asyncio.gather(
                        read_stream(process.stdout, "[OUT]"),
                        read_stream(process.stderr, "[ERR]"),
                        process.wait()
                    ),
                    timeout=timeout_seconds
                )
                
                if process.returncode == 0:
                    print(f"[Marketplace] [OK] Script completed successfully")
                else:
                    print(f"[Marketplace] [ERROR] Script failed with return code {process.returncode}")
                    
            except asyncio.TimeoutError:
                process.kill()
                print(f"[Marketplace] [TIMEOUT] Timeout after {timeout_seconds}s")
            except Exception as e:
                print(f"[Marketplace] [ERROR] Subprocess error: {e}")
            
            # Parse results and copy to test_output
            print("[Marketplace] Collecting results...")
            analysis_result = await self._parse_results(address)
            
            return {
                "success": True,
                "address": address,
                "industry": industry,
                "radius": radius,
                "result": analysis_result,
                "data_source": "골목상권분석 시스템"
            }
            
        except Exception as e:
            print(f"[Marketplace] Error: {e}")
            return {
                "success": False,
                "error": str(e),
                "address": address
            }
    
    async def _execute_bat_async(self, timeout_seconds: int) -> Dict[str, Any]:
        """
        Execute bat file asynchronously with timeout
        
        Args:
            timeout_seconds: Maximum execution time
            
        Returns:
            Execution result
        """
        try:
            # Run subprocess
            process = await asyncio.create_subprocess_exec(
                self.bat_path,
                cwd=self.root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout_seconds
                )
                
                if process.returncode == 0:
                    return {"success": True}
                else:
                    return {
                        "success": False,
                        "error": f"Process failed with code {process.returncode}",
                        "stderr": stderr.decode('utf-8', errors='ignore')
                    }
                    
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": f"Execution timeout ({timeout_seconds}s)"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}"
            }
    
    async def _parse_results(self, address: str) -> Dict[str, Any]:
        """
        Parse analysis results from .playwright-mcp folder and auto-copy to test_output
        
        Args:
            address: Original address
            
        Returns:
            Parsed results
        """
        import shutil
        from datetime import datetime
        
        # Gemini CLI 실제 저장 위치: .playwright-mcp
        playwright_dir = Path(__file__).parent.parent / "marketplcae_anal" / ".playwright-mcp"
        test_output_dir = Path(__file__).parent.parent / "test_output"
        test_output_dir.mkdir(exist_ok=True)
        
        if not playwright_dir.exists():
            print(f"[Marketplace] Warning: .playwright-mcp folder not found")
            return {
                "status": "files_not_found",
                "message": "Gemini output directory not found"
            }
        
        # Find PNG and PDF files in .playwright-mcp
        png_files = list(playwright_dir.glob("*상권분석레포트.png"))
        pdf_files = list(playwright_dir.glob("*.pdf"))
        
        print(f"[Marketplace] Found {len(png_files)} PNG, {len(pdf_files)} PDF files in .playwright-mcp")
        
        # Auto-copy to test_output
        copied_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for png in png_files:
            dest = test_output_dir / f"marketplace_report_{timestamp}.png"
            shutil.copy2(png, dest)
            copied_files.append(str(dest))
            print(f"[Marketplace] Copied PNG: {dest.name}")
        
        for pdf in pdf_files:
            dest = test_output_dir / f"marketplace_report_{timestamp}.pdf"
            shutil.copy2(pdf, dest)
            copied_files.append(str(dest))
            print(f"[Marketplace] Copied PDF: {dest.name}")
        
        return {
            "status": "completed",
            "output_files": copied_files,
            "save_location": str(test_output_dir),
            "message": f"Analysis completed! {len(copied_files)} files auto-copied to test_output",
            "png_count": len(png_files),
            "pdf_count": len(pdf_files)
        }
    
    def _get_recent_files(self, directory: Path, minutes: int = 10) -> list[str]:
        """
        Get files modified in the last N minutes
        
        Args:
            directory: Directory to search
            minutes: Time window in minutes
            
        Returns:
            List of file paths
        """
        recent = []
        cutoff_time = time.time() - (minutes * 60)
        
        for file in directory.rglob("*"):
            if file.is_file() and file.stat().st_mtime > cutoff_time:
                recent.append(str(file))
        
        return recent


async def run_marketplace_analysis(
    address: str,
    industry: str = "외식업",
    radius: str = "500M"
) -> Dict[str, Any]:
    """
    Async wrapper to run marketplace analysis
    
    Args:
        address: Address to analyze
        industry: Industry type
        radius: Analysis radius
        
    Returns:
        Analysis result
    """
    wrapper = MarketplaceWrapper()
    result = await wrapper.analyze(address, industry, radius)
    return result


if __name__ == "__main__":
    """
    Direct execution from command line
    Usage:
        python marketplace_wrapper.py "서울특별시 성동구 왕십리로 222" "외식업" "500M"
        python marketplace_wrapper.py "서울특별시 강남구 테헤란로 427"
    """
    import sys
    
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python marketplace_wrapper.py <address> [industry] [radius]")
        print("Example: python marketplace_wrapper.py '서울특별시 성동구 왕십리로 222' '외식업' '500M'")
        sys.exit(1)
    
    address = sys.argv[1]
    industry = sys.argv[2] if len(sys.argv) > 2 else "외식업"
    radius = sys.argv[3] if len(sys.argv) > 3 else "500M"
    
    print(f"\n{'='*60}")
    print(f"Marketplace Analysis Wrapper - Direct Execution")
    print(f"{'='*60}")
    print(f"Address: {address}")
    print(f"Industry: {industry}")
    print(f"Radius: {radius}")
    print(f"{'='*60}\n")
    
    # Run analysis
    result = asyncio.run(run_marketplace_analysis(address, industry, radius))
    
    # Print result
    import json
    print("\n" + "="*60)
    print("Analysis Result:")
    print("="*60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("="*60)

