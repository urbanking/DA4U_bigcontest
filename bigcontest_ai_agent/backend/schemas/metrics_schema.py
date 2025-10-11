"""
Metrics Pydantic 스키마
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class MetricBase(BaseModel):
    metric_name: str
    metric_value: float
    metric_score: Optional[float] = None
    metric_grade: Optional[str] = None


class MetricsResponse(BaseModel):
    store_code: str
    metrics: Dict[str, Any]
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

