"""
Store ORM 모델
"""
from sqlalchemy import Column, String, Float, Integer, DateTime
from backend.core.database import Base


class Store(Base):
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, index=True)
    store_code = Column(String, unique=True, index=True, nullable=False)
    store_name = Column(String, nullable=False)
    category = Column(String)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

