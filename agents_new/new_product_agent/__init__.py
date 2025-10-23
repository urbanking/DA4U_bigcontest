"""
신제품 제안 Agent
- StoreAgent 리포트 기반으로 네이버 데이터랩 키워드 크롤링
- Gemini 2.5 Flash를 활용한 템플릿 제안문 생성
"""
from .new_product_agent import NewProductAgent

__all__ = ["NewProductAgent"]
