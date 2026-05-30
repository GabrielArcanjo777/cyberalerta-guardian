from pydantic import BaseModel
from typing import Optional
from app.schemas.analysis import AnalysisResponse, ReportModel


class ReportRequest(BaseModel):
    analysis: Optional[AnalysisResponse] = None


class ReportResponse(BaseModel):
    report: ReportModel
