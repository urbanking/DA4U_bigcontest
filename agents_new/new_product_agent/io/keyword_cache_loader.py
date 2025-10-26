"""
Keyword Cache Loader - JSON 파일에서 크롤링 데이터 로드

Streamlit 배포시 사전 크롤링한 데이터를 재사용
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

# 현재 디렉토리 기준 경로
BASE_DIR = Path(__file__).parent.parent


class KeywordCacheLoader:
    """JSON 캐시에서 키워드 로드"""
    
    def __init__(self, json_path: Optional[str] = None):
        """
        Args:
            json_path: JSON 파일 경로 (None이면 현재 디렉토리에서 keywords_20251026.json 찾음)
        """
        if json_path is None:
            # 현재 디렉토리 또는 BASE_DIR에서 찾기
            possible_paths = [
                Path("keywords_20251026.json"),
                BASE_DIR / "keywords_20251026.json"
            ]
            for path in possible_paths:
                if path.exists():
                    self.json_path = path
                    break
            else:
                self.json_path = Path("keywords_20251026.json")
        else:
            self.json_path = Path(json_path)
        
        self.cache: Dict[str, Any] = {}
        
        if self.json_path.exists():
            self._load_cache()
    
    def _load_cache(self):
        """JSON 파일 로드"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.cache = json.load(f)
            print(f"[OK] 키워드 캐시 로드: {self.json_path}")
        except Exception as e:
            print(f"[ERROR] 캐시 로드 실패: {e}")
    
    def get_keywords(
        self, 
        gender: str, 
        ages: List[str], 
        categories: List[str]
    ) -> List[Dict[str, Any]]:
        """
        키워드 조회
        
        Args:
            gender: 성별 ("남성", "여성", "전체")
            ages: 연령 리스트 (["10대"], ["10대", "20대"], 등)
            categories: 카테고리 리스트 (["농산물", "음료", "과자/베이커리"])
        
        Returns:
            키워드 리스트 [{"rank": 1, "keyword": "..."}, ...]
        """
        if not self.cache:
            print("[WARN] 캐시가 비어있음")
            return []
        
        # 연령 문자열로 변환 (JSON의 키 형식)
        ages_str = ", ".join(ages)
        
        # 캐시에서 조회
        if gender not in self.cache:
            print(f"[WARN] 성별 '{gender}' 없음")
            return []
        
        if ages_str not in self.cache[gender]:
            print(f"[WARN] 연령 '{ages_str}' 없음")
            return []
        
        # 키워드 수집
        keywords = []
        for category in categories:
            if category in self.cache[gender][ages_str]:
                for kw in self.cache[gender][ages_str][category]:
                    keywords.append({
                        "category": category,
                        "rank": kw["rank"],
                        "keyword": kw["keyword"]
                    })
        
        # rank로 정렬
        keywords.sort(key=lambda x: x["rank"])
        
        return keywords

