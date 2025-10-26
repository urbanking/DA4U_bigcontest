"""
Crawler Output Manager - 크롤링 결과 저장 및 로드
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


class CrawlerOutputManager:
    """네이버 데이터랩 크롤링 결과 저장/로드 관리"""
    
    def __init__(self, output_dir: str = "open_sdk/output"):
        """
        Args:
            output_dir: 크롤링 결과 저장 디렉토리 (기본: open_sdk/output)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_keywords(
        self, 
        keywords: List[Dict[str, Any]], 
        store_code: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        크롤링 키워드 저장 (open_sdk/output/naver_datalab_{timestamp}/ 하위)
        
        Args:
            keywords: 크롤링된 키워드 리스트
            store_code: 매장 코드
            metadata: 추가 메타데이터 (업종, 타깃 정보 등)
            
        Returns:
            저장된 파일 경로
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # open_sdk/output/naver_datalab_{timestamp}/ 폴더 생성
        session_dir = self.output_dir / f"naver_datalab_{timestamp}"
        session_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{store_code}_keywords.json"
        filepath = session_dir / filename
        
        data = {
            "store_code": store_code,
            "crawled_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "keywords": keywords,
            "total_count": len(keywords)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] 크롤링 결과 저장: {filepath}")
        return str(filepath)
    
    def load_keywords(self, filepath: str) -> Dict[str, Any]:
        """
        저장된 키워드 로드
        
        Args:
            filepath: JSON 파일 경로
            
        Returns:
            저장된 데이터 전체
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def get_latest_keywords(self, store_code: str) -> Optional[Dict[str, Any]]:
        """
        특정 매장의 가장 최근 크롤링 결과 로드
        
        Args:
            store_code: 매장 코드
            
        Returns:
            최신 크롤링 데이터 또는 None
        """
        # naver_datalab_* 폴더들을 순회
        session_dirs = sorted(self.output_dir.glob("naver_datalab_*"), reverse=True)
        
        for session_dir in session_dirs:
            keyword_file = session_dir / f"{store_code}_keywords.json"
            if keyword_file.exists():
                return self.load_keywords(str(keyword_file))
        
        return None
    
    def save_final_result(
        self,
        result: Dict[str, Any],
        store_code: str,
        session_timestamp: Optional[str] = None
    ) -> str:
        """
        NewProductAgent 최종 결과 저장 (같은 세션 폴더에 저장)
        
        Args:
            result: Agent 최종 응답
            store_code: 매장 코드
            session_timestamp: 크롤링 세션 타임스탬프 (None이면 현재 시각)
            
        Returns:
            저장된 파일 경로
        """
        timestamp = session_timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 같은 세션 폴더에 저장
        session_dir = self.output_dir / f"naver_datalab_{timestamp}"
        session_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{store_code}_new_product_result.json"
        filepath = session_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] 최종 결과 저장: {filepath}")
        return str(filepath)
