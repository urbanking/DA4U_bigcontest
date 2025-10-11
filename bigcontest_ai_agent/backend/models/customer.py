"""
Customer ORM 모델
"""
from sqlalchemy import Column, String, Integer, DateTime, Float
from backend.core.database import Base


class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True, nullable=False)
    age_group = Column(String)
    gender = Column(String)
    region = Column(String)
    total_purchases = Column(Integer)
    total_amount = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

