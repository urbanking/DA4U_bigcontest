"""
Metrics ORM 모델
"""
from sqlalchemy import Column, String, Integer, DateTime, Float, JSON
from backend.core.database import Base


class Metrics(Base):
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    store_code = Column(String, index=True, nullable=False)
    metric_name = Column(String)
    metric_value = Column(Float)
    metric_score = Column(Float)
    metric_grade = Column(String)
    metadata = Column(JSON)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

