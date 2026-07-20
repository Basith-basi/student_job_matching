from fastapi import APIRouter, HTTPException
import pandas as pd

from api.database import get_connection
from api.schemas import JobCreate, ApplicationCreate

from src.matching import JobMatcher
from src.threshold_validation import ThresholdValidator
from src.explainability import Explainability
from src.ranking import JobRanker
from src.evaluation import Evaluator

router = APIRouter()

matcher = JobMatcher()
validator = ThresholdValidator()
explainer = Explainability()
ranker = JobRanker()
evaluator = Evaluator()

STUDENTS_CSV = "data/students.csv"
JOBS_CSV = "data/jobs.csv"


# --------------------------------------------------
# POST /jobs
# --------------------------------------------------
@router.post("/jobs")
def create_job(job: JobCreate):
    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------------
    # Validate CGPA
    # -----------------------------
    if job.Minimum_CGPA < 0 or job.Minimum_CGPA > 10:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid CGPA")

    # -----------------------------
    # Validate Python Threshold
    # -----------------------------
    if job.Python_Threshold < 0 or job.Python_Threshold > 100:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid Python Threshold")

    # -----------------------------
    # Validate SQL Threshold
    # -----------------------------
    if job.SQL_Threshold < 0 or job.SQL_Threshold > 100:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid SQL Threshold")

    # -----------------------------
    # Validate ML Threshold
    # -----------------------------
    if job.ML_Threshold < 0 or job.ML_Threshold > 100:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid ML Threshold")

    # -----------------------------
    # Validate Communication Threshold
    # -----------------------------
    if job.Communication_Threshold < 0 or job.Communication_Threshold > 100:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid Communication Threshold")

    # -----------------------------
    # Validate Experience Threshold
    # -----------------------------
    if job.Experience_Threshold < 0:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid Experience Threshold")

    # -----------------------------
    # Validate Skills
    # -----------------------------
    if (
        len(job.skills) == 0
        or all(skill.strip() == "" for skill in job.skills)
    ):
        conn.close()
        raise HTTPException(status_code=400, detail="Skills cannot be empty")

    cursor.execute("SELECT * FROM jobs WHERE job_id=?", (job.job_id,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Job ID already exists")

    cursor.execute(
        """
        INSERT INTO jobs (
            job_id, title, company, skills,
            Python_Threshold, SQL_Threshold, ML_Threshold,
            Communication_Threshold, Experience_Threshold, Minimum_CGPA
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            job.job_id,
            job.title,
            job.company,
            ",".join(job.skills),
            job.Python_Threshold,
            job.SQL_Threshold,
            job.ML_Threshold,
            job.Communication_Threshold,
            job.Experience_Threshold,
            job.Minimum_CGPA,
        ),
    )
    conn.commit()
    conn.close()

    return {"message": "Job created successfully", "job_id": job.job_id}


# --------------------------------------------------
# GET /jobs
# --------------------------------------------------
@router.get("/jobs")
def get_jobs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()
    conn.close()
    return [dict(job) for job in jobs]


# --------------------------------------------------
# GET /jobs/{job_id}
# --------------------------------------------------
@router.get("/jobs/{job_id}")
def get_job(job_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,))
    job = cursor.fetchone()
    conn.close()

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    data = dict(job)
    data["skills"] = data["skills"].split(",")
    return data


# --------------------------------------------------
# GET /rankings/{job_id}
# --------------------------------------------------
@router.get("/rankings/{job_id}")
def get_rankings(job_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,))
    job = cursor.fetchone()
    conn.close()

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    students = pd.read_csv(STUDENTS_CSV)
    job_series = pd.Series(dict(job))

    ranking = ranker.rank_students(students, job_series)
    return ranking.to_dict(orient="records")


# --------------------------------------------------
# POST /applications
# --------------------------------------------------
@router.post("/applications")
def apply_job(application: ApplicationCreate):
    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------------------
    # Verify student exists
    # --------------------------------------------------
    students = pd.read_csv(STUDENTS_CSV)
    student_rows = students[students["Student_ID"] == application.student_id]

    if student_rows.empty:
        conn.close()
        raise HTTPException(status_code=404, detail="Student not found")

    student = student_rows.iloc[0]

    # --------------------------------------------------
    # Verify job exists
    # --------------------------------------------------
    cursor.execute("SELECT * FROM jobs WHERE job_id=?", (application.job_id,))
    job = cursor.fetchone()

    if job is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found")

    job_series = pd.Series(dict(job))

    # --------------------------------------------------
    # Prevent duplicate application
    # --------------------------------------------------
    cursor.execute(
        "SELECT * FROM applications WHERE student_id=? AND job_id=?",
        (application.student_id, application.job_id),
    )
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Already applied")

    # --------------------------------------------------
    # Score, validate, explain (the "why" the study guide requires)
    # --------------------------------------------------
    student = students[
    students["Student_ID"] == application.student_id
]

    job_series = pd.Series(dict(job))

    match_score, explanation = matcher.calculate_match_score(
     student,
     job_series
)
    threshold_result = validator.validate(student, job_series)
    explanation = explainer.generate_explanation(student, job_series)

    if match_score >= 90:
        recommendation = "Excellent Match"
    elif match_score >= 75:
        recommendation = "Strong Match"
    elif match_score >= 60:
        recommendation = "Potential Match"
    else:
        recommendation = "Low Match"

    status = "Eligible" if threshold_result["passed"] else "Not Eligible"

    # --------------------------------------------------
    # Save application
    # --------------------------------------------------
    cursor.execute(
        "INSERT INTO applications (student_id, job_id, score, status) VALUES (?, ?, ?, ?)",
        (application.student_id, application.job_id, match_score, status),
    )

    # --------------------------------------------------
    # Save prediction / audit trail
    # --------------------------------------------------
    cursor.execute(
        """
        INSERT INTO predictions
        (student_id, job_id, match_score, recommendation, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            application.student_id,
            application.job_id,
            match_score,
            recommendation,
            status,
        ),
    )

    conn.commit()
    conn.close()

    return {
        "message": "Application submitted successfully",
        "student_id": application.student_id,
        "job_id": application.job_id,
        "match_score": match_score,
        "recommendation": recommendation,
        "status": status,
        "reason": explanation,
    }


# --------------------------------------------------
# GET /applications
# --------------------------------------------------
@router.get("/applications")
def get_applications():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications")
    applications = cursor.fetchall()
    conn.close()
    return [dict(row) for row in applications]


# --------------------------------------------------
# GET /metrics  — precision / recall / false-positive rate on real data
# --------------------------------------------------
@router.get("/metrics")
def metrics():
    students = pd.read_csv(STUDENTS_CSV)
    jobs = pd.read_csv(JOBS_CSV)
    return evaluator.evaluate(students, jobs)


# --------------------------------------------------
# HEALTH
# --------------------------------------------------
@router.get("/health")
def health():
    return {"status": "Healthy"}