"""
Google Maps MCP HTTP Client
LangChain 기반으로 Google Maps API를 HTTP 방식으로 호출하는 클라이언트
"""

import os
import json
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv


class GoogleMapsHTTPClient:
    """
    Google Maps API HTTP 클라이언트
    LangChain과 통합하여 사용
    """
    
    def __init__(self):
        """HTTP 클라이언트 초기화"""
        load_dotenv()
        
        self.google_maps_api_key = os.getenv("Google_Map_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.google_maps_api_key:
            raise ValueError("Google_Map_API_KEY가 환경변수에 설정되지 않았습니다.")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY가 환경변수에 설정되지 않았습니다.")
        
        # Google Maps API 엔드포인트
        self.places_api_url = "https://maps.googleapis.com/maps/api/place"
        self.geocoding_api_url = "https://maps.googleapis.com/maps/api/geocode"
        
        print("✅ Google Maps HTTP Client 초기화 완료")
    
    def search_places(self, query: str, location: str = None, radius: int = 5000) -> Dict[str, Any]:
        """
        Google Places API를 사용하여 장소 검색
        
        Args:
            query: 검색할 장소명 또는 키워드
            location: 검색 중심 위치 (위도,경도)
            radius: 검색 반경 (미터)
            
        Returns:
            검색 결과 딕셔너리
        """
        try:
            url = f"{self.places_api_url}/textsearch/json"
            params = {
                "query": query,
                "key": self.google_maps_api_key
            }
            
            if location:
                params["location"] = location
                params["radius"] = radius
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "OK":
                raise Exception(f"Places API 오류: {data.get('status')}")
            
            return data
            
        except Exception as e:
            print(f"❌ 장소 검색 실패: {e}")
            return {"error": str(e)}
    
    def get_place_details(self, place_id: str, fields: str = None) -> Dict[str, Any]:
        """
        Google Places API를 사용하여 장소 상세 정보 조회
        
        Args:
            place_id: Google Places API Place ID
            fields: 조회할 필드들 (쉼표로 구분)
            
        Returns:
            장소 상세 정보 딕셔너리
        """
        try:
            if not fields:
                fields = "name,formatted_address,geometry,rating,user_ratings_total,reviews,opening_hours,formatted_phone_number,website,photos,types"
            
            url = f"{self.places_api_url}/details/json"
            params = {
                "place_id": place_id,
                "fields": fields,
                "key": self.google_maps_api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "OK":
                raise Exception(f"Place Details API 오류: {data.get('status')}")
            
            return data.get("result", {})
            
        except Exception as e:
            print(f"❌ 장소 상세 정보 조회 실패: {e}")
            return {"error": str(e)}
    
    def geocode_address(self, address: str) -> Dict[str, Any]:
        """
        주소를 좌표로 변환 (Geocoding)
        
        Args:
            address: 변환할 주소
            
        Returns:
            좌표 정보 딕셔너리
        """
        try:
            url = f"{self.geocoding_api_url}/json"
            params = {
                "address": address,
                "key": self.google_maps_api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "OK":
                raise Exception(f"Geocoding API 오류: {data.get('status')}")
            
            return data
            
        except Exception as e:
            print(f"❌ 주소 변환 실패: {e}")
            return {"error": str(e)}


def run_lookup_from_code_http(
    code: str,
    csv_path: str,
    out_dir: str = None,
    force: bool = False
) -> Dict[str, Any]:
    """
    CSV 코드를 기반으로 Google Maps HTTP API를 사용하여 장소 정보 조회
    
    Args:
        code: CSV의 코드 값
        csv_path: CSV 파일 경로
        out_dir: 출력 디렉토리
        force: 덮어쓰기 여부
        
    Returns:
        검색 결과 딕셔너리
    """
    try:
        # CSV 파일에서 해당 코드의 정보 찾기
        import csv
        
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if str(row.get("코드", "")).strip() == str(code).strip():
                    # HTTP 클라이언트 초기화
                    client = GoogleMapsHTTPClient()
                    
                    # Place ID가 있으면 상세 정보 조회
                    place_id = row.get("place_id", "").strip()
                    if place_id:
                        place_details = client.get_place_details(place_id)
                        
                        # 결과 정리
                        result = {
                            "code": row.get("코드", "").strip(),
                            "input_address": row.get("입력_주소", "").strip(),
                            "input_store_name": row.get("입력_가맹점명", "").strip(),
                            "matched_store_name": row.get("매칭_상호명", "").strip(),
                            "place_id": place_id,
                            "search_query": f"{row.get('매칭_상호명', '')} {row.get('입력_주소', '')}".strip(),
                            "place_details": place_details,
                            "csv_row": row
                        }
                        
                        # 출력 파일 저장
                        if out_dir:
                            os.makedirs(out_dir, exist_ok=True)
                            output_path = os.path.join(out_dir, f"gm_http_result_{code}.json")
                            
                            if force or not os.path.exists(output_path):
                                with open(output_path, "w", encoding="utf-8") as f:
                                    json.dump(result, f, ensure_ascii=False, indent=2)
                                result["output_path"] = output_path
                        
                        return result
                    else:
                        # Place ID가 없으면 텍스트 검색 시도
                        search_query = f"{row.get('매칭_상호명', '')} {row.get('입력_주소', '')}".strip()
                        search_results = client.search_places(search_query)
                        
                        result = {
                            "code": row.get("코드", "").strip(),
                            "input_address": row.get("입력_주소", "").strip(),
                            "input_store_name": row.get("입력_가맹점명", "").strip(),
                            "matched_store_name": row.get("매칭_상호명", "").strip(),
                            "search_query": search_query,
                            "search_results": search_results,
                            "csv_row": row
                        }
                        
                        return result
        
        return {"error": f"코드 '{code}'를 CSV에서 찾을 수 없습니다."}
        
    except Exception as e:
        return {"error": f"HTTP 조회 실패: {str(e)}"}


# LangChain 도구로 사용할 수 있는 래퍼 함수들
def search_place_tool(query: str) -> str:
    """LangChain 도구로 사용할 수 있는 장소 검색 함수"""
    try:
        client = GoogleMapsHTTPClient()
        results = client.search_places(query)
        
        if "error" in results:
            return f"검색 실패: {results['error']}"
        
        places = results.get("results", [])
        if not places:
            return "검색 결과가 없습니다."
        
        # 상위 3개 결과 반환
        formatted_results = []
        for i, place in enumerate(places[:3]):
            formatted_results.append(f"""
{i+1}. {place.get('name', 'N/A')}
   주소: {place.get('formatted_address', 'N/A')}
   평점: {place.get('rating', 'N/A')}/5.0 ({place.get('user_ratings_total', 0)} 리뷰)
   Place ID: {place.get('place_id', 'N/A')}
""")
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"장소 검색 실패: {str(e)}"


def get_place_details_tool(place_id: str) -> str:
    """LangChain 도구로 사용할 수 있는 장소 상세 정보 조회 함수"""
    try:
        client = GoogleMapsHTTPClient()
        details = client.get_place_details(place_id)
        
        if "error" in details:
            return f"상세 정보 조회 실패: {details['error']}"
        
        # 상세 정보 포맷팅
        formatted_details = f"""
장소명: {details.get('name', 'N/A')}
주소: {details.get('formatted_address', 'N/A')}
평점: {details.get('rating', 'N/A')}/5.0 ({details.get('user_ratings_total', 0)} 리뷰)
전화번호: {details.get('formatted_phone_number', 'N/A')}
웹사이트: {details.get('website', 'N/A')}
영업시간: {details.get('opening_hours', {}).get('weekday_text', ['N/A'])}

리뷰:
"""
        
        reviews = details.get('reviews', [])
        for review in reviews[:5]:  # 최대 5개 리뷰
            formatted_details += f"""
- {review.get('author_name', 'N/A')} ({review.get('rating', 'N/A')}/5.0)
  {review.get('text', 'N/A')}
"""
        
        return formatted_details
        
    except Exception as e:
        return f"상세 정보 조회 실패: {str(e)}"


if __name__ == "__main__":
    # 테스트 코드
    print("Google Maps HTTP Client 테스트")
    
    try:
        client = GoogleMapsHTTPClient()
        
        # 장소 검색 테스트
        print("\n1. 장소 검색 테스트")
        results = client.search_places("강남역 스타벅스")
        print(f"검색 결과: {len(results.get('results', []))}개")
        
        # 상세 정보 조회 테스트
        if results.get('results'):
            place_id = results['results'][0]['place_id']
            print(f"\n2. 상세 정보 조회 테스트 (Place ID: {place_id})")
            details = client.get_place_details(place_id)
            print(f"상세 정보: {details.get('name', 'N/A')}")
        
    except Exception as e:
        print(f"테스트 실패: {e}")
