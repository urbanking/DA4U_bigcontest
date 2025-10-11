"""
표 컴포넌트
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any


def create_data_table(data: List[Dict[str, Any]], columns: List[str] = None):
    """데이터 테이블 생성"""
    df = pd.DataFrame(data)
    
    if columns:
        df = df[columns]
    
    st.dataframe(df, use_container_width=True)
    return df


def create_metrics_table(metrics: Dict[str, Dict[str, Any]]):
    """지표 테이블 생성"""
    data = []
    for metric_name, metric_data in metrics.items():
        data.append({
            "지표": metric_name.upper(),
            "값": metric_data.get("value", 0),
            "점수": metric_data.get("score", 0),
            "등급": metric_data.get("grade", "N/A")
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    return df


def create_recommendations_table(recommendations: List[Dict[str, Any]]):
    """권고사항 테이블 생성"""
    data = []
    for rec in recommendations:
        data.append({
            "권고사항": rec.get("recommendation", ""),
            "우선순위": rec.get("priority", "medium"),
            "예상 효과": rec.get("impact", "medium")
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    return df

