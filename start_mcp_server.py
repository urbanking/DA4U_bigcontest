#!/usr/bin/env python3
"""
MCP Google Maps 서버 시작 스크립트

이 스크립트는 mcp-google-map HTTP 서버를 시작합니다.
Streamlit 배포 환경에서 Google Maps 기능을 사용하기 위해 필요합니다.

사용법:
    python start_mcp_server.py

환경 변수:
    GOOGLE_API_KEY: Google Maps API 키
    MCP_SERVER_PORT: MCP 서버 포트 (기본값: 3000)
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def check_google_api_key():
    """Google API 키 확인"""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY 또는 GOOGLE_MAPS_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("다음과 같이 설정하세요:")
        print("export GOOGLE_API_KEY=your_api_key_here")
        return False
    return True


def check_npm_available():
    """npm이 사용 가능한지 확인"""
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_mcp_package():
    """mcp-google-map 패키지 설치"""
    try:
        print("📦 mcp-google-map 패키지 설치 중...")
        subprocess.run([
            "npm", "install", "-g", "@cablate/mcp-google-map"
        ], check=True, capture_output=True)
        print("✅ mcp-google-map 패키지 설치 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 패키지 설치 실패: {e}")
        return False


def start_mcp_server():
    """MCP 서버 시작"""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
    port = os.getenv("MCP_SERVER_PORT", "3000")
    
    print(f"🚀 MCP Google Maps 서버 시작 중... (포트: {port})")
    print(f"📍 서버 URL: http://localhost:{port}/mcp")
    
    try:
        # mcp-google-map 서버 시작
        subprocess.run([
            "mcp-google-map",
            "--port", port,
            "--apikey", api_key
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ MCP 서버 시작 실패: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 MCP 서버가 중지되었습니다.")
        return True


def main():
    """메인 함수"""
    print("🔧 MCP Google Maps 서버 설정")
    print("=" * 50)
    
    # 1. Google API 키 확인
    if not check_google_api_key():
        sys.exit(1)
    
    # 2. npm 사용 가능 여부 확인
    if not check_npm_available():
        print("❌ npm이 설치되지 않았습니다.")
        print("Node.js와 npm을 설치하세요: https://nodejs.org/")
        sys.exit(1)
    
    # 3. mcp-google-map 패키지 설치
    if not install_mcp_package():
        print("❌ 패키지 설치에 실패했습니다.")
        sys.exit(1)
    
    # 4. MCP 서버 시작
    print("\n" + "=" * 50)
    start_mcp_server()


if __name__ == "__main__":
    main()
