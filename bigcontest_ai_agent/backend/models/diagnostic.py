"""
Diagnostic ORM 모델
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from backend.core.database import Base


class Diagnostic(Base):
    __tablename__ = "diagnostics"
    
    id = Column(Integer, primary_key=True, index=True)
    store_code = Column(String, index=True, nullable=False)
    issue_type = Column(String)
    severity = Column(String)  # 'critical', 'warning', 'info'
    description = Column(Text)
    recommendations = Column(JSON)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

