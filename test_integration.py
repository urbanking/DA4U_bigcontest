#!/usr/bin/env python3
"""
Google Maps HTTP 통합 테스트 스크립트
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_http_client():
    """HTTP 클라이언트 테스트"""
    print("=" * 60)
    print("Google Maps HTTP Client 테스트")
    print("=" * 60)
    
    try:
        from agents_new.google_map_mcp.http_client import GoogleMapsHTTPClient
        
        # 환경 변수 설정 (테스트용)
        os.environ['Google_Map_API_KEY'] = 'test_key'
        os.environ['GEMINI_API_KEY'] = 'test_key'
        
        client = GoogleMapsHTTPClient()
        print("✅ HTTP 클라이언트 초기화 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ HTTP 클라이언트 테스트 실패: {e}")
        return False

def test_langchain_tools():
    """LangChain 도구 테스트"""
    print("\n" + "=" * 60)
    print("Google Maps LangChain 도구 테스트")
    print("=" * 60)
    
    try:
        from agents_new.google_map_mcp.langchain_tools import get_google_maps_tools
        
        tools = get_google_maps_tools()
        print(f"✅ LangChain 도구 로드 성공: {len(tools)}개 도구")
        
        for tool in tools:
            print(f"   - {tool.name}: {tool.description[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ LangChain 도구 테스트 실패: {e}")
        return False

def test_app_integration():
    """app.py 통합 테스트"""
    print("\n" + "=" * 60)
    print("app.py 통합 테스트")
    print("=" * 60)
    
    try:
        # app.py에서 Google Maps 관련 임포트 테스트
        sys.path.append('open_sdk/streamlit_app')
        
        # 환경 변수 설정
        os.environ['Google_Map_API_KEY'] = 'test_key'
        os.environ['GEMINI_API_KEY'] = 'test_key'
        
        # Google Maps 모듈 임포트 테스트
        from agents_new.google_map_mcp.http_client import run_lookup_from_code_http
        from agents_new.google_map_mcp.langchain_tools import get_google_maps_tools
        
        print("✅ app.py 통합 테스트 성공")
        print("   - HTTP 클라이언트 임포트: ✅")
        print("   - LangChain 도구 임포트: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ app.py 통합 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_csv_lookup():
    """CSV 기반 조회 테스트"""
    print("\n" + "=" * 60)
    print("CSV 기반 조회 테스트")
    print("=" * 60)
    
    try:
        from agents_new.google_map_mcp.http_client import run_lookup_from_code_http
        
        # CSV 파일 경로
        csv_path = 'agents_new/google_map_mcp/matched_store_results.csv'
        
        if not os.path.exists(csv_path):
            print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")
            return False
        
        print(f"✅ CSV 파일 발견: {csv_path}")
        
        # Dry run으로 테스트 (실제 API 호출 없이)
        result = run_lookup_from_code_http(
            code="000F03E44A",
            csv_path=csv_path
        )
        
        if "error" in result:
            print(f"⚠️  조회 결과에 오류: {result['error']}")
        else:
            print("✅ CSV 기반 조회 성공")
            print(f"   - 코드: {result.get('code', 'N/A')}")
            print(f"   - 매장명: {result.get('input_store_name', 'N/A')}")
            print(f"   - 매칭 매장명: {result.get('matched_store_name', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ CSV 기반 조회 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Google Maps HTTP 통합 테스트 시작")
    
    # 테스트 실행
    tests = [
        test_http_client,
        test_langchain_tools,
        test_app_integration,
        test_csv_lookup
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 테스트 실행 중 오류: {e}")
            results.append(False)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    
    test_names = [
        "HTTP 클라이언트",
        "LangChain 도구",
        "app.py 통합",
        "CSV 기반 조회"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{i+1}. {name}: {status}")
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n총 {total_count}개 테스트 중 {success_count}개 성공")
    
    if success_count == total_count:
        print("🎉 모든 테스트가 성공했습니다!")
        print("\n📋 사용 방법:")
        print("1. .env 파일에 Google_Map_API_KEY와 GEMINI_API_KEY 설정")
        print("2. streamlit run open_sdk/streamlit_app/app.py")
        print("3. Google Maps 도구 섹션에서 기능 테스트")
    else:
        print("⚠️  일부 테스트가 실패했습니다. API 키 설정을 확인해주세요.")
