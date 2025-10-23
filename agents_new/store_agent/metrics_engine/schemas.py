"""
지표 정의, 가중치 구조
"""
from pydantic import BaseModel
from typing import Dict, List, Optional


class MetricDefinition(BaseModel):
    """지표 정의"""
    name: str
    description: str
    unit: str
    weight: float
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class MetricWeights(BaseModel):
    """지표 가중치"""
    cvi: float = 0.25  # Commercial Viability Index
    asi: float = 0.25  # Accessibility Score Index
    sci: float = 0.25  # Store Competitiveness Index
    gmi: float = 0.25  # Growth & Market Index


# 지표 정의 예시
METRIC_DEFINITIONS = {
    "cvi": MetricDefinition(
        name="CVI",
        description="Commercial Viability Index - 상권 활성도 지수",
        unit="score",
        weight=0.25,
        min_value=0,
        max_value=100
    ),
    "asi": MetricDefinition(
        name="ASI",
        description="Accessibility Score Index - 접근성 지수",
        unit="score",
        weight=0.25,
        min_value=0,
        max_value=100
    ),
    "sci": MetricDefinition(
        name="SCI",
        description="Store Competitiveness Index - 점포 경쟁력 지수",
        unit="score",
        weight=0.25,
        min_value=0,
        max_value=100
    ),
    "gmi": MetricDefinition(
        name="GMI",
        description="Growth & Market Index - 성장 및 시장 지수",
        unit="score",
        weight=0.25,
        min_value=0,
        max_value=100
    )
}

