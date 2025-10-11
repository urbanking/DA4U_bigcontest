"""
Plotly/Altair 그래프
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List


def create_gauge_chart(value: float, title: str, max_value: float = 100):
    """게이지 차트 생성"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [None, max_value]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, max_value * 0.6], 'color': "lightgray"},
                {'range': [max_value * 0.6, max_value * 0.8], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    return fig


def create_radar_chart(categories: List[str], values: List[float], title: str):
    """레이더 차트 생성"""
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        title=title
    )
    
    return fig


def create_bar_chart(data: Dict[str, float], title: str, x_label: str, y_label: str):
    """막대 차트 생성"""
    df = pd.DataFrame(list(data.items()), columns=[x_label, y_label])
    
    fig = px.bar(
        df,
        x=x_label,
        y=y_label,
        title=title
    )
    
    return fig


def create_line_chart(data: pd.DataFrame, x_col: str, y_col: str, title: str):
    """라인 차트 생성"""
    fig = px.line(
        data,
        x=x_col,
        y=y_col,
        title=title
    )
    
    return fig

