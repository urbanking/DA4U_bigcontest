"""
주소 기반 지역 종합 분석 모듈
- 주소를 입력하면 좌표로 변환
- 300m 버퍼 내의 모든 파노라마 이미지 수집
- Gemini 2.5 Flash로 모든 이미지를 분석 (OpenAI SDK 호환)
- 종합 리포트 생성 (상권분위기, 도로분위기, 주거/상가, 청결도 등)
"""

import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import base64
from openai import OpenAI
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import io
from datetime import datetime
import numpy as np
from typing import List, Dict, Optional
import folium
from folium import plugins
import shutil
import warnings
import time
warnings.filterwarnings('ignore')


def init_openai_client():
    """Gemini OpenAI 호환 API 클라이언트 초기화"""
    from pathlib import Path
    
    # 프로젝트 루트의 env 파일 찾기
    current_path = Path(__file__)
    root_path = current_path
    while root_path.parent != root_path:
        root_path = root_path.parent
        env_path = root_path / "env"
        if env_path.exists():
            load_dotenv(env_path, override=True)
            print(f"[Panorama] Loaded env from: {env_path}")
            break
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY가 env 파일에 설정되지 않았습니다.")
    
    print(f"[Panorama] Using API key: {api_key[:20]}...")
    
    # Gemini OpenAI 호환 API 사용
    return OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )


def address_to_coordinates(address: str) -> tuple:
    """
    주소를 좌표로 변환 (Kakao API 사용)
    
    Parameters:
    -----------
    address : str
        한국 주소 (예: "서울특별시 성동구 왕십리로 222")
        
    Returns:
    --------
    tuple : (longitude, latitude)
    """
    from geopy.geocoders import Nominatim
    import requests
    
    load_dotenv()
    kakao_key = os.getenv('KAKAO_REST_API_KEY')
    
    # Kakao API 사용 (더 정확함)
    if kakao_key:
        url = 'https://dapi.kakao.com/v2/local/search/address.json'
        headers = {'Authorization': f'KakaoAK {kakao_key}'}
        params = {'query': address}
        try:
            # Add sane timeouts to avoid hanging on network issues
            response = requests.get(url, headers=headers, params=params, timeout=(5, 15))
            if response.status_code == 200:
                result = response.json()
                if result.get('documents'):
                    doc = result['documents'][0]
                    lon = float(doc['x'])
                    lat = float(doc['y'])
                    print(f"[OK] Kakao API: {address} -> ({lat:.6f}, {lon:.6f})")
                    return lon, lat
        except requests.RequestException as e:
            print(f"[WARN] Kakao API 요청 실패: {e}")
    
    # Fallback: Nominatim (무료, 느림)
    print("[INFO] Kakao API 미사용/실패로 Nominatim 사용 (느릴 수 있음)")
    geolocator = Nominatim(user_agent="street_analyzer")
    # Nominatim can be slow; provide a timeout
    location = geolocator.geocode(address, timeout=15)
    
    if location:
        print(f"[OK] Nominatim: {address} -> ({location.latitude:.6f}, {location.longitude:.6f})")
        return location.longitude, location.latitude
    else:
        raise ValueError(f"[ERROR] 주소를 찾을 수 없습니다: {address}")


