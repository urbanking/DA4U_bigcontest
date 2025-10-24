"""
마케팅과 Google Maps MCP 자동 연동 모듈
마케팅 분석 후 자동으로 Google Maps 정보를 조회하여 txt 파일로 저장
"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
try:
    from .http_client import run_lookup_from_code_http
except ImportError:
    from http_client import run_lookup_from_code_http


def auto_marketing_google_maps_integration(
    store_code: str,
    marketing_result: Dict[str, Any],
    csv_path: str = None,
    output_dir: str = None
) -> Dict[str, Any]:
    """
    마케팅 분석 결과를 받아서 Google Maps 정보를 자동으로 조회하고 txt 파일로 저장
    
    Args:
        store_code: 상점 코드
        marketing_result: 마케팅 분석 결과 딕셔너리
        csv_path: CSV 파일 경로 (기본값: matched_store_results.csv)
        output_dir: 출력 디렉토리
        
    Returns:
        통합 결과 딕셔너리
    """
    try:
        # 기본 경로 설정
        if not csv_path:
            csv_path = os.path.join(os.path.dirname(__file__), "matched_store_results.csv")
        
        if not output_dir:
            output_dir = os.path.join(os.path.dirname(__file__), "outputs")
        
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        # Google Maps 정보 조회
        print(f"🔍 Google Maps 정보 조회 중: {store_code}")
        google_maps_result = run_lookup_from_code_http(
            code=store_code,
            csv_path=csv_path,
            out_dir=output_dir,
            force=True
        )
        
        # 통합 결과 생성
        integrated_result = {
            "store_code": store_code,
            "timestamp": datetime.now().isoformat(),
            "marketing_analysis": marketing_result,
            "google_maps_info": google_maps_result,
            "integration_status": "success"
        }
        
        # txt 파일로 저장
        output_filename = f"marketing_google_maps_integration_{store_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"마케팅 & Google Maps 통합 분석 결과\n")
            f.write(f"상점 코드: {store_code}\n")
            f.write(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # 마케팅 분석 결과
            f.write("📊 마케팅 분석 결과\n")
            f.write("-" * 40 + "\n")
            if "marketing_strategies" in marketing_result:
                f.write(f"마케팅 전략 수: {len(marketing_result['marketing_strategies'])}\n")
                for i, strategy in enumerate(marketing_result['marketing_strategies'], 1):
                    f.write(f"{i}. {strategy.get('title', 'N/A')}\n")
                    f.write(f"   - 설명: {strategy.get('description', 'N/A')}\n")
                    f.write(f"   - 예상 효과: {strategy.get('expected_effect', 'N/A')}\n\n")
            
            if "target_audience" in marketing_result:
                f.write(f"타겟 고객: {marketing_result['target_audience']}\n")
            
            if "recommendations" in marketing_result:
                f.write(f"추천사항: {marketing_result['recommendations']}\n")
            
            f.write("\n" + "=" * 80 + "\n\n")
            
            # Google Maps 정보
            f.write("🗺️ Google Maps 정보\n")
            f.write("-" * 40 + "\n")
            
            if "error" not in google_maps_result:
                f.write(f"매장명: {google_maps_result.get('input_store_name', 'N/A')}\n")
                f.write(f"매칭 매장명: {google_maps_result.get('matched_store_name', 'N/A')}\n")
                f.write(f"주소: {google_maps_result.get('input_address', 'N/A')}\n")
                f.write(f"Place ID: {google_maps_result.get('place_id', 'N/A')}\n")
                
                # Place Details 정보
                place_details = google_maps_result.get('place_details', {})
                if place_details and "error" not in place_details:
                    f.write(f"\n📍 상세 정보:\n")
                    f.write(f"정식 매장명: {place_details.get('name', 'N/A')}\n")
                    f.write(f"주소: {place_details.get('formatted_address', 'N/A')}\n")
                    f.write(f"전화번호: {place_details.get('formatted_phone_number', 'N/A')}\n")
                    f.write(f"웹사이트: {place_details.get('website', 'N/A')}\n")
                    f.write(f"평점: {place_details.get('rating', 'N/A')}/5.0\n")
                    f.write(f"리뷰 수: {place_details.get('user_ratings_total', 0)}개\n")
                    
                    # 영업시간
                    opening_hours = place_details.get('opening_hours', {})
                    if opening_hours.get('weekday_text'):
                        f.write(f"\n🕐 영업시간:\n")
                        for day_info in opening_hours['weekday_text']:
                            f.write(f"  {day_info}\n")
                    
                    # 리뷰
                    reviews = place_details.get('reviews', [])
                    if reviews:
                        f.write(f"\n💬 리뷰 (최대 5개):\n")
                        for i, review in enumerate(reviews[:5], 1):
                            f.write(f"{i}. {review.get('author_name', 'N/A')} ⭐ {review.get('rating', 'N/A')}/5.0\n")
                            f.write(f"   {review.get('text', 'N/A')}\n\n")
            else:
                f.write(f"Google Maps 정보 조회 실패: {google_maps_result.get('error', 'N/A')}\n")
            
            f.write("\n" + "=" * 80 + "\n\n")
            
            # 통합 분석 및 추천
            f.write("🎯 통합 분석 및 추천\n")
            f.write("-" * 40 + "\n")
            
            # 마케팅 전략과 Google Maps 정보를 바탕으로 한 통합 추천
            recommendations = generate_integrated_recommendations(marketing_result, google_maps_result)
            for i, rec in enumerate(recommendations, 1):
                f.write(f"{i}. {rec}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("분석 완료\n")
            f.write("=" * 80 + "\n")
        
        print(f"✅ 통합 분석 결과 저장 완료: {output_path}")
        
        # 통합 결과에 파일 경로 추가
        integrated_result["output_file"] = output_path
        
        return integrated_result
        
    except Exception as e:
        print(f"❌ 자동 연동 실패: {e}")
        return {
            "store_code": store_code,
            "timestamp": datetime.now().isoformat(),
            "marketing_analysis": marketing_result,
            "google_maps_info": {"error": str(e)},
            "integration_status": "failed",
            "error": str(e)
        }


def generate_integrated_recommendations(
    marketing_result: Dict[str, Any],
    google_maps_result: Dict[str, Any]
) -> list:
    """
    마케팅 분석 결과와 Google Maps 정보를 바탕으로 통합 추천사항 생성
    
    Args:
        marketing_result: 마케팅 분석 결과
        google_maps_result: Google Maps 정보
        
    Returns:
        추천사항 리스트
    """
    recommendations = []
    
    # Google Maps 정보 기반 추천
    if "error" not in google_maps_result:
        place_details = google_maps_result.get('place_details', {})
        
        if place_details and "error" not in place_details:
            rating = place_details.get('rating', 0)
            review_count = place_details.get('user_ratings_total', 0)
            
            # 평점 기반 추천
            if rating < 3.0:
                recommendations.append("Google Maps 평점이 낮으므로 고객 만족도 개선이 필요합니다.")
            elif rating >= 4.5:
                recommendations.append("높은 Google Maps 평점을 활용한 마케팅 전략을 수립하세요.")
            
            # 리뷰 수 기반 추천
            if review_count < 10:
                recommendations.append("리뷰 수가 적으므로 고객 리뷰 유도 전략을 마케팅에 포함하세요.")
            elif review_count > 100:
                recommendations.append("많은 리뷰를 활용한 소셜 프루프 마케팅을 강화하세요.")
    
    # 마케팅 전략 기반 추천
    if "marketing_strategies" in marketing_result:
        strategy_count = len(marketing_result['marketing_strategies'])
        if strategy_count > 0:
            recommendations.append(f"제안된 {strategy_count}개의 마케팅 전략을 Google Maps 정보와 연계하여 실행하세요.")
    
    # 타겟 고객 기반 추천
    if "target_audience" in marketing_result:
        target = marketing_result['target_audience']
        recommendations.append(f"타겟 고객 '{target}'에게 맞는 Google Maps 최적화를 고려하세요.")
    
    # 기본 추천사항
    if not recommendations:
        recommendations.append("마케팅 전략과 Google Maps 정보를 종합적으로 분석하여 실행 계획을 수립하세요.")
    
    return recommendations


def batch_auto_integration(
    store_codes: list,
    marketing_results: Dict[str, Dict[str, Any]],
    csv_path: str = None,
    output_dir: str = None
) -> Dict[str, Any]:
    """
    여러 상점 코드에 대해 일괄 자동 연동 처리
    
    Args:
        store_codes: 상점 코드 리스트
        marketing_results: 상점 코드별 마케팅 결과 딕셔너리
        csv_path: CSV 파일 경로
        output_dir: 출력 디렉토리
        
    Returns:
        일괄 처리 결과
    """
    results = {}
    
    for store_code in store_codes:
        print(f"🔄 처리 중: {store_code}")
        
        marketing_result = marketing_results.get(store_code, {})
        if not marketing_result:
            print(f"⚠️  {store_code}의 마케팅 결과가 없습니다.")
            continue
        
        result = auto_marketing_google_maps_integration(
            store_code=store_code,
            marketing_result=marketing_result,
            csv_path=csv_path,
            output_dir=output_dir
        )
        
        results[store_code] = result
    
    return results


if __name__ == "__main__":
    # 테스트 코드
    print("마케팅 & Google Maps 자동 연동 테스트")
    
    # 테스트용 마케팅 결과
    test_marketing_result = {
        "marketing_strategies": [
            {
                "title": "온라인 마케팅 강화",
                "description": "SNS와 온라인 플랫폼을 통한 홍보",
                "expected_effect": "고객 유입 증가"
            }
        ],
        "target_audience": "20-30대 직장인",
        "recommendations": "디지털 마케팅 전략 수립"
    }
    
    # 자동 연동 테스트
    result = auto_marketing_google_maps_integration(
        store_code="000F03E44A",
        marketing_result=test_marketing_result
    )
    
    print(f"테스트 결과: {result.get('integration_status')}")
    if result.get('output_file'):
        print(f"출력 파일: {result['output_file']}")
