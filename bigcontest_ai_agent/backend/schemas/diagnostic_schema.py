"""
Diagnostic Pydantic 스키마
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class DiagnosticIssue(BaseModel):
    issue_type: str
    severity: str
    description: str
    recommendations: List[str]


class DiagnosticResponse(BaseModel):
    store_code: str
    diagnostic: Dict[str, Any]
    issues: List[DiagnosticIssue]
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

