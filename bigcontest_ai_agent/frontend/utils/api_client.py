"""
FastAPI 호출
"""
import requests
from typing import Dict, Any, Optional


class APIClient:
    """API 클라이언트"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def _get(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """GET 요청"""
        try:
            response = requests.get(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error: {e}")
            return None
    
    def _post(self, endpoint: str, data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """POST 요청"""
        try:
            response = requests.post(f"{self.base_url}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error: {e}")
            return None
    
    # Store Report
    def get_store_report(self, store_code: str) -> Optional[Dict[str, Any]]:
        """가게 리포트 조회"""
        return self._get(f"/api/store/{store_code}")
    
    def generate_store_report(self, store_code: str) -> Optional[Dict[str, Any]]:
        """가게 리포트 생성"""
        return self._post(f"/api/store/{store_code}/generate")
    
    # Metrics
    def get_metrics(self, store_code: str) -> Optional[Dict[str, Any]]:
        """지표 조회"""
        return self._get(f"/api/metrics/{store_code}")
    
    def calculate_metrics(self, store_code: str) -> Optional[Dict[str, Any]]:
        """지표 계산"""
        return self._post(f"/api/metrics/{store_code}/calculate")
    
    # Diagnostic
    def get_diagnostic(self, store_code: str) -> Optional[Dict[str, Any]]:
        """진단 결과 조회"""
        return self._get(f"/api/diagnostic/{store_code}")
    
    def run_diagnostic(self, store_code: str) -> Optional[Dict[str, Any]]:
        """진단 실행"""
        return self._post(f"/api/diagnostic/{store_code}/diagnose")
    
    # Marketing
    def get_marketing_strategy(self, store_code: str) -> Optional[Dict[str, Any]]:
        """마케팅 전략 조회"""
        return self._get(f"/api/marketing/{store_code}")
    
    def generate_marketing_strategy(self, store_code: str) -> Optional[Dict[str, Any]]:
        """마케팅 전략 생성"""
        return self._post(f"/api/marketing/{store_code}/generate")
    
    # Orchestrator
    def run_full_pipeline(self, store_code: str) -> Optional[Dict[str, Any]]:
        """전체 파이프라인 실행"""
        return self._post(f"/api/run/{store_code}")
    
    def get_pipeline_status(self, store_code: str) -> Optional[Dict[str, Any]]:
        """파이프라인 상태 조회"""
        return self._get(f"/api/run/{store_code}/status")

