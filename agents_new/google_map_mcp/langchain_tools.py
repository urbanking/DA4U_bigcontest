"""
Google Maps MCP LangChain 도구
LangChain과 통합하여 사용할 수 있는 Google Maps 도구들
"""

from langchain_core.tools import tool
from typing import Optional, Dict, Any
try:
    from .http_client import GoogleMapsHTTPClient, search_place_tool, get_place_details_tool
except ImportError:
    from http_client import GoogleMapsHTTPClient, search_place_tool, get_place_details_tool


@tool
def search_places(query: str, location: str = None, radius: int = 5000) -> str:
    """
    Google Places API를 사용하여 장소를 검색합니다.
    
    Args:
        query: 검색할 장소명 또는 키워드 (예: "강남역 스타벅스", "서울 맛집")
        location: 검색 중심 위치 (위도,경도 형식, 예: "37.5665,126.9780")
        radius: 검색 반경 (미터 단위, 기본값: 5000)
        
    Returns:
        검색 결과를 포맷팅된 문자열로 반환
    """
    try:
        client = GoogleMapsHTTPClient()
        results = client.search_places(query, location, radius)
        
        if "error" in results:
            return f"검색 실패: {results['error']}"
        
        places = results.get("results", [])
        if not places:
            return "검색 결과가 없습니다."
        
        # 상위 5개 결과 반환
        formatted_results = ["📍 **검색 결과:**\n"]
        for i, place in enumerate(places[:5]):
            formatted_results.append(f"""
**{i+1}. {place.get('name', 'N/A')}**
- 📍 주소: {place.get('formatted_address', 'N/A')}
- ⭐ 평점: {place.get('rating', 'N/A')}/5.0 ({place.get('user_ratings_total', 0)} 리뷰)
- 🏷️ 카테고리: {', '.join(place.get('types', []))}
- 🆔 Place ID: {place.get('place_id', 'N/A')}
""")
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"장소 검색 실패: {str(e)}"


@tool
def get_place_details(place_id: str) -> str:
    """
    Google Places API를 사용하여 특정 장소의 상세 정보를 조회합니다.
    
    Args:
        place_id: Google Places API Place ID
        
    Returns:
        장소의 상세 정보를 포맷팅된 문자열로 반환
    """
    try:
        client = GoogleMapsHTTPClient()
        details = client.get_place_details(place_id)
        
        if "error" in details:
            return f"상세 정보 조회 실패: {details['error']}"
        
        # 상세 정보 포맷팅
        formatted_details = f"""
🏪 **{details.get('name', 'N/A')}**

📍 **기본 정보**
- 주소: {details.get('formatted_address', 'N/A')}
- 전화번호: {details.get('formatted_phone_number', 'N/A')}
- 웹사이트: {details.get('website', 'N/A')}

⭐ **평가 정보**
- 평점: {details.get('rating', 'N/A')}/5.0
- 리뷰 수: {details.get('user_ratings_total', 0)}개

🕐 **영업시간**
"""
        
        opening_hours = details.get('opening_hours', {})
        if opening_hours.get('weekday_text'):
            for day_info in opening_hours['weekday_text']:
                formatted_details += f"- {day_info}\n"
        else:
            formatted_details += "- 영업시간 정보 없음\n"
        
        formatted_details += "\n💬 **리뷰**\n"
        
        reviews = details.get('reviews', [])
        if reviews:
            for i, review in enumerate(reviews[:5]):  # 최대 5개 리뷰
                formatted_details += f"""
**{i+1}. {review.get('author_name', 'N/A')}** ⭐ {review.get('rating', 'N/A')}/5.0
{review.get('text', 'N/A')}
"""
        else:
            formatted_details += "- 리뷰가 없습니다.\n"
        
        return formatted_details
        
    except Exception as e:
        return f"상세 정보 조회 실패: {str(e)}"