def find_images_in_buffer(center_lon: float, 
                          center_lat: float, 
                          buffer_meters: float,
                          data_csv_path: str,
                          image_folder: str) -> List[Dict]:
    """
    중심 좌표로부터 버퍼(반경) 내의 모든 이미지 찾기
    
    Parameters:
    -----------
    center_lon : float
        중심점 경도
    center_lat : float
        중심점 위도
    buffer_meters : float
        버퍼 반경 (미터)
    data_csv_path : str
        포인트 데이터 CSV 경로
    image_folder : str
        이미지 폴더 경로
        
    Returns:
    --------
    List[Dict] : 버퍼 내 이미지 정보 리스트
    """
    # CSV 로드
    df = pd.read_csv(data_csv_path)
    
    # GeoDataFrame 생성
    geometry = [Point(xy) for xy in zip(df['pano_lon'], df['pano_lat'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
    
    # UTM으로 투영 (미터 단위 계산을 위해)
    gdf_utm = gdf.to_crs('EPSG:5179')  # 한국 중부 원점 (성동구 적합)
    
    # 중심점 생성 및 투영
    center_point = gpd.GeoDataFrame(
        [{'geometry': Point(center_lon, center_lat)}],
        crs='EPSG:4326'
    ).to_crs('EPSG:5179')
    
    # 버퍼 생성
    buffer = center_point.geometry.buffer(buffer_meters)
    
    # 버퍼 내 점들 필터링
    within_buffer_utm = gdf_utm[gdf_utm.geometry.within(buffer.iloc[0])].copy()
    
    # 중심점으로부터의 거리 계산 (UTM 좌표계에서 미터 단위로)
    within_buffer_utm['distance_m'] = within_buffer_utm.geometry.distance(
        center_point.geometry.iloc[0]
    )
    
    # 다시 WGS84로 변환 (거리는 이미 계산됨)
    within_buffer = within_buffer_utm.to_crs('EPSG:4326')
    
    # 이미지 정보 수집
    images_info = []
    image_folder_path = Path(image_folder)
    
    for idx, row in within_buffer.iterrows():
        point_id = row['point_ID']
        pano_id = row['pano_id']
        
        # 이미지 파일 경로
        image_filename = f"point_{point_id}_pano_{pano_id}.jpg"
        image_path = image_folder_path / image_filename
        
        if image_path.exists():
            images_info.append({
                'point_id': int(point_id),
                'pano_id': pano_id,
                'lon': float(row['pano_lon']),
                'lat': float(row['pano_lat']),
                'distance_m': float(row['distance_m']),
                'image_path': str(image_path)
            })
    
    # 거리순 정렬
    images_info.sort(key=lambda x: x['distance_m'])
    
    return images_info


def extract_panorama_section(image_path: str, section: str = 'front') -> Image.Image:
    """
    파노라마 이미지에서 특정 섹션 추출
    
    Parameters:
    -----------
    image_path : str
        이미지 파일 경로
    section : str
        추출할 섹션 ('front', 'back', 'left', 'right')
        
    Returns:
    --------
    PIL.Image : 추출된 이미지
    """
    img = Image.open(image_path)
    width, height = img.size
    
    # 1x6 파노라마 가정
    section_width = width // 6
    
    sections = {
        'left': (0, 0, section_width, height),
        'front': (section_width, 0, section_width * 2, height),
        'right': (section_width * 2, 0, section_width * 3, height),
        'back': (section_width * 3, 0, section_width * 4, height),
    }
    
    if section in sections:
        coords = sections[section]
        return img.crop(coords)
    else:
        return img.crop(sections['front'])

def _downscale_if_needed(pil_image: Image.Image, max_dim: int = 1024) -> Image.Image:
    """과도한 업로드를 방지하기 위해 이미지를 축소합니다."""
    if max(pil_image.size) <= max_dim:
        return pil_image
    img = pil_image.copy()
    img.thumbnail((max_dim, max_dim), Image.LANCZOS)
    return img


def encode_image_pil(pil_image: Image.Image, quality: int = 80, max_dim: int = 1024) -> str:
    """PIL 이미지를 base64로 인코딩 (크기 제한 및 품질 조정 포함)"""
    img = _downscale_if_needed(pil_image, max_dim=max_dim)
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=quality)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def get_individual_analysis_prompt() -> str:
    """개별 이미지 분석용 프롬프트"""
    return """당신은 상권 전략 컨설턴트입니다. 이 거리 이미지를 세밀하게 분석하여 JSON 형식으로 답변하세요.

[분석 목적] 
이 지점의 상업적 가치, 보행 환경, 청결도, 건물 상태를 정량적·정성적으로 평가합니다.

[출력 형식]

{
  "report_metadata": {
    "analyst_persona": "상권 전략 컨설턴트",
    "analysis_type": "정성적 서술 및 정량적 감사를 결합한 하이브리드 시각 분석",
    "analysis_timestamp": "자동생성"
  },
  
  "visit_summary": {
    "location_headline": "이 장소의 첫인상을 한 문장으로 표현하세요 (예: 활기찬 상업지역의 중심부)",
    "overall_impression_prose": "이 장소에 대한 전반적인 느낌을 2-3문장으로 서술하세요. 공간의 분위기, 특징을 포함하세요."
  },
  
  "virtual_walkthrough_notes": {
    "objective_sketch": {
      "space_and_buildings": "눈에 보이는 공간과 건물을 묘사하세요. 건물 높이, 형태, 배치, 용도 등을 포함하세요.",
      "street_details": "도로와 보도의 상태를 묘사하세요. 보도블럭, 가로수, 벤치, 가로등 등을 포함하세요."
    },
    "sensory_experience": {
      "dominant_colors_and_textures": "이 공간을 지배하는 색감과 재질감을 설명하세요 (밝음/어두움, 깨끗함/낡음 등)",
      "imagined_sounds": "이곳에서 들릴 법한 소리를 상상하여 묘사하세요 (차량 소리, 사람들 목소리, 조용함 등)"
    }
  },
  
  "people_and_energy": {
    "observed_tribes_description": "보이는 사람들의 유형과 특징을 묘사하세요. 사람이 없다면 '사람 없음'이라고 쓰세요.",
    "street_energy_level": "거리의 에너지 레벨을 표현하세요 (활기참/차분함/조용함/침체됨 중 선택)"
  },
  
  "commercial_ecosystem_insight": {
    "dominant_store_types": "이 거리의 주요 가게 종류를 나열하세요 (음식점, 카페, 편의점 등). 없으면 '상점 없음'",
    "signs_of_change_or_stability": "상권의 변화나 안정성 신호를 설명하세요 (신규 개업, 폐업, 리모델링 흔적 등)",
    "opportunity_for_target_business": {
      "business_category": "이 지역에 적합해 보이는 업종 (예: 카페, 음식점, 편의점 등)",
      "narrative_insight": "이 분위기에서 해당 업종이 들어선다면 어떤 역할과 컨셉으로 접근해야 할지 2-3문장으로 서술하세요."
    }
  },
  
  "final_verdict_from_expert": {
    "recommendation_prose": "이 장소에 대한 최종 전문가 의견을 3-4문장으로 작성하세요. 창업자나 투자자에게 실질적인 조언을 제공하세요."
  },
  
  "quantitative_audit": {
    "commercial_vitality": {
      "Storefront_Count": "시야에 보이는 상점 전면 개수 (정수)",
      "Operational_Status": "영업 중인 상점 수 (정수, 판단 불가시 N/A)",
      "Customer_Presence": "고객이 보이는 상점 수 (정수)",
      "Promotional_Activity": "홍보물이 있는 상점 수 (정수)"
    },
    "street_attractiveness": {
      "Facade_Condition": "건물 외관 상태: 2(깨끗하고 관리됨) | 1(보통) | 0(낡고 방치됨)",
      "Design_Diversity": "디자인 다양성: 2(다양하고 개성있음) | 1(보통) | 0(단조로움)",
      "Amenity_Presence": "편의시설: 2(벤치/그늘 등 많음) | 1(일부 있음) | 0(없음)",
      "Brand_Type": "브랜드 유형: 2(프랜차이즈 많음) | 1(혼합) | 0(독립 상점 위주)"
    },
    "pedestrian_experience": {
      "Sidewalk_Clutter": "보도 상태: 2(깨끗하고 넓음) | 1(보통) | 0(어지럽거나 좁음)",
      "Weather_Protection": "날씨 보호: 2(캐노피/차양 있음) | 1(일부) | 0(없음)",
      "Lighting_Proxy": "조명 상태: 2(밝고 충분) | 1(보통) | 0(어둡거나 부족)"
    }
  }
}

[점수 기준]
- 정수 카운트 (Storefront_Count 등): 실제로 보이는 개수를 세어 기입하세요
- 0-2 점수: 2=우수/좋음, 1=보통/평균, 0=나쁨/열악
- N/A는 정말 판단이 불가능한 경우만 사용하세요

[중요] 
오직 JSON 형식만 출력하세요. 마크다운이나 추가 설명을 포함하지 마세요."""


def get_synthesis_prompt(individual_results: List[Dict]) -> str:
    """종합 분석용 프롬프트"""
    summary = f"총 {len(individual_results)}개 지점의 개별 분석 결과:\n\n"
    
    for i, result in enumerate(individual_results[:10], 1):  # 최대 10개만 포함
        analysis = result.get('analysis', {})
        visit = analysis.get('visit_summary', {})
        commercial = analysis.get('commercial_ecosystem_insight', {})
        energy = analysis.get('people_and_energy', {})
        
        summary += f"지점 {i} (중심에서 {result['distance_m']:.0f}m):\n"
        summary += f"   헤드라인: {visit.get('location_headline', 'N/A')}\n"
        summary += f"   주요 상점: {commercial.get('dominant_store_types', 'N/A')}\n"
        summary += f"   에너지: {energy.get('street_energy_level', 'N/A')}\n"
        
        # 정량 지표도 포함
        quant = analysis.get('quantitative_audit', {})
        if quant:
            cv = quant.get('commercial_vitality', {})
            summary += f"   상점수: {cv.get('Storefront_Count', 'N/A')}, "
            summary += f"영업중: {cv.get('Operational_Status', 'N/A')}\n"
        summary += "\n"
    
    if len(individual_results) > 10:
        summary += f"... 외 {len(individual_results) - 10}개 지점 데이터 생략\n\n"
    
    prompt = f"""[상권 전략 컨설턴트 종합 분석]

{summary}

[당신의 임무]
위의 개별 지점 분석 결과들을 종합하여, 이 지역 전체의 특성을 평가하고 상업적 잠재력을 진단하세요.
단순 평균이 아닌, 전체적인 패턴과 흐름을 파악하여 통찰력 있는 종합 리포트를 작성하세요.

[출력 형식]

{{
  "area_summary": {{
    "overall_character": "이 지역의 전반적인 특성을 2-3문장으로 종합 서술하세요. 상권 성격, 공간 특성, 분위기 등을 통합적으로 기술하세요.",
    "dominant_zone_type": "주거지역|상업지역|혼합지역|공업지역|공원/녹지 중 하나 선택",
    "primary_commercial_type": "이 지역 상권의 주요 유형을 구체적으로 기술하세요 (예: 근린형 생활상가, 유흥 중심 상권, 카페거리 등)"
  }},
  
  "comprehensive_scores": {{
    "commercial_atmosphere": "상권 분위기 점수 (0-10): 상업 활동의 활발함, 매출 잠재력 등을 고려",
    "street_atmosphere": "도로 분위기 점수 (0-10): 거리의 쾌적함, 시각적 매력도 등을 고려",
    "cleanliness": "청결도 점수 (0-10): 거리 및 건물의 깨끗함, 쓰레기 관리 상태 등을 고려",
    "maintenance": "유지보수 상태 점수 (0-10): 건물, 도로, 시설물의 관리 상태 등을 고려",
    "walkability": "보행 편의성 점수 (0-10): 보행자 친화성, 인도 상태, 접근성 등을 고려",
    "safety_perception": "안전 인식 점수 (0-10): 조명, 시야, 관리 상태 등에서 느껴지는 안전감을 고려",
    "business_diversity": "업종 다양성 점수 (0-10): 다양한 업종의 혼합 정도, 선택의 폭 등을 고려",
    "residential_suitability": "거주 적합도 점수 (0-10): 주거지로서의 쾌적성과 편의성을 고려",
    "commercial_suitability": "상업 적합도 점수 (0-10): 상업 활동을 위한 입지 및 환경의 적합성을 고려"
  }},
  
  "detailed_assessment": {{
    "strengths": [
      "이 지역의 주요 강점 1 (구체적이고 실질적으로)",
      "이 지역의 주요 강점 2",
      "이 지역의 주요 강점 3"
    ],
    "weaknesses": [
      "이 지역의 주요 약점 1 (개선이 필요한 부분)",
      "이 지역의 주요 약점 2",
      "이 지역의 주요 약점 3"
    ],
    "recommended_business_types": [
      "이 지역에 적합한 업종 1 (구체적인 업종명)",
      "이 지역에 적합한 업종 2",
      "이 지역에 적합한 업종 3"
    ],
    "foot_traffic_estimate": "상|중|하 중 하나 선택 (관찰된 인구 밀도 및 상권 활력도 기반)",
    "competition_level": "높음|보통|낮음 중 하나 선택 (기존 상점 밀도 및 경쟁 강도 기반)"
  }},
  
  "final_recommendation": "상권 전략 컨설턴트로서 이 지역에 대한 최종 종합 의견을 7-10문장으로 매우 자세하게 작성하세요. 다음 내용을 모두 포함해야 합니다: (1) 이 지역의 전반적인 평가와 특징, (2) 상권의 강점과 활용 방안, (3) 주의해야 할 약점이나 리스크, (4) 추천하는 업종과 그 이유, (5) 성공을 위한 구체적인 전략이나 접근법, (6) 예상 투자 규모나 수익성에 대한 견해, (7) 최종 추천 여부와 근거. 창업자나 투자자가 실질적인 의사결정을 할 수 있도록 구체적이고 상세하게 작성하세요."
}}

[점수 산정 가이드라인]
- 0-3점: 매우 나쁨, 큰 문제 있음, 회피 권장
- 4-5점: 평균 이하, 개선 필요
- 6-7점: 보통 수준, 평균적
- 8-9점: 좋음, 경쟁력 있음
- 10점: 매우 우수, 최상급

[중요 지침]
1. 개별 지점들의 단순 평균이 아니라, 전체적인 패턴과 경향성을 파악하세요
2. 모든 점수는 정수(0-10)로 기입하세요
3. 강점/약점/추천업종은 각각 정확히 3개씩 작성하세요
4. final_recommendation은 반드시 7-10문장으로 매우 상세하게 작성하세요
5. JSON 형식만 출력하고, 다른 설명은 포함하지 마세요"""
    
    return prompt


def _chat_with_retry(client: OpenAI, *, messages, model: str = "gemini-2.5-flash", temperature: float = 0.3, timeout: float = None, max_retries: int = 2, backoff_base: float = 1.5):
    """Gemini Chat Completions 호출을 재시도/타임아웃과 함께 수행 (OpenAI SDK 호환)"""
    last_err = None
    for attempt in range(1, max_retries + 2):
        try:
            kwargs = {
                "model": model,
                "temperature": temperature,
                "messages": messages,
            }
            if timeout is not None:
                kwargs["timeout"] = timeout
            return client.chat.completions.create(**kwargs)
        except Exception as e:
            last_err = e
            wait = backoff_base ** attempt + (0.1 * attempt)
            print(f"      [WARN] Gemini API 호출 실패 (시도 {attempt}): {e.__class__.__name__}: {e}")
            if attempt <= max_retries:
                print(f"      [INFO] {wait:.1f}s 후 재시도")
                time.sleep(wait)
            else:
                break
    raise last_err


def analyze_image_with_gpt(client: OpenAI, 
                           image_path: str, 
                           prompt: str) -> Dict:
    """Gemini 2.5 Flash로 단일 이미지 분석"""
    # 시뮬레이션 모드 (테스트/네트워크 문제 방지)
    if os.getenv("SIMULATE_OPENAI", "0") == "1":
        return {
            "report_metadata": {"analyst_persona": "상권 전략 컨설턴트", "analysis_type": "simulate", "analysis_timestamp": datetime.now().isoformat()},
            "visit_summary": {"location_headline": "시뮬레이션 응답", "overall_impression_prose": "테스트용 더미 응답"},
        }

    # 이미지 추출 및 인코딩
    extracted_image = extract_panorama_section(image_path, 'front')
    base64_image = encode_image_pil(extracted_image, quality=80, max_dim=1024)

    # 환경설정 기반 타임아웃과 재시도 설정 (기본: 타임아웃 없음)
    load_dotenv()
    if os.getenv("OPENAI_NO_TIMEOUT", "0") == "1":
        timeout_s = None
    else:
        if os.getenv("OPENAI_TIMEOUT"):
            try:
                timeout_s = float(os.getenv("OPENAI_TIMEOUT"))
            except Exception:
                timeout_s = None
        else:
            timeout_s = None
    try:
        max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "2"))
    except Exception:
        max_retries = 2

    print("      [INFO] Gemini API 호출 시작 (이미지 업로드, 제한된 크기)")
    start_ts = time.time()
    response = _chat_with_retry(
        client,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ],
            }
        ],
        model="gemini-2.5-flash",
        temperature=0.3,
        timeout=timeout_s,
        max_retries=max_retries,
    )
    elapsed = time.time() - start_ts
    print(f"      [OK] Gemini API 응답 수신 ({elapsed:.1f}s 소요)")

    result_text = response.choices[0].message.content
    
    # 응답 체크
    if not result_text or result_text.strip() == "":
        print(f"[ERROR] Gemini 빈 응답 반환")
        return {
            "error": "Empty response from Gemini",
            "description": "이미지 분석 실패 (빈 응답)"
        }
    
    # JSON 파싱
    try:
        json_pattern = r'```json\s*(.*?)\s*```|(\{.*\})'
        matches = re.search(json_pattern, result_text, re.DOTALL)
        
        if matches:
            json_str = matches.group(1) if matches.group(1) else matches.group(2)
        else:
            json_str = result_text.strip()
        
        return json.loads(json_str)
    except Exception as e:
        print(f"[ERROR] JSON 파싱 오류: {e}")
        print(f"[DEBUG] 응답 미리보기 (처음 200자): {result_text[:200]}")
        return {
            "error": str(e),
            "raw_response": result_text,
            "description": "이미지 분석 실패 (JSON 파싱 오류)"
        }


