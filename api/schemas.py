from typing import Dict, List
from pydantic import BaseModel


class PredictionRequest(BaseModel):
    student_id: int
    job_id: int


class PredictionResponse(BaseModel):
    student_name: str
    company: str
    role: str
    match_score: float
    status: str
    threshold_validation: Dict[str, bool]
    reasons: List[str]