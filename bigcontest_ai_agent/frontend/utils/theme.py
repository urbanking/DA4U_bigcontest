"""
UI 스타일 관리
"""

# 색상 팔레트
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "warning": "#ffbb00",
    "danger": "#d62728",
    "info": "#17a2b8",
    "light": "#f8f9fa",
    "dark": "#343a40"
}

# 등급 색상
GRADE_COLORS = {
    "A+": "#2ca02c",
    "A": "#2ca02c",
    "B+": "#1f77b4",
    "B": "#1f77b4",
    "C+": "#ffbb00",
    "C": "#ffbb00",
    "D": "#ff7f0e",
    "F": "#d62728"
}

# 심각도 색상
SEVERITY_COLORS = {
    "critical": "#d62728",
    "warning": "#ff7f0e",
    "info": "#1f77b4",
    "success": "#2ca02c"
}


def get_color(key: str, default: str = "#000000") -> str:
    """색상 가져오기"""
    return COLORS.get(key, default)


def get_grade_color(grade: str) -> str:
    """등급 색상 가져오기"""
    return GRADE_COLORS.get(grade, COLORS["light"])


def get_severity_color(severity: str) -> str:
    """심각도 색상 가져오기"""
    return SEVERITY_COLORS.get(severity, COLORS["info"])