def synthesize_analysis(client: OpenAI, individual_results: List[Dict]) -> Dict:
    """개별 분석 결과들을 종합하여 최종 리포트 생성"""
    # 시뮬레이션 모드
    if os.getenv("SIMULATE_OPENAI", "0") == "1":
        return {
            "area_summary": {"dominant_zone_type": "시뮬레이션"},
            "comprehensive_scores": {"commercial_atmosphere": 7, "street_atmosphere": 7, "cleanliness": 7, "walkability": 7, "business_diversity": 7},
            "detailed_assessment": {"strengths": ["더미"], "weaknesses": ["더미"], "recommended_business_types": ["더미"]},
            "final_recommendation": "시뮬레이션 결과",
        }

    prompt = get_synthesis_prompt(individual_results)

    load_dotenv()
    if os.getenv("OPENAI_NO_TIMEOUT", "0") == "1":
        timeout_s = None
    else:
        if os.getenv("OPENAI_TIMEOUT"):
            try:
                timeout_s = float(os.getenv("OPENAI_TIMEOUT"))
            except Exception:
                timeout_s = None
        else:
            timeout_s = None
    try:
        max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "2"))
    except Exception:
        max_retries = 2

    print("      [INFO] Gemini 종합 분석 호출 시작")
    start_ts = time.time()
    response = _chat_with_retry(
        client,
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="gemini-2.5-flash",
        temperature=0.3,
        timeout=timeout_s,
        max_retries=max_retries,
    )
    elapsed = time.time() - start_ts
    print(f"      [OK] 종합 분석 응답 수신 ({elapsed:.1f}s 소요)")

    result_text = response.choices[0].message.content
    
    # 응답 체크
    if not result_text or result_text.strip() == "":
        print(f"[ERROR] Gemini 빈 응답 반환 (종합 분석)")
        return {
            "error": "Empty response from Gemini",
            "analysis_type": "synthesis"
        }
    
    # JSON 파싱
    try:
        json_pattern = r'```json\s*(.*?)\s*```|(\{.*\})'
        matches = re.search(json_pattern, result_text, re.DOTALL)
        
        if matches:
            json_str = matches.group(1) if matches.group(1) else matches.group(2)
        else:
            json_str = result_text.strip()
        
        return json.loads(json_str)
    except Exception as e:
        print(f"[ERROR] 종합 분석 JSON 파싱 오류: {e}")
        print(f"[DEBUG] 종합 분석 응답 미리보기 (처음 200자): {result_text[:200]}")
        return {
            "error": str(e),
            "raw_response": result_text,
            "analysis_type": "synthesis"
        }


