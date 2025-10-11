"""
Store Pydantic 스키마
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class StoreBase(BaseModel):
    store_code: str
    store_name: str
    category: Optional[str] = None
    address: Optional[str] = None


class StoreReportResponse(BaseModel):
    store_code: str
    report: Dict[str, Any]
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

