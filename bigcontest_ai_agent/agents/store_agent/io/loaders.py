"""
DB/API 데이터 로드
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session


class DataLoader:
    """데이터 로더"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
    
    async def load_store_data(self, store_code: str) -> Dict[str, Any]:
        """가게 데이터 로드"""
        # TODO: DB에서 가게 데이터 로드
        return {"store_code": store_code, "data": {}}
    
    async def load_commercial_data(self, store_code: str) -> Dict[str, Any]:
        """상권 데이터 로드"""
        # TODO: DB/API에서 상권 데이터 로드
        return {}
    
    async def load_customer_data(self, store_code: str) -> Dict[str, Any]:
        """고객 데이터 로드"""
        # TODO: DB에서 고객 데이터 로드
        return {}