def create_analysis_map(center_lon: float, 
                        center_lat: float, 
                        buffer_meters: float,
                        analyzed_images: List[Dict],
                        synthesis: Dict,
                        output_path: str = "analysis_map.html") -> str:
    """
    분석 결과를 지도로 시각화
    
    Parameters:
    -----------
    center_lon : float
        중심점 경도
    center_lat : float
        중심점 위도
    buffer_meters : float
        버퍼 반경 (미터)
    analyzed_images : List[Dict]
        분석된 이미지 정보 리스트
    synthesis : Dict
        종합 분석 결과
    output_path : str
        저장할 HTML 파일 경로
        
    Returns:
    --------
    str : 생성된 HTML 파일 경로
    """
    # 지도 생성
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=16,
        tiles='OpenStreetMap'
    )
    
    # 중심점 마커
    folium.Marker(
        [center_lat, center_lon],
        popup=f"<b>분석 중심점</b><br>위도: {center_lat:.6f}<br>경도: {center_lon:.6f}",
        tooltip="분석 중심점",
        icon=folium.Icon(color='red', icon='star', prefix='fa')
    ).add_to(m)
    
    # 버퍼 원
    folium.Circle(
        [center_lat, center_lon],
        radius=buffer_meters,
        color='blue',
        fill=True,
        fillColor='blue',
        fillOpacity=0.1,
        popup=f"<b>분석 범위</b><br>반경: {buffer_meters}m",
        tooltip=f"분석 범위 ({buffer_meters}m)"
    ).add_to(m)
    
    # 분석된 지점들 표시
    for i, img_info in enumerate(analyzed_images, 1):
        lat = img_info['lat']
        lon = img_info['lon']
        distance = img_info['distance_m']
        
        # 분석 결과 가져오기
        analysis = img_info.get('analysis', {})
        visit = analysis.get('visit_summary', {})
        commercial = analysis.get('commercial_ecosystem_insight', {})
        quant = analysis.get('quantitative_audit', {})
        
        # 팝업 내용 구성
        popup_html = f"""
        <div style='width:300px'>
            <h4>지점 {i}</h4>
            <hr>
            <b>거리:</b> {distance:.1f}m<br>
            <b>Point ID:</b> {img_info['point_id']}<br>
            <br>
            <b>첫인상:</b><br>
            {visit.get('location_headline', 'N/A')}<br>
            <br>
            <b>주요 상점:</b><br>
            {commercial.get('dominant_store_types', 'N/A')}<br>
            <br>
        """
        
        # 정량 지표 추가
        if quant:
            cv = quant.get('commercial_vitality', {})
            popup_html += f"""
            <b>정량 지표:</b><br>
            - 상점 수: {cv.get('Storefront_Count', 'N/A')}<br>
            - 영업중: {cv.get('Operational_Status', 'N/A')}<br>
            """
        
        popup_html += "</div>"
        
        # 거리에 따른 색상 (가까울수록 진한 녹색)
        if distance < buffer_meters * 0.3:
            color = 'darkgreen'
        elif distance < buffer_meters * 0.7:
            color = 'green'
        else:
            color = 'lightgreen'
        
        folium.CircleMarker(
            [lat, lon],
            radius=8,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"지점 {i} ({distance:.0f}m)"
        ).add_to(m)
    
    # 종합 분석 결과를 지도에 추가
    if synthesis and "area_summary" in synthesis:
        area_summary = synthesis['area_summary']
        scores = synthesis.get('comprehensive_scores', {})
        
        legend_html = f"""
        <div style='position: fixed; 
                    bottom: 50px; right: 50px; width: 350px; height: auto; 
                    background-color: white; z-index:9999; font-size:14px;
                    border:2px solid grey; border-radius: 5px; padding: 10px;
                    box-shadow: 2px 2px 6px rgba(0,0,0,0.3);'>
            <h4 style='margin-top:0'>종합 분석 결과</h4>
            <hr>
            <b>지역 유형:</b> {area_summary.get('dominant_zone_type', 'N/A')}<br>
            <b>상권 유형:</b> {area_summary.get('primary_commercial_type', 'N/A')}<br>
            <br>
            <b>종합 점수:</b><br>
            <div style='margin-left: 10px'>
                상권 분위기: {scores.get('commercial_atmosphere', 'N/A')}/10<br>
                도로 분위기: {scores.get('street_atmosphere', 'N/A')}/10<br>
                청결도: {scores.get('cleanliness', 'N/A')}/10<br>
                보행환경: {scores.get('walkability', 'N/A')}/10<br>
            </div>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))
    
    # 저장
    m.save(output_path)
    print(f"[지도] 시각화 저장: {output_path}")
    
    return output_path


def analyze_area_by_address(address: str,
                            buffer_meters: float = 300,
                            data_csv_path: Optional[str] = None,
                            image_folder: Optional[str] = None,
                            max_images: int = 5,
                            output_json_path: Optional[str] = None,
                            create_map: bool = True,
                            map_output_path: Optional[str] = None) -> Dict:
    """
    주소를 입력받아 해당 지역의 종합 분석 수행
    
    Parameters:
    -----------
    address : str
        분석할 주소 (예: "서울특별시 성동구 왕십리로 222")
    buffer_meters : float
        분석 반경 (미터), 기본값 300m
    data_csv_path : str, optional
        포인트 데이터 CSV 경로 (.env에서 자동 로드)
    image_folder : str, optional
        이미지 폴더 경로 (.env에서 자동 로드)
    max_images : int
        최대 분석할 이미지 개수 (비용 절감용), 기본값 5개
    output_json_path : str, optional
        결과를 저장할 JSON 파일 경로
    create_map : bool
        지도 시각화 생성 여부, 기본값 True
    map_output_path : str, optional
        지도 HTML 파일 저장 경로 (기본값: 자동 생성)
        
    Returns:
    --------
    Dict : 종합 분석 결과
    
    Example:
    --------
    >>> result = analyze_area_by_address("서울특별시 성동구 왕십리로 222", buffer_meters=300)
    >>> print(result['synthesis']['comprehensive_scores']['commercial_atmosphere'])
    >>> print(result['synthesis']['final_recommendation'])
    """
    
    print("=" * 80)
    print("주소 기반 지역 종합 분석 시작")
    print("=" * 80)
    
    # .env에서 경로 로드
    load_dotenv()
    
    if data_csv_path is None:
        data_csv_path = os.getenv('PANOID_FILE')
        if not data_csv_path:
            data_csv_path = "C:/img_gpt/Step1_Result_final (1).csv"
    
    if image_folder is None:
        image_folder = os.getenv('IMAGE_FOLDER')
        if not image_folder:
            image_folder = "C:/img_gpt/downloaded_img"
    
    # 1. 주소 -> 좌표 변환
    print(f"\n[주소] {address}")
    print(f"[지오코딩] 주소 변환 중...")
    center_lon, center_lat = address_to_coordinates(address)
    print(f"[OK] 좌표: ({center_lat:.6f}, {center_lon:.6f})")
    
    # 2. 버퍼 내 이미지 찾기
    print(f"\n[검색] 반경 {buffer_meters}m 내의 이미지 검색 중...")
    images_info = find_images_in_buffer(
        center_lon, center_lat, buffer_meters,
        data_csv_path, image_folder
    )
    
    print(f"[OK] 총 {len(images_info)}개 이미지 발견")
    
    if len(images_info) == 0:
        return {
            "error": "버퍼 내에 이미지가 없습니다.",
            "center_coordinates": {"lon": center_lon, "lat": center_lat},
            "buffer_meters": buffer_meters
        }
    
    # 3. 이미지 개수 제한
    if len(images_info) > max_images:
        print(f"[INFO] 이미지가 {len(images_info)}개로 많아 가장 가까운 {max_images}개만 분석합니다.")
        images_info = images_info[:max_images]
    
    # 4. Gemini 클라이언트 초기화
    print(f"\n[API] Gemini API 초기화 중...")
    client = init_openai_client()
    
    # 5. 개별 이미지 분석
    print(f"\n[분석] 개별 이미지 분석 중 (총 {len(images_info)}개)...")
    individual_results = []
    individual_prompt = get_individual_analysis_prompt()
    
    for i, img_info in enumerate(images_info, 1):
        print(f"  [{i}/{len(images_info)}] Point {img_info['point_id']} (거리: {img_info['distance_m']:.1f}m) 분석 중...")
        
        try:
            analysis = analyze_image_with_gpt(
                client, 
                img_info['image_path'], 
                individual_prompt
            )
            
            individual_results.append({
                **img_info,
                'analysis': analysis
            })
            
            # 간단한 결과 출력
            vsum = analysis.get('visit_summary', {})
            print(f"      [OK] 완료 - {vsum.get('location_headline', 'N/A')[:40]}...")
            
        except Exception as e:
            print(f"      [ERROR] 오류: {e}")
            individual_results.append({
                **img_info,
                'analysis': {"error": str(e)}
            })
    
    # 6. 종합 분석
    print(f"\n[종합] 종합 분석 생성 중...")
    synthesis = synthesize_analysis(client, individual_results)
    print(f"[OK] 종합 분석 완료")
    
    # 7. 결과 구성
    result = {
        "metadata": {
            "input_address": address,
            "center_coordinates": {
                "longitude": center_lon,
                "latitude": center_lat
            },
            "buffer_meters": buffer_meters,
            "total_images_found": len(images_info),
            "images_analyzed": len(individual_results),
            "analysis_timestamp": datetime.now().isoformat()
        },
        "individual_analyses": individual_results,
        "synthesis": synthesis
    }
    
    # 8. output 폴더 구조 생성 및 파일 저장
    print(f"\n[저장] 결과 파일 저장 중...")
    
    # output 폴더 생성
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_folder = f"C:/img_gpt/output/analysis_{timestamp}"
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(f"{output_folder}/images", exist_ok=True)
    
    # 8-1. 전체 분석 결과 JSON 저장 (종합 분석 포함)
    full_json_path = f"{output_folder}/analysis_result.json"
    with open(full_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  [OK] 전체 분석 결과 (종합 분석 포함): {full_json_path}")
    
    # 8-3. 분석에 사용한 이미지 복사
    print(f"\n[복사] 분석에 사용한 이미지 복사 중...")
    for i, img_info in enumerate(individual_results, 1):
        src_path = img_info['image_path']
        filename = Path(src_path).name
        dst_path = f"{output_folder}/images/{filename}"
        shutil.copy2(src_path, dst_path)
        print(f"  [{i}/{len(individual_results)}] {filename}")
    print(f"  [OK] 총 {len(individual_results)}개 이미지 복사 완료")
    
    # 9. 지도 시각화 생성
    if create_map:
        map_output_path = f"{output_folder}/analysis_map.html"
        create_analysis_map(
            center_lon, center_lat, buffer_meters,
            individual_results, synthesis,
            map_output_path
        )
    
    # output 폴더 경로를 결과에 추가
    result['output_folder'] = output_folder
    
    # 10. 요약 출력
    print("\n" + "=" * 80)
    print("[결과] 분석 결과 요약")
    print("=" * 80)
    print(f"\n[폴더] 결과 저장 위치: {output_folder}")
    print(f"  - analysis_result.json (전체 분석 + 종합 분석)")
    print(f"  - analysis_map.html (지도)")
    print(f"  - images/ ({len(individual_results)}개 이미지)")
    
    if "area_summary" in synthesis:
        print(f"\n[특성] 지역 특성: {synthesis['area_summary']['dominant_zone_type']}")
        print(f"[상권] 상권 유형: {synthesis['area_summary'].get('primary_commercial_type', 'N/A')}")
        
        if "comprehensive_scores" in synthesis:
            scores = synthesis['comprehensive_scores']
            print(f"\n[점수] 종합 점수:")
            print(f"   - 상권 분위기: {scores.get('commercial_atmosphere', 0)}/10")
            print(f"   - 도로 분위기: {scores.get('street_atmosphere', 0)}/10")
            print(f"   - 청결도: {scores.get('cleanliness', 0)}/10")
            print(f"   - 보행환경: {scores.get('walkability', 0)}/10")
            print(f"   - 업종다양성: {scores.get('business_diversity', 0)}/10")
        
        if "detailed_assessment" in synthesis:
            assess = synthesis['detailed_assessment']
            print(f"\n[강점]")
            for strength in assess.get('strengths', [])[:3]:
                print(f"   - {strength}")
            
            print(f"\n[약점]")
            for weakness in assess.get('weaknesses', [])[:3]:
                print(f"   - {weakness}")
            
            print(f"\n[업종] 추천 업종:")
            for biz in assess.get('recommended_business_types', [])[:3]:
                print(f"   - {biz}")
        
        if "final_recommendation" in synthesis:
            print(f"\n[의견] 전문가 종합 의견:")
            print(f"   {synthesis['final_recommendation']}")
    
    print("\n" + "=" * 80)
    
    return result


if __name__ == "__main__":
    # 테스트 예제
    test_address = "서울특별시 성동구 왕십리로 222"
    
    result = analyze_area_by_address(
        address=test_address,
        buffer_meters=300,
        max_images=10  # 테스트용으로 10개만
    )
    
    print(f"\n\n결과 폴더: {result['output_folder']}")
    
    # 지도 자동 열기
    import webbrowser
    map_path = f"{result['output_folder']}/analysis_map.html"
    webbrowser.open(map_path)
