#!/usr/bin/env python3
"""
마케팅 & Google Maps 자동 연동 테스트 스크립트
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_auto_integration():
    """자동 연동 테스트"""
    print("=" * 60)
    print("마케팅 & Google Maps 자동 연동 테스트")
    print("=" * 60)
    
    try:
        from agents_new.google_map_mcp.auto_integration import auto_marketing_google_maps_integration
        
        # 테스트용 마케팅 결과
        test_marketing_result = {
            "marketing_strategies": [
                {
                    "title": "온라인 마케팅 강화",
                    "description": "SNS와 온라인 플랫폼을 통한 홍보",
                    "expected_effect": "고객 유입 증가"
                },
                {
                    "title": "지역 커뮤니티 참여",
                    "description": "지역 이벤트 및 커뮤니티 활동 참여",
                    "expected_effect": "지역 인지도 향상"
                }
            ],
            "target_audience": "20-30대 직장인",
            "recommendations": "디지털 마케팅 전략 수립 및 지역 특성 활용"
        }
        
        # 자동 연동 테스트
        print("🔄 자동 연동 테스트 시작...")
        result = auto_marketing_google_maps_integration(
            store_code="000F03E44A",
            marketing_result=test_marketing_result
        )
        
        print(f"✅ 테스트 완료: {result.get('integration_status')}")
        
        if result.get('output_file'):
            print(f"📄 출력 파일: {result['output_file']}")
            
            # 파일 존재 확인
            if os.path.exists(result['output_file']):
                print("✅ 파일 생성 성공")
                
                # 파일 내용 일부 출력
                with open(result['output_file'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"📊 파일 크기: {len(content)} 문자")
                    print("📋 파일 내용 미리보기:")
                    print("-" * 40)
                    print(content[:500] + "..." if len(content) > 500 else content)
                    print("-" * 40)
            else:
                print("❌ 파일 생성 실패")
        
        return True
        
    except Exception as e:
        print(f"❌ 자동 연동 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_integration():
    """app.py 통합 테스트"""
    print("\n" + "=" * 60)
    print("app.py 통합 테스트")
    print("=" * 60)
    
    try:
        # app.py에서 자동 연동 모듈 임포트 테스트
        from agents_new.google_map_mcp.auto_integration import auto_marketing_google_maps_integration
        
        print("✅ 자동 연동 모듈 임포트 성공")
        
        # 간단한 기능 테스트
        test_result = auto_marketing_google_maps_integration(
            store_code="test_code",
            marketing_result={"test": "data"}
        )
        
        print(f"✅ 기능 테스트 성공: {test_result.get('integration_status')}")
        
        return True
        
    except Exception as e:
        print(f"❌ app.py 통합 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("마케팅 & Google Maps 자동 연동 통합 테스트 시작")
    
    # 테스트 실행
    tests = [
        test_auto_integration,
        test_app_integration
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
        "자동 연동 기능",
        "app.py 통합"
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
        print("3. 상점 코드 입력 후 분석 시작")
        print("4. 마케팅 분석 후 자동으로 Google Maps 연동 실행")
        print("5. 통합 결과가 txt 파일로 자동 저장됨")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 설정을 확인해주세요.")
