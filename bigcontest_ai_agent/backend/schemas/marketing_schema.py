"""
Marketing Pydantic 스키마
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class MarketingStrategy(BaseModel):
    strategy_name: str
    description: str
    target_segments: List[str]
    expected_impact: Dict[str, Any]


class MarketingResponse(BaseModel):
    store_code: str
    strategy: Dict[str, Any]
    strategies: List[MarketingStrategy]
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

