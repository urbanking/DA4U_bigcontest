"""
리포트 생성기
comprehensive_analysis.json을 기반으로 MD 리포트를 생성합니다.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional

def generate_md_report(json_data: Dict[str, Any], store_code: str) -> str:
    """
    JSON 분석 데이터를 기반으로 MD 리포트를 생성합니다.
    
    Args:
        json_data: comprehensive_analysis.json 데이터
        store_code: 상점 코드
        
    Returns:
        생성된 MD 리포트 문자열
    """
    try:
        # 메타데이터 추출
        metadata = json_data.get("metadata", {})
        spatial_analysis = json_data.get("spatial_analysis", {})
        store_summary = json_data.get("store_summary", {})
        marketing_summary = json_data.get("marketing_summary", {})
        panorama_summary = json_data.get("panorama_summary", {})
        marketplace_summary = json_data.get("marketplace_summary", {})
        mobility_summary = json_data.get("mobility_summary", {})
        
        # MD 리포트 생성
        md_content = f"""# 매장 분석 리포트

## 📋 기본 정보
- **상점 코드**: {store_code}
- **분석 일시**: {metadata.get('analysis_timestamp', 'N/A')}
- **분석 유형**: {metadata.get('analysis_type', 'comprehensive_analysis')}

---

## 🗺️ 위치 분석
- **주소**: {spatial_analysis.get('address', 'N/A')}
- **좌표**: {spatial_analysis.get('coordinates', 'N/A')}
- **행정동**: {spatial_analysis.get('administrative_dong', 'N/A')}
- **상권**: {spatial_analysis.get('marketplace', {}).get('상권명', 'N/A') if spatial_analysis.get('marketplace') else 'N/A'}

---

## 🏪 매장 개요
- **매장명**: {store_summary.get('store_name', 'N/A')}
- **업종**: {store_summary.get('industry', 'N/A')}
- **상권**: {store_summary.get('commercial_area', 'N/A')}
- **품질 점수**: {store_summary.get('quality_score', 'N/A')}

---

## 📈 마케팅 분석
- **페르소나 유형**: {marketing_summary.get('persona_type', 'N/A')}
- **위험 수준**: {marketing_summary.get('risk_level', 'N/A')}
- **전략 수**: {marketing_summary.get('strategy_count', 0)}개
- **캠페인 수**: {marketing_summary.get('campaign_count', 0)}개

---

## 🌆 파노라마 분석
- **지역 특성**: {panorama_summary.get('area_characteristics', 'N/A')}
- **상권 유형**: {panorama_summary.get('marketplace_type', 'N/A')}
- **종합 점수**: {panorama_summary.get('scores', 'N/A')}

### 강점
{_format_list(panorama_summary.get('strengths', []))}

### 약점
{_format_list(panorama_summary.get('weaknesses', []))}

### 추천 업종
{_format_list(panorama_summary.get('recommended_industries', []))}

### 전문가 의견
{panorama_summary.get('expert_opinion', 'N/A')}

---

## 🏬 상권 분석
- **상권명**: {marketplace_summary.get('marketplace_name', 'N/A')}
- **점포 수**: {marketplace_summary.get('store_count', 'N/A')}개
- **매출액**: {marketplace_summary.get('sales_volume', 'N/A')}

---

## 🚶 이동 분석
- **분석 기간**: {mobility_summary.get('analysis_period', 'N/A')}
- **생성된 차트**: {mobility_summary.get('total_charts', 0)}개

---

## 📊 종합 평가

이 리포트는 5차원 분석(Store, Marketing, Mobility, Panorama, Marketplace)을 통해 생성되었습니다.
각 분석 결과를 종합하여 매장의 현재 상황과 개선 방안을 제시합니다.

### 주요 인사이트
1. **위치 분석**: 행정동 및 상권 정보를 통한 입지 평가
2. **매장 분석**: 매장 운영 현황 및 품질 평가
3. **마케팅 분석**: 고객 페르소나 및 마케팅 전략 제안
4. **환경 분석**: 주변 상권 및 이동 패턴 분석
5. **경쟁 분석**: 상권 내 경쟁 상황 및 기회 요소

### 추천 사항
- 위 분석 결과를 바탕으로 구체적인 개선 방안을 수립하세요
- 정기적인 분석을 통해 매장 성과를 모니터링하세요
- 마케팅 전략을 실행하고 효과를 측정하세요

---
*이 리포트는 AI 분석 시스템에 의해 자동 생성되었습니다.*
"""
        
        return md_content
        
    except Exception as e:
        print(f"[ERROR] MD 리포트 생성 실패: {e}")
        return f"# 매장 분석 리포트\n\n오류가 발생했습니다: {str(e)}"

def save_md_report(md_content: str, store_code: str, output_dir: Path) -> str:
    """
    MD 리포트를 파일로 저장합니다.
    
    Args:
        md_content: MD 내용
        store_code: 상점 코드
        output_dir: 출력 디렉토리
        
    Returns:
        저장된 파일 경로
    """
    try:
        # 리포트 디렉토리 생성
        report_dir = output_dir / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # 파일명 생성
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_report_{store_code}_{timestamp}.md"
        file_path = report_dir / filename
        
        # 파일 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"[OK] MD 리포트 저장: {file_path}")
        return str(file_path)
        
    except Exception as e:
        print(f"[ERROR] MD 리포트 저장 실패: {e}")
        return None

def load_comprehensive_analysis(file_path: str) -> Optional[Dict[str, Any]]:
    """
    comprehensive_analysis.json 파일을 로드합니다.
    
    Args:
        file_path: JSON 파일 경로
        
    Returns:
        로드된 JSON 데이터 또는 None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"[ERROR] JSON 파일 로드 실패: {e}")
        return None

def _format_list(items: list) -> str:
    """리스트를 MD 형식으로 포맷팅합니다."""
    if not items:
        return "N/A"
    
    if isinstance(items, list):
        return "\n".join([f"- {item}" for item in items])
    else:
        return str(items)
