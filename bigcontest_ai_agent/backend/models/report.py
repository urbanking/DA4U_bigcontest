"""
Report ORM 모델
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text
from backend.core.database import Base


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    store_code = Column(String, index=True, nullable=False)
    report_type = Column(String)  # 'store', 'marketing', etc.
    report_data = Column(JSON)
    summary = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

