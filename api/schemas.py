from typing import Any, Dict, List
from pydantic import AliasChoices, BaseModel, Field, field_validator, model_validator


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
    company: str = ""
    role: str = ""
    skills: List[str] = []
    python_threshold: int = 50
    sql_threshold: int = 50
    ml_threshold: int = 50
    communication_threshold: int = 50
    experience_threshold: int = 0
    minimum_cgpa: float = 7.0
    job_id: int = 0

    @field_validator("skills", mode="before")
    @classmethod
    def parse_skills(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    @model_validator(mode="before")
    @classmethod
    def convert_old_format(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        old_to_new = {
            "title": "role",
            "Python_Threshold": "python_threshold",
            "SQL_Threshold": "sql_threshold",
            "ML_Threshold": "ml_threshold",
            "Communication_Threshold": "communication_threshold",
            "Experience_Threshold": "experience_threshold",
            "Minimum_CGPA": "minimum_cgpa",
        }
        for old, new in old_to_new.items():
            if old in data and new not in data:
                data[new] = data.pop(old)
        return data


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
    student: str = ""
    student_id: int = 0
    job_id: int = Field(..., gt=0, description="Job ID")

    @model_validator(mode="before")
    @classmethod
    def convert_old_format(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        if "student_name" in data and "student" not in data:
            data["student"] = data.pop("student_name")
        return data


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