@tool
def search_and_get_details(query: str, location: str = None, radius: int = 5000) -> str:
    """
    장소를 검색하고 첫 번째 결과의 상세 정보를 조회합니다.
    
    Args:
        query: 검색할 장소명 또는 키워드
        location: 검색 중심 위치 (위도,경도 형식)
        radius: 검색 반경 (미터 단위, 기본값: 5000)
        
    Returns:
        검색 결과와 상세 정보를 포함한 포맷팅된 문자열
    """
    try:
        client = GoogleMapsHTTPClient()
        
        # 1. 장소 검색
        search_results = client.search_places(query, location, radius)
        
        if "error" in search_results:
            return f"검색 실패: {search_results['error']}"
        
        places = search_results.get("results", [])
        if not places:
            return "검색 결과가 없습니다."
        
        # 2. 첫 번째 결과의 상세 정보 조회
        first_place = places[0]
        place_id = first_place.get('place_id')
        
        if place_id:
            details = client.get_place_details(place_id)
            
            if "error" not in details:
                # 검색 결과와 상세 정보 결합
                result = f"""
🔍 **검색 결과: {query}**

🏪 **{details.get('name', first_place.get('name', 'N/A'))}**

📍 **기본 정보**
- 주소: {details.get('formatted_address', first_place.get('formatted_address', 'N/A'))}
- 전화번호: {details.get('formatted_phone_number', 'N/A')}
- 웹사이트: {details.get('website', 'N/A')}

⭐ **평가 정보**
- 평점: {details.get('rating', first_place.get('rating', 'N/A'))}/5.0
- 리뷰 수: {details.get('user_ratings_total', first_place.get('user_ratings_total', 0))}개

🕐 **영업시간**
"""
                
                opening_hours = details.get('opening_hours', {})
                if opening_hours.get('weekday_text'):
                    for day_info in opening_hours['weekday_text']:
                        result += f"- {day_info}\n"
                else:
                    result += "- 영업시간 정보 없음\n"
                
                result += "\n💬 **리뷰**\n"
                
                reviews = details.get('reviews', [])
                if reviews:
                    for i, review in enumerate(reviews[:3]):  # 최대 3개 리뷰
                        result += f"""
**{i+1}. {review.get('author_name', 'N/A')}** ⭐ {review.get('rating', 'N/A')}/5.0
{review.get('text', 'N/A')}
"""
                else:
                    result += "- 리뷰가 없습니다.\n"
                
                return result
        
        # Place ID가 없거나 상세 정보 조회 실패 시 기본 검색 결과 반환
        return search_places.invoke({"query": query, "location": location, "radius": radius})
        
    except Exception as e:
        return f"검색 및 상세 정보 조회 실패: {str(e)}"


@tool
def geocode_address(address: str) -> str:
    """
    주소를 좌표로 변환합니다.
    
    Args:
        address: 변환할 주소 (예: "서울특별시 강남구 테헤란로 123")
        
    Returns:
        좌표 정보를 포맷팅된 문자열로 반환
    """
    try:
        client = GoogleMapsHTTPClient()
        result = client.geocode_address(address)
        
        if "error" in result:
            return f"주소 변환 실패: {result['error']}"
        
        results = result.get("results", [])
        if not results:
            return "주소 변환 결과가 없습니다."
        
        # 첫 번째 결과 반환
        first_result = results[0]
        geometry = first_result.get("geometry", {})
        location = geometry.get("location", {})
        
        formatted_result = f"""
📍 **주소 변환 결과**

**입력 주소:** {address}
**변환된 주소:** {first_result.get('formatted_address', 'N/A')}
**위도:** {location.get('lat', 'N/A')}
**경도:** {location.get('lng', 'N/A')}
"""
        
        return formatted_result
        
    except Exception as e:
        return f"주소 변환 실패: {str(e)}"


# LangChain 도구 목록
GOOGLE_MAPS_TOOLS = [
    search_places,
    get_place_details,
    search_and_get_details,
    geocode_address
]


def get_google_maps_tools():
    """
    Google Maps LangChain 도구들을 반환합니다.
    
    Returns:
        Google Maps 도구들의 리스트
    """
    return GOOGLE_MAPS_TOOLS


if __name__ == "__main__":
    # 테스트 코드
    print("Google Maps LangChain 도구 테스트")
    
    try:
        # 도구 테스트
        print("\n1. 장소 검색 테스트")
        result = search_places.invoke({"query": "강남역 스타벅스"})
        print(result[:500] + "..." if len(result) > 500 else result)
        
        print("\n2. 주소 변환 테스트")
        result = geocode_address.invoke({"address": "서울특별시 강남구 테헤란로 123"})
        print(result)
        
    except Exception as e:
        print(f"테스트 실패: {e}")
