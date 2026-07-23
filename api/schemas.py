from typing import Dict, List
from pydantic import BaseModel,Field


# ==========================================================
# Prediction
# ==========================================================



class PredictionResponse(BaseModel):
    student_name: str
    company: str
    role: str
    match_score: float
    status: str
    threshold_validation: Dict[str, bool]
    reasons: Dict


# ==========================================================
# Ranking
# ==========================================================

class JobRankingItem(BaseModel):
    rank: int
    company: str
    role: str
    score: float
    status: str


# ==========================================================
# Metrics
# ==========================================================

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


# ==========================================================
# Company creates a Job
# POST /jobs
# ==========================================================

class JobCreate(BaseModel):
    company: str
    role: str
    skills: List[str]
    python_threshold: int
    sql_threshold: int
    ml_threshold: int
    communication_threshold: int
    experience_threshold: int
    minimum_cgpa: float


class JobResponse(BaseModel):
    message: str
    job_id: int
    company: str
    role: str


# ==========================================================
# Student applies for a Job
# POST /applications
# ==========================================================

class ApplicationCreate(BaseModel):
    student: str = Field(
        ...,
        min_length=1,
        description="Student name"
    )
    job_id: int = Field(
        ...,
        gt=0,
        description="Job ID"
    )


class ApplicationResponse(BaseModel):
    message: str
    student_id: int
    job_id: int


# ==========================================================
# Match Result
# ==========================================================

class MatchResponse(BaseModel):
    student: str
    company: str
    role: str

    score: float
    status: str
    recommendation: str


# ==========================================================
# Health Check
# ==========================================================

class HealthResponse(BaseModel):
    status: str

class PaymentRequest(BaseModel):
    student_name: str
    company: str
    job_id: int
    plan: str
   

class PaymentResponse(BaseModel):
    success: bool
    student: str
    company: str
    job_id: int
    plan: str
    amount: float
    status: str
    transaction_id: str


class VerifyPaymentRequest(BaseModel):
    transaction_id: str


class PredictionRequest(BaseModel):
    student_id: int
    job_id: int
