"""
환경 변수 로더
프로젝트 루트의 env 파일을 로드하고 필수 키를 검증합니다.
"""
from pathlib import Path
from dotenv import load_dotenv
import os

def load_env():
    """프로젝트 루트의 env 파일을 로드하고 환경 변수를 설정합니다."""
    try:
        # 프로젝트 루트의 env 파일 로드
        project_root = Path(__file__).parent.parent.parent.parent
        env_path = project_root / "env"
        
        if env_path.exists():
            load_dotenv(env_path, override=True)
            print(f"[ENV] 환경 변수 로드 완료: {env_path}")
        else:
            print(f"[WARN] env 파일을 찾을 수 없습니다: {env_path}")
            # 현재 디렉토리에서 시도
            load_dotenv(override=True)
        
        # 필수 키 검증
        required_keys = ["GEMINI_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
        missing_keys = []
        
        for key in required_keys:
            if not os.getenv(key):
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
        
        print("[ENV] 모든 필수 환경 변수가 설정되었습니다.")
        return True
        
    except Exception as e:
        print(f"[ERROR] 환경 변수 로드 실패: {e}")
        return False

def get_env_var(key: str, default: str = None) -> str:
    """환경 변수 값을 가져옵니다."""
    return os.getenv(key, default)

# 모듈 로드 시 자동으로 환경 변수 로드
if __name__ != "__main__":
    load_env()
