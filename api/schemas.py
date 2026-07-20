from typing import Dict, List
from pydantic import BaseModel,Field


class PredictionRequest(BaseModel):
    student_id: int
    job_id: int


class PredictionResponse(BaseModel):
    student_name: str
    company: str
    role: str
    match_score: float
    status: str
    threshold_validation: dict[str, bool]
    reasons: dict


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

class JobCreate(BaseModel):
    job_id: int
    title: str
    skills: List[str]
    company: str

    Python_Threshold: int
    SQL_Threshold: int
    ML_Threshold: int
    Communication_Threshold: int
    Experience_Threshold: int
    Minimum_CGPA: float



class ApplicationCreate(BaseModel):
    student_id: int
    job_id: int