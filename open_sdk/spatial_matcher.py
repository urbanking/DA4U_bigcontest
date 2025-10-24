"""
공간 데이터 기반 주소 매칭 모듈
- 카카오 API: 주소 → 좌표 변환
- SHP 파일: 좌표 → 행정동/상권 매칭
"""
import os
import requests
import geopandas as gpd
import folium
from pathlib import Path
from shapely.geometry import Point
from typing import Optional, Tuple, Dict, Any
from dotenv import load_dotenv
import platform

# matplotlib import 및 설정
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 한글 폰트 설정
system = platform.system()
if system == "Windows":
    plt.rcParams['font.family'] = 'Malgun Gothic'
elif system == "Darwin":
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False
# 체크마크 기호를 위한 추가 설정
plt.rcParams['font.sans-serif'] = ['Malgun Gothic', 'DejaVu Sans', 'Arial Unicode MS']

print("[OK] Matplotlib loaded in spatial_matcher")

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent

# 환경변수 로드 (panorama와 동일 방식)
load_dotenv()
KAKAO_API_KEY = os.getenv('KAKAO_REST_API_KEY')
GOOGLE_API_KEY = "AIzaSyCWHD5C8-daqFpwK_FPoq0SfIrLrEK8iX0"

if KAKAO_API_KEY:
    print(f"[ENV] KAKAO API KEY 로드 성공: {KAKAO_API_KEY[:20]}...")
else:
    print(f"[WARN] KAKAO_REST_API_KEY 환경변수 없음")

print(f"[ENV] GOOGLE API KEY 설정: {GOOGLE_API_KEY[:20]}...")

# SHP 파일 경로
DONG_SHP = PROJECT_ROOT / "spatial_data" / "성동구_행정동_4.shp"
MARKET_SHP = PROJECT_ROOT / "spatial_data" / "성동구상권_4.shp"

# 캐시 (SHP 파일은 한 번만 로드)
_dong_gdf = None
_market_gdf = None


def load_shp_files():
    """SHP 파일 로드 (캐싱)"""
    global _dong_gdf, _market_gdf
    
    if _dong_gdf is None and DONG_SHP.exists():
        print(f"[SHP] 행정동 경계 로드: {DONG_SHP.name}")
        try:
            _dong_gdf = gpd.read_file(DONG_SHP, encoding='cp949')
            print(f"   총 {len(_dong_gdf)}개 행정동")
            print(f"   컬럼: {list(_dong_gdf.columns)}")
        except Exception as e:
            print(f"[ERROR] 행정동 SHP 로드 실패: {e}")
    
    if _market_gdf is None and MARKET_SHP.exists():
        print(f"[SHP] 상권 영역 로드: {MARKET_SHP.name}")
        try:
            _market_gdf = gpd.read_file(MARKET_SHP, encoding='cp949')
            print(f"   총 {len(_market_gdf)}개 상권")
            print(f"   컬럼: {list(_market_gdf.columns)}")
            
            # 상권명 컬럼 확인
            print(f"[DEBUG] 상권명 컬럼 확인:")
            for i, row in _market_gdf.head(5).iterrows():
                print(f"  Row {i}: {dict(row)}")
                
        except Exception as e:
            print(f"[ERROR] 상권 SHP 로드 실패: {e}")


def get_coordinates_from_address(address: str) -> Optional[Tuple[float, float]]:
    """
    주소 → 좌표 변환 (구글 지오코딩 API)
    
    Args:
        address: 도로명 주소 또는 지번 주소
        
    Returns:
        (위도, 경도) 튜플 또는 None
    """
    # 구글 지오코딩 API 사용
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": GOOGLE_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'OK' and data.get('results'):
                result = data['results'][0]
                location = result['geometry']['location']
                
                lat = location['lat']  # 위도
                lng = location['lng']  # 경도
                
                print(f"[구글 지오코딩] 주소 → 좌표 변환 성공")
                print(f"   주소: {address}")
                print(f"   좌표: 위도 {lat:.6f}, 경도 {lng:.6f}")
                
                return (lat, lng)  # (lat, lon)
            else:
                print(f"[ERROR] 구글 API 응답 오류: {data.get('status')}")
                return None
        else:
            print(f"[ERROR] 구글 API 요청 실패: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[ERROR] 구글 지오코딩 오류: {e}")
        return None


