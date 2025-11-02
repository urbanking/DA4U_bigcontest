"""
환경 변수 로더
Streamlit Secrets → 환경 변수로 변환 → 기존 코드 그대로 작동
배포: Streamlit Cloud Secrets만 사용
로컬: .streamlit/secrets.toml 파일 직접 읽기
"""
from pathlib import Path
import os

def _load_toml_file(toml_path: Path) -> dict:
    """TOML 파일을 직접 파싱하여 딕셔너리로 반환"""
    try:
        import tomllib  # Python 3.11+
        with open(toml_path, 'rb') as f:
            return tomllib.load(f)
    except ImportError:
        # Python 3.10 이하: tomli 사용
        try:
            import tomli
            with open(toml_path, 'rb') as f:
                return tomli.load(f)
        except ImportError:
            # tomli도 없으면 수동 파싱
            result = {}
            with open(toml_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        result[key] = value
            return result

def load_env():
    """Streamlit Secrets 또는 secrets.toml 파일을 환경 변수로 변환합니다."""
    try:
        # 1순위: Streamlit Secrets를 환경 변수로 변환 (배포 환경)
        try:
            import streamlit as st
            secrets = st.secrets
            if hasattr(secrets, 'to_dict'):
                secrets_dict = secrets.to_dict()
                for key, value in secrets_dict.items():
                    # Secrets를 환경 변수로 설정 (기존 코드는 그대로 os.getenv() 사용)
                    os.environ[key] = str(value)
                print("[ENV] Streamlit Secrets를 환경 변수로 변환 완료")
                
                # 필수 키 검증
                required_keys = ["GEMINI_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
                missing_keys = [k for k in required_keys if not os.getenv(k)]
                
                if not missing_keys:
                    print("[ENV] 모든 필수 환경 변수가 설정되었습니다.")
                    return True
        except (FileNotFoundError, AttributeError, RuntimeError):
            # Streamlit 컨텍스트가 아닌 경우 (독립 실행 에이전트)
            pass
        
        # 2순위: .streamlit/secrets.toml 파일 직접 읽기 (로컬 개발 + 독립 실행)
        # 여러 위치에서 secrets.toml 파일 찾기
        possible_paths = [
            Path(__file__).parent.parent / ".streamlit" / "secrets.toml",  # open_sdk/streamlit_app/.streamlit/secrets.toml
            Path(__file__).parent.parent.parent.parent / ".streamlit" / "secrets.toml",  # 프로젝트 루트/.streamlit/secrets.toml
            Path.cwd() / ".streamlit" / "secrets.toml",  # 현재 작업 디렉토리
        ]
        
        secrets_toml_path = None
        for path in possible_paths:
            if path.exists():
                secrets_toml_path = path
                break
        
        if secrets_toml_path and secrets_toml_path.exists():
            try:
                secrets_dict = _load_toml_file(secrets_toml_path)
                for key, value in secrets_dict.items():
                    # 이미 설정된 환경 변수는 덮어쓰지 않음
                    if key not in os.environ:
                        os.environ[key] = str(value)
                print(f"[ENV] secrets.toml 파일을 환경 변수로 변환 완료: {secrets_toml_path}")
                
                # 필수 키 검증
                required_keys = ["GEMINI_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
                missing_keys = [k for k in required_keys if not os.getenv(k)]
                
                if not missing_keys:
                    print("[ENV] 모든 필수 환경 변수가 설정되었습니다.")
                    return True
            except Exception as e:
                print(f"[WARN] secrets.toml 파일 읽기 실패: {e}")
        else:
            print("[WARN] .streamlit/secrets.toml 파일을 찾을 수 없습니다.")
        
        # 필수 키 검증
        required_keys = ["GEMINI_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
        missing_keys = [k for k in required_keys if not os.getenv(k)]
        
        if missing_keys:
            error_msg = f"""
[ERROR] 필수 환경 변수가 설정되지 않았습니다: {', '.join(missing_keys)}

로컬 개발 시:
1. .streamlit/secrets.toml 파일을 생성하세요
   위치: open_sdk/streamlit_app/.streamlit/secrets.toml

배포 시:
1. Streamlit Cloud 대시보드에서 Secrets를 설정하세요

예시 (.streamlit/secrets.toml):
GEMINI_API_KEY = "your-key"
LANGFUSE_PUBLIC_KEY = "your-key"
LANGFUSE_SECRET_KEY = "your-key"
"""
            raise ValueError(error_msg)
        
        print("[ENV] 모든 필수 환경 변수가 설정되었습니다.")
        return True
        
    except Exception as e:
        print(f"[ERROR] 환경 변수 로드 실패: {e}")
        return False

def get_env_var(key: str, default: str = None) -> str:
    """환경 변수 값을 가져옵니다. Streamlit Secrets 우선, 그 다음 환경 변수."""
    # 먼저 Streamlit Secrets 확인 (배포 환경)
    try:
        import streamlit as st
        secret_value = st.secrets.get(key)
        if secret_value:
            return secret_value
    except (FileNotFoundError, AttributeError, RuntimeError):
        pass
    
    # 그 다음 환경 변수 확인 (secrets.toml에서 로드된 값 또는 시스템 환경 변수)
    return os.getenv(key, default)

# 모듈 로드 시 자동으로 환경 변수 로드
if __name__ != "__main__":
    load_env()