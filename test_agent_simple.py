#!/usr/bin/env python3
"""
Google Maps Agent 간단 테스트
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agents_new', 'google_map_mcp'))

def test_agent_basic():
    """기본 에이전트 테스트"""
    try:
        # 환경 변수 설정 (테스트용)
        os.environ['Google_Map_API_KEY'] = 'test_key'
        os.environ['GEMINI_API_KEY'] = 'test_key'
        
        # 모듈 임포트 테스트
        from agents_new.google_map_mcp.google_maps_agent import GoogleMapsAgent
        print("✅ GoogleMapsAgent 모듈 임포트 성공")
        
        # 에이전트 초기화 테스트 (환경 변수만 확인)
        try:
            agent = GoogleMapsAgent()
            print("✅ GoogleMapsAgent 초기화 성공")
        except ValueError as e:
            if "API_KEY" in str(e):
                print("⚠️  API 키가 설정되지 않음 (예상된 오류)")
                print("   실제 사용 시에는 .env 파일에 API 키를 설정해야 합니다")
            else:
                raise e
        
        return True
    except Exception as e:
        print(f"❌ 에이전트 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_csv_data():
    """CSV 데이터 테스트"""
    try:
        import csv
        csv_path = 'agents_new/google_map_mcp/matched_store_results.csv'
        
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            first_row = next(reader)
            
            print("✅ CSV 데이터 읽기 성공:")
            print(f"   - 코드: {first_row.get('코드', 'N/A')}")
            print(f"   - 입력 매장명: {first_row.get('입력_가맹점명', 'N/A')}")
            print(f"   - 매칭 매장명: {first_row.get('매칭_상호명', 'N/A')}")
            print(f"   - Place ID: {first_row.get('place_id', 'N/A')}")
            print(f"   - 주소: {first_row.get('입력_주소', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"❌ CSV 데이터 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_lookup_runner():
    """Lookup Runner 테스트"""
    try:
        # 상대 임포트 문제 해결을 위해 직접 모듈 로드
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "lookup_runner", 
            "agents_new/google_map_mcp/lookup_runner.py"
        )
        lookup_runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lookup_runner)
        
        # CSV 파일 경로
        csv_path = 'agents_new/google_map_mcp/matched_store_results.csv'
        
        # Dry run으로 테스트
        result = lookup_runner.run_lookup_from_code(
            code="000F03E44A",  # 첫 번째 행의 코드
            csv_path=csv_path,
            dry_run=True  # 실제 API 호출 없이 CSV 조회만
        )
        
        print("✅ Lookup Runner 테스트 성공:")
        print(f"   - 코드: {result.get('code')}")
        print(f"   - 입력 매장명: {result.get('input_store_name')}")
        print(f"   - 매칭 매장명: {result.get('matched_store_name')}")
        print(f"   - 검색 쿼리: {result.get('search_query')}")
        
        return True
    except Exception as e:
        print(f"❌ Lookup Runner 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Google Maps Agent 테스트 시작")
    print("=" * 60)
    
    # 1. 기본 에이전트 테스트
    print("\n1. 기본 에이전트 테스트")
    agent_success = test_agent_basic()
    
    # 2. CSV 데이터 테스트
    print("\n2. CSV 데이터 테스트")
    csv_success = test_csv_data()
    
    # 3. Lookup Runner 테스트
    print("\n3. Lookup Runner 테스트")
    lookup_success = test_lookup_runner()
    
    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)
    
    if agent_success and csv_success and lookup_success:
        print("🎉 모든 테스트가 성공했습니다!")
        print("\n📋 테스트 결과 요약:")
        print("   - Google Maps Agent 모듈 임포트: ✅")
        print("   - CSV 데이터 읽기: ✅")
        print("   - Lookup Runner 기능: ✅")
        print("\n💡 실제 사용을 위해서는:")
        print("   1. .env 파일에 Google_Map_API_KEY와 GEMINI_API_KEY 설정")
        print("   2. run_from_code.py를 사용하여 특정 코드로 검색 실행")
    else:
        print("❌ 일부 테스트가 실패했습니다.")
