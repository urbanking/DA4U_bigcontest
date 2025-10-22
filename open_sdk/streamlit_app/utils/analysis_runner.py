"""
분석 실행 래퍼
run_analysis.py를 subprocess로 실행하고 실시간 로그를 캡처합니다.
"""
import subprocess
import sys
from pathlib import Path
try:
    from langfuse.decorators import observe, langfuse_context
except ImportError:
    # Langfuse가 없을 때 폴백
    def observe(name=None):
        def decorator(func):
            return func
        return decorator
    
    class MockLangfuseContext:
        def update_current_trace(self, **kwargs):
            pass
    
    langfuse_context = MockLangfuseContext()
from typing import Callable, Optional

@observe(name="run_analysis")
def run_analysis_with_logging(store_code: str, log_callback: Callable[[str], None]) -> Optional[str]:
    """
    run_analysis.py를 실행하고 실시간 로그를 캡처합니다.
    
    Args:
        store_code: 분석할 상점 코드
        log_callback: 로그를 처리할 콜백 함수
        
    Returns:
        출력 파일 경로 또는 None (실패 시)
    """
    langfuse_context.update_current_trace(
        user_id=store_code,
        tags=["analysis_execution"]
    )
    
    try:
        # run_analysis.py 스크립트 경로
        script_path = Path(__file__).parent.parent.parent / "run_analysis.py"
        
        if not script_path.exists():
            log_callback(f"[ERROR] 분석 스크립트를 찾을 수 없습니다: {script_path}")
            return None
        
        log_callback(f"[INFO] 분석 시작: {store_code}")
        log_callback(f"[INFO] 스크립트 경로: {script_path}")
        
        # subprocess로 분석 실행
        process = subprocess.Popen(
            [sys.executable, str(script_path), store_code],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        output_file = None
        
        # 실시간 로그 캡처
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if line:
                log_callback(line)
                
                # 출력 파일 경로 추출
                if "[OUTPUT] 출력 파일:" in line:
                    output_file = line.split(":")[-1].strip()
                elif "[OUTPUT] 통합 결과 저장:" in line:
                    output_file = line.split(":")[-1].strip()
        
        # 프로세스 완료 대기
        return_code = process.wait()
        
        if return_code == 0:
            log_callback(f"[OK] 분석 완료: {store_code}")
            if output_file:
                log_callback(f"[OK] 결과 파일: {output_file}")
            return output_file
        else:
            log_callback(f"[ERROR] 분석 실패 (코드: {return_code})")
            return None
            
    except Exception as e:
        log_callback(f"[ERROR] 분석 실행 중 오류: {e}")
        return None

def check_analysis_status(store_code: str) -> dict:
    """
    분석 상태를 확인합니다.
    
    Args:
        store_code: 상점 코드
        
    Returns:
        분석 상태 정보
    """
    try:
        # outputs 디렉토리에서 최신 분석 결과 확인
        outputs_dir = Path(__file__).parent.parent.parent / "output"
        
        if not outputs_dir.exists():
            return {"status": "not_started", "message": "분석 결과 디렉토리가 없습니다."}
        
        # 상점 코드로 시작하는 디렉토리 찾기
        analysis_dirs = [d for d in outputs_dir.iterdir() 
                        if d.is_dir() and d.name.startswith(f"analysis_{store_code}")]
        
        if not analysis_dirs:
            return {"status": "not_started", "message": "분석 결과를 찾을 수 없습니다."}
        
        # 가장 최근 디렉토리 선택
        latest_dir = max(analysis_dirs, key=lambda x: x.stat().st_mtime)
        
        # 분석 결과 파일 확인
        result_file = latest_dir / "analysis_result.json"
        comprehensive_file = latest_dir / "comprehensive_analysis.json"
        
        if result_file.exists() and comprehensive_file.exists():
            return {
                "status": "completed",
                "message": "분석이 완료되었습니다.",
                "result_dir": str(latest_dir),
                "result_file": str(result_file),
                "comprehensive_file": str(comprehensive_file)
            }
        else:
            return {
                "status": "in_progress",
                "message": "분석이 진행 중입니다.",
                "result_dir": str(latest_dir)
            }
            
    except Exception as e:
        return {"status": "error", "message": f"상태 확인 중 오류: {e}"}
