"""
수치/텍스트 포맷팅
"""
from typing import Union


def format_number(value: Union[int, float], decimals: int = 2) -> str:
    """숫자 포맷팅"""
    return f"{value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """퍼센트 포맷팅"""
    return f"{value:.{decimals}f}%"


def format_currency(value: Union[int, float], currency: str = "₩") -> str:
    """통화 포맷팅"""
    return f"{currency}{value:,.0f}"


def format_grade(grade: str) -> str:
    """등급 포맷팅 (색상 추가)"""
    colors = {
        "A+": "🟢",
        "A": "🟢",
        "B+": "🔵",
        "B": "🔵",
        "C+": "🟡",
        "C": "🟡",
        "D": "🟠",
        "F": "🔴"
    }
    
    icon = colors.get(grade, "⚪")
    return f"{icon} {grade}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """텍스트 자르기"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def format_list(items: list, separator: str = ", ") -> str:
    """리스트를 문자열로 포맷팅"""
    return separator.join(str(item) for item in items)

