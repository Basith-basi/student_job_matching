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


class JobRankingItem(BaseModel):
    Rank: int
    Company: str
    Role: str
    Score: float
    Status: str


class MetricsResponse(BaseModel):
    n_train: int
    n_test: int
    model_precision: float
    model_recall: float
    model_f1: float
    model_fpr: float
    baseline_precision: float
    baseline_recall: float
    baseline_f1: float
    baseline_fpr: float