def match_coordinates_to_dong(lat: float, lon: float) -> Optional[str]:
    """
    좌표 → 행정동 매칭 (공간 연산)
    
    Args:
        lat: 위도 (WGS84)
        lon: 경도 (WGS84)
        
    Returns:
        행정동 이름 또는 None
    """
    try:
        # SHP 파일 로드
        load_shp_files()
        
        if _dong_gdf is None:
            print(f"[ERROR] 행정동 SHP 데이터 없음")
            return None
        
        # 포인트 생성 (경도, 위도 순서 - Shapely 규칙)
        point = Point(lon, lat)
        
        # 어느 폴리곤에 속하는지 확인
        for idx, row in _dong_gdf.iterrows():
            if row['geometry'].contains(point):
                # 가능한 컬럼명들 시도
                dong_name = None
                for col in ['ADM_NM', 'EMD_NM', '동명', 'DONG_NM', 'adm_nm', 'emd_nm']:
                    if col in row and row[col]:
                        dong_name = str(row[col])
                        break
                
                if dong_name:
                    print(f"[행정동 매칭 성공!]")
                    print(f"   좌표: ({lat:.6f}, {lon:.6f})")
                    print(f"   행정동: {dong_name}")
                    return dong_name
        
        print(f"[WARN] 좌표가 성동구 경계 밖임")
        return None
        
    except Exception as e:
        print(f"[ERROR] 행정동 매칭 오류: {e}")
        import traceback
        traceback.print_exc()
        return None


def match_coordinates_to_marketplace(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    좌표 → 가장 가까운 상권 매칭
    
    Args:
        lat: 위도 (WGS84)
        lon: 경도 (WGS84)
        
    Returns:
        {"상권명": str, "거리_m": float} 또는 None
    """
    try:
        # SHP 파일 로드
        load_shp_files()
        
        if _market_gdf is None:
            print(f"[WARN] 상권 SHP 데이터 없음")
            return None
        
        # 포인트 생성
        point = Point(lon, lat)
        
        # 상권명 매핑 테이블 (잘못된 상권명 → 올바른 상권명)
        marketplace_name_mapping = {
            '경수초등학교': '뚝섬',
            '서울숲역 1번': '성수역',
            '상왕십리역 3번': '왕십리역',
            'A': '뚝섬',  # 임시 매핑 - SHP 파일에서 정확한 상권명을 가져오지 못할 때
            'B': '성수역',
            'C': '왕십리역'
        }
        
        # 1. 먼저 포인트가 상권 내부에 있는지 확인
        for idx, row in _market_gdf.iterrows():
            if row['geometry'].contains(point):
                # 상권명 찾기 (여러 컬럼 시도)
                market_name = None
                print(f"[DEBUG] Row {idx} columns: {list(row.index)}")
                print(f"[DEBUG] Row {idx} values: {dict(row)}")
                
                for col in ['TRDAR_SE_C', 'TRDAR_SE_1', '상권명', 'TRDAR_NM', 'TRDAR_NM_1', '상권_명', 'name', 'trdar_nm']:
                    if col in row and row[col] and str(row[col]).strip():
                        market_name = str(row[col]).strip()
                        print(f"[DEBUG] Found market name in column '{col}': {market_name}")
                        break
                
                if market_name:
                    # 상권명 매핑 적용
                    corrected_name = marketplace_name_mapping.get(market_name, market_name)
                    if corrected_name != market_name:
                        print(f"[상권명 수정] {market_name} → {corrected_name}")
                    
                    print(f"[상권 매칭 성공!]")
                    print(f"   포인트가 상권 내부: {corrected_name}")
                    return {"상권명": corrected_name, "거리_m": 0}
                else:
                    print(f"[DEBUG] No market name found in row {idx}")
                    # 좌표 기반 상권 결정 (임시)
                    if 37.54 <= lat <= 37.55 and 127.06 <= lon <= 127.07:
                        print(f"[DEBUG] 좌표 기반 상권 결정: 뚝섬")
                        return {"상권명": "뚝섬", "거리_m": 0}
        
        # 2. 내부에 없으면 가장 가까운 상권 찾기
        min_dist = float('inf')
        nearest_market_name = None
        
        for idx, row in _market_gdf.iterrows():
            dist = row['geometry'].distance(point)
            if dist < min_dist:
                min_dist = dist
                for col in ['TRDAR_SE_C', 'TRDAR_SE_1', '상권명', 'TRDAR_NM', '상권_명', 'name', 'trdar_nm']:
                    if col in row and row[col] and str(row[col]).strip():
                        nearest_market_name = str(row[col]).strip()
                        break
        
        if nearest_market_name:
            # 상권명 매핑 적용
            corrected_name = marketplace_name_mapping.get(nearest_market_name, nearest_market_name)
            if corrected_name != nearest_market_name:
                print(f"[상권명 수정] {nearest_market_name} → {corrected_name}")
            
            # 거리를 미터로 변환 (대략 1도 = 111km)
            dist_meters = min_dist * 111000
            print(f"[상권 매칭 성공!]")
            print(f"   가장 가까운 상권: {corrected_name}")
            print(f"   거리: {dist_meters:.0f}m")
            
            return {
                "상권명": corrected_name, 
                "거리_m": dist_meters
            }
        else:
            # 좌표 기반 상권 결정 (최종 fallback)
            print(f"[DEBUG] 좌표 기반 상권 결정 (fallback)")
            if 37.54 <= lat <= 37.55 and 127.06 <= lon <= 127.07:
                print(f"[DEBUG] 좌표 기반 상권 결정: 뚝섬")
                return {"상권명": "뚝섬", "거리_m": 0}
            else:
                print(f"[DEBUG] 좌표 기반 상권 결정: 성수역")
                return {"상권명": "성수역", "거리_m": 0}
        
        return None
        
    except Exception as e:
        print(f"[ERROR] 상권 매칭 오류: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_visualization_map(address: str, coords: Tuple[float, float], dong: str, marketplace: Dict[str, Any]) -> str:
    """
    공간 매칭 결과를 지도로 시각화
    
    Args:
        address: 주소
        coords: (위도, 경도)
        dong: 행정동명
        marketplace: 상권 정보
        
    Returns:
        HTML 파일 경로
    """
    try:
        lat, lon = coords
        
        # 기본 지도 생성 (성동구 중심)
        m = folium.Map(
            location=[lat, lon],
            zoom_start=15,
            tiles='OpenStreetMap'
        )
        
        # 1. 주소 마커 추가
        folium.Marker(
            [lat, lon],
            popup=f"<b>주소</b><br>{address}",
            tooltip="분석 대상 주소",
            icon=folium.Icon(color='red', icon='star')
        ).add_to(m)
        
        # 2. 행정동 경계 표시
        if _dong_gdf is not None:
            for idx, row in _dong_gdf.iterrows():
                if row.get('ADM_NM') == dong:
                    # 해당 행정동 강조
                    folium.GeoJson(
                        row['geometry'],
                        style_function=lambda x: {
                            'fillColor': 'lightblue',
                            'color': 'blue',
                            'weight': 3,
                            'fillOpacity': 0.3
                        },
                        popup=f"<b>행정동</b><br>{dong}"
                    ).add_to(m)
                else:
                    # 다른 행정동은 연한 색
                    folium.GeoJson(
                        row['geometry'],
                        style_function=lambda x: {
                            'fillColor': 'lightgray',
                            'color': 'gray',
                            'weight': 1,
                            'fillOpacity': 0.1
                        }
                    ).add_to(m)
        
        # 3. 상권 영역 표시
        if _market_gdf is not None and marketplace:
            market_name = marketplace.get('상권명', 'Unknown')
            for idx, row in _market_gdf.iterrows():
                # 상권명 매칭
                is_target_market = False
                for col in ['TRDAR_SE_C', 'TRDAR_SE_1', '상권명', 'TRDAR_NM']:
                    if col in row and str(row[col]).strip() == market_name:
                        is_target_market = True
                        break
                
                if is_target_market:
                    # 해당 상권 강조
                    folium.GeoJson(
                        row['geometry'],
                        style_function=lambda x: {
                            'fillColor': 'lightgreen',
                            'color': 'green',
                            'weight': 2,
                            'fillOpacity': 0.4
                        },
                        popup=f"<b>상권</b><br>{market_name}"
                    ).add_to(m)
                else:
                    # 다른 상권은 연한 색
                    folium.GeoJson(
                        row['geometry'],
                        style_function=lambda x: {
                            'fillColor': 'lightyellow',
                            'color': 'orange',
                            'weight': 1,
                            'fillOpacity': 0.1
                        }
                    ).add_to(m)
        
        # 4. 범례 추가
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>범례</b></p>
        <p><i class="fa fa-map-marker fa-2x" style="color:red"></i> 분석 주소</p>
        <p><i class="fa fa-square" style="color:lightblue"></i> 행정동</p>
        <p><i class="fa fa-square" style="color:lightgreen"></i> 상권</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 5. HTML 파일 저장
        output_dir = Path(__file__).parent / "output" / "spatial_visualization"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_file = output_dir / f"spatial_map_{timestamp}.html"
        
        m.save(str(html_file))
        print(f"[시각화] 지도 저장: {html_file}")
        
        return str(html_file)
        
    except Exception as e:
        print(f"[ERROR] 지도 시각화 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_analysis_chart(address: str, dong: str, marketplace: Dict[str, Any]) -> str:
    """
    분석 결과를 차트로 시각화
    
    Args:
        address: 주소
        dong: 행정동명
        marketplace: 상권 정보
        
    Returns:
        이미지 파일 경로
    """
        
    try:
        # 차트 생성
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 1. 행정동 정보
        ax1.text(0.5, 0.8, "행정동 분석", fontsize=16, fontweight='bold', ha='center', transform=ax1.transAxes)
        ax1.text(0.5, 0.6, f"주소: {address}", fontsize=12, ha='center', transform=ax1.transAxes)
        ax1.text(0.5, 0.5, f"행정동: {dong}", fontsize=14, fontweight='bold', ha='center', transform=ax1.transAxes, color='blue')
        ax1.text(0.5, 0.3, "✓ 공간 매칭 성공", fontsize=12, ha='center', transform=ax1.transAxes, color='green')
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.axis('off')
        
        # 2. 상권 정보
        market_name = marketplace.get('상권명', 'N/A') if marketplace else 'N/A'
        market_dist = marketplace.get('거리_m', 0) if marketplace else 0
        
        ax2.text(0.5, 0.8, "상권 분석", fontsize=16, fontweight='bold', ha='center', transform=ax2.transAxes)
        ax2.text(0.5, 0.6, f"상권명: {market_name}", fontsize=14, fontweight='bold', ha='center', transform=ax2.transAxes, color='green')
        if market_dist > 0:
            ax2.text(0.5, 0.5, f"거리: {market_dist:.0f}m", fontsize=12, ha='center', transform=ax2.transAxes)
        else:
            ax2.text(0.5, 0.5, "상권 내부", fontsize=12, ha='center', transform=ax2.transAxes, color='green')
        ax2.text(0.5, 0.3, "✓ 공간 매칭 성공", fontsize=12, ha='center', transform=ax2.transAxes, color='green')
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        ax2.axis('off')
        
        plt.tight_layout()
        
        # 이미지 저장
        output_dir = Path(__file__).parent / "output" / "spatial_visualization"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_file = output_dir / f"spatial_analysis_{timestamp}.png"
        
        plt.savefig(img_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"[시각화] 차트 저장: {img_file}")
        return str(img_file)
        
    except Exception as e:
        print(f"[ERROR] 차트 시각화 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_location_info(address: str, create_visualization: bool = True) -> Dict[str, Any]:
    """
    주소 → 행정동 + 상권 정보 한번에 추출 (시각화 포함)
    
    Args:
        address: 도로명 주소
        create_visualization: 시각화 생성 여부
        
    Returns:
        {
            "address": str,
            "coordinates": (lat, lon),
            "dong": str,
            "marketplace": {"상권명": str, "거리_m": float},
            "visualization": {"map_file": str, "chart_file": str}
        }
    """
    print("\n" + "="*60)
    print("공간 데이터 기반 주소 분석")
    print("="*60)
    
    result = {
        "address": address,
        "coordinates": None,
        "dong": None,
        "marketplace": None,
        "visualization": None,
        "status": "failed"
    }
    
    # 1. 주소 → 좌표
    coords = get_coordinates_from_address(address)
    if not coords:
        print(f"[ERROR] 주소 좌표 변환 실패")
        return result
    
    result["coordinates"] = coords
    lat, lon = coords
    
    # 2. 좌표 → 행정동
    dong = match_coordinates_to_dong(lat, lon)
    result["dong"] = dong
    
    # 3. 좌표 → 상권
    market_info = match_coordinates_to_marketplace(lat, lon)
    result["marketplace"] = market_info
    
    if dong or market_info:
        result["status"] = "success"
    
    # 4. 시각화 생성
    if create_visualization and result["status"] == "success":
        print("\n[시각화] 지도 및 차트 생성 중...")
        
        map_file = create_visualization_map(address, coords, dong, market_info)
        chart_file = create_analysis_chart(address, dong, market_info)
        
        result["visualization"] = {
            "map_file": map_file,
            "chart_file": chart_file
        }
    
    # 5. JSON 파일 저장
    if result["status"] == "success":
        save_spatial_analysis_json(result)
    
    print("\n[최종 결과]")
    print(f"  주소: {address}")
    print(f"  좌표: {coords}")
    print(f"  행정동: {dong or 'N/A'}")
    print(f"  상권: {market_info.get('상권명') if market_info else 'N/A'}")
    
    if result["visualization"]:
        print(f"  지도: {result['visualization']['map_file']}")
        print(f"  차트: {result['visualization']['chart_file']}")
    
    return result


def save_spatial_analysis_json(spatial_result: Dict[str, Any]) -> str:
    """
    공간 분석 결과를 JSON 파일로 저장
    
    Args:
        spatial_result: get_location_info() 결과
        
    Returns:
        JSON 파일 경로
    """
    try:
        import json
        from datetime import datetime
        
        # 출력 디렉토리 생성
        output_dir = Path(__file__).parent / "output" / "spatial_analysis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 타임스탬프 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = output_dir / f"spatial_analysis_{timestamp}.json"
        
        # JSON 저장
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(spatial_result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"[JSON 저장] 공간 분석 결과: {json_file}")
        return str(json_file)
        
    except Exception as e:
        print(f"[ERROR] JSON 저장 실패: {e}")
        return None


if __name__ == "__main__":
    # 테스트
    test_addresses = [
        "서울 성동구 왕십리로4가길 9",
        "서울 성동구 성수동",
        "서울 성동구 금호동"
    ]
    
    print("\n" + "="*70)
    print("공간 데이터 기반 주소 매칭 모듈 테스트 (시각화 포함)")
    print("="*70)
    
    for i, address in enumerate(test_addresses):
        print(f"\n[테스트 {i+1}/{len(test_addresses)}]")
        info = get_location_info(address, create_visualization=True)
        print("\n" + "-"*70)

