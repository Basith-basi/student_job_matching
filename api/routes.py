from email.mime import application

from fastapi import APIRouter, HTTPException,status
import sqlite3
import pandas as pd

from api.database import get_connection
from api.schemas import JobCreate, ApplicationCreate

from src.matching import JobMatcher
from src.threshold_validation import ThresholdValidator
from src.explainability import Explainability
from src.ranking import JobRanker
from src.evaluation import Evaluator
from src.data_loader import DataLoader
from src.preprocessing import DataPreprocessor
from src.feature_engineering import FeatureEngineer
from payments.payment_service import PaymentService

from api.schemas import (
    PaymentRequest,
    PaymentResponse,
    VerifyPaymentRequest
)


router = APIRouter()
payment_service = PaymentService()
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
@router.post("/jobs", status_code=201)
def create_job(job: JobCreate):

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------------------
    # COMPANY PREMIUM SUBSCRIPTION CHECK (Task 6)
    # --------------------------------------------------
    cursor.execute(
        """
        SELECT *
        FROM payments
        WHERE company = ?
        AND payment_status = 'SUCCESS'
        """,
        (job.company,)
    )

    subscription = cursor.fetchone()

    if subscription is None:
        conn.close()
        raise HTTPException(
            status_code=403,
            detail="Company Premium Subscription Required"
        )

    # --------------------------------------------------
    # VALIDATE THRESHOLDS
    # --------------------------------------------------
    if not (0 <= job.python_threshold <= 100):
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Invalid Python Threshold"
        )

    if not (0 <= job.sql_threshold <= 100):
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Invalid SQL Threshold"
        )

    if not (0 <= job.ml_threshold <= 100):
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Invalid ML Threshold"
        )

    if not (0 <= job.communication_threshold <= 100):
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Invalid Communication Threshold"
        )

    if job.experience_threshold < 0:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Invalid Experience Threshold"
        )

    if not (0 <= job.minimum_cgpa <= 10):
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Invalid Minimum CGPA"
        )

    # --------------------------------------------------
    # GENERATE NEXT JOB ID
    # --------------------------------------------------
    cursor.execute("SELECT MAX(job_id) FROM jobs")

    row = cursor.fetchone()

    if row[0] is None:
        job_id = 1
    else:
        job_id = row[0] + 1

    # --------------------------------------------------
    # INSERT JOB
    # --------------------------------------------------
    cursor.execute("""
INSERT INTO jobs (
    job_id,
    company,
    role,
    skills,
    Python_Threshold,
    SQL_Threshold,
    ML_Threshold,
    Communication_Threshold,
    Experience_Threshold,
    Minimum_CGPA
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""",
(
    job_id,
    job.company,
    job.role,
    ",".join(job.skills),
    job.python_threshold,
    job.sql_threshold,
    job.ml_threshold,
    job.communication_threshold,
    job.experience_threshold,
    job.minimum_cgpa
))

    conn.commit()
    conn.close()

    return {
        "message": "Job Created Successfully",
        "job_id": job_id,
        "company": job.company,
        "role": job.role,
        "status": "Premium Verified"
    }
# --------------------------------------------------
# GET /jobs
# --------------------------------------------------
@router.get("/jobs")
def get_jobs():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            job_id,
            company,
            title,
            skills,
            min_cgpa,
            min_experience
        FROM jobs
        ORDER BY job_id
    """)

    rows = cursor.fetchall()

    conn.close()

    jobs = []

    for row in rows:
        jobs.append({
            "job_id": row["job_id"],
            "company": row["company"],
            "title": row["title"],
            "skills": row["skills"],
            "min_cgpa": row["min_cgpa"],
            "min_experience": row["min_experience"]
        })

    return {
        "total_jobs": len(jobs),
        "jobs": jobs
    }
# --------------------------------------------------
# POST /applications
# --------------------------------------------------
@router.post("/applications")
def apply_job(application: ApplicationCreate):

    # -----------------------------
    # Load Students
    # -----------------------------
    students = pd.read_csv(STUDENTS_CSV)

    student_df = students[
        students["Name"].str.lower() ==
        application.student.lower()
    ]

    if student_df.empty:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    student = student_df.iloc[0]

    # -----------------------------
    # Load Job
    # -----------------------------
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM jobs
        WHERE job_id=?
        """,
        (application.job_id,)
    )

    job = cursor.fetchone()

    if job is None:
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    job = dict(job)
    job_series = pd.Series(job)



     # -----------------------------
    # PREMIUM CHECK ← INSERT HERE
    # -----------------------------
    cursor.execute("""
        SELECT *
        FROM payments
        WHERE student_name=?
        AND payment_status='SUCCESS'
    """, (application.student,))

    payment = cursor.fetchone()

    if payment is None:
        conn.close()
        raise HTTPException(
            status_code=403,
            detail="Student Premium Subscription Required"
        )

    # -----------------------------
    # Duplicate Application Check
    # -----------------------------
    cursor.execute(
    """
    SELECT *
    FROM applications
    WHERE student_id=?
    AND job_id=?
    """,
    (
        student["Student_ID"],
        application.job_id,
    )
)

    if cursor.fetchone():

        conn.close()

        raise HTTPException(
            status_code=400,
            detail="Student already applied for this job."
        )

    # -----------------------------
    # Threshold Validation
    # -----------------------------
    validation = validator.validate(
        student,
        job_series
    )

    # -----------------------------
    # Match Score
    # -----------------------------
    score, _ = matcher.calculate_match_score(
        student,
        job_series
    )

    # -----------------------------
    # Explainability
    # -----------------------------
    explanation = explainer.explain(
        student,
        job_series,
        score
    )

    # -----------------------------
    # Recommendation
    # -----------------------------
    status = validator.overall_status(validation)
    if score >= 90:

        recommendation = "Highly Recommended"

    elif score >= 75:

        recommendation = "Recommended"

    elif score >= 60:

        recommendation = "Average Match"

    else:

        recommendation = "Low Match"

    # -----------------------------
    # Eligibility
    # -----------------------------
    status = validator.overall_status(validation)

    # -----------------------------
    # Save Application
    # -----------------------------
    cursor.execute(
    """
    INSERT INTO applications
    (student_id, job_id, score, status)
    VALUES (?, ?, ?, ?)
    """,
    (
        student["Student_ID"],
        application.job_id,
        score,
        status,
    )
)

    conn.commit()

    conn.close()

    # -----------------------------
    # Response
    # -----------------------------
    return {
    "message": "Application Submitted",
    "student": application.student,
    "company": job_series["company"],
    "score": float(score),
    "status": status,
    "recommendation": recommendation,
    "validation": {
        k: bool(v)
        for k, v in validation.items()
    },
    "explanation": explanation

}



# GET /jobs/{job_id}/candidates
# --------------------------------------------------
@router.get("/jobs/{job_id}/candidates")
def get_job_candidates(job_id: int):

    # -----------------------------
    # Load Students Dataset
    # -----------------------------
    students = pd.read_csv(STUDENTS_CSV)

    # -----------------------------
    # Get Job from Database
    # -----------------------------
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM jobs
        WHERE job_id=?
        """,
        (job_id,)
    )

    job = cursor.fetchone()

    conn.close()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # -----------------------------
    # Convert database row to Series
    # -----------------------------
    job_series = pd.Series(dict(job))

    # -----------------------------
    # Rank Students
    # -----------------------------
    ranking = ranker.rank_students(
        students,
        job_series
    )

    # -----------------------------
    # Return Top 10 Candidates
    # -----------------------------
    candidates = []

    for _, row in ranking.head(10).iterrows():

        candidates.append({

            "rank": int(row["Rank"]),

            "student": row["Student"],

            "score": float(row["Score"]),

            "status": row["Status"],

            "recommendation": row["Recommendation"]

        })

    return {

        "job_id": job_id,

        "company": job["company"],

        "role": job["role"],

        "total_candidates": len(ranking),

        "top_candidates": candidates

    }

# --------------------------------------------------
# GET /students/{student_id}/jobs
# Student Dashboard
# --------------------------------------------------
@router.get("/students/{student_id}/jobs")
def get_student_jobs(student_id: int):

    # Load datasets
    students = pd.read_csv(STUDENTS_CSV)
    jobs = pd.read_csv(JOBS_CSV)

    # Find student
    student_rows = students[students["Student_ID"] == student_id]

    if student_rows.empty:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    student = student_rows.iloc[0]

    # Rank jobs using your existing AI model
    ranked_jobs = ranker.rank_jobs_for_student(
        student,
        jobs
    )

    # Return only the required fields
    response = []

    for _, row in ranked_jobs.iterrows():

        response.append(
            {
                "company": row["Company"],
                "role": row["Role"],
                "score": round(float(row["Score"]), 2),
                "status": row["Status"],
                "recommendation": row["Recommendation"]
            }
        )

    return response
# --------------------------------------------------
# GET /metrics
# Model Evaluation Metrics
# --------------------------------------------------
@router.get("/metrics")
def get_metrics():

    # Load datasets
    students = pd.read_csv(STUDENTS_CSV)
    jobs = pd.read_csv(JOBS_CSV)

    # Evaluate model
    results = evaluator.evaluate(
        students,
        jobs,
        test_size=0.30
    )

    return {
        "precision": round(results["precision"], 3),
        "recall": round(results["recall"], 3),
        "f1": round(results["f1"], 3),
        "fpr": round(results["fpr"], 3),
        "total_pairs": results["pairs"],
        "train_pairs": results["train_pairs"],
        "test_pairs": results["test_pairs"],
        "confusion_matrix": results["confusion_matrix"]
    }
# --------------------------------------------------
# GET /health
# Health Check
# --------------------------------------------------
@router.get("/health")
def health():

    return {
        "status": "healthy",
        "message": "Student Job Matching API is running successfully",
        "version": "1.0.0"
    }

@router.post(
    "/payments",
    response_model=PaymentResponse
)
def create_payment(payment: PaymentRequest):

    result = payment_service.process_payment(
        student_name=payment.student_name,
        company=payment.company,
        job_id=payment.job_id,
        plan=payment.plan
    )

    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )

    return result

@router.get("/payments")
def get_payments():

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
    """
    INSERT INTO payments (
        student_name,
        company,
        job_id,
        plan,
        amount,
        payment_status,
        transaction_id
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (
        payment.student_name,
        payment.company,
        payment.job_id,
        payment.plan,
        payment.amount,
        status,
        transaction_id,
    ),
)

    cursor.execute("""
        SELECT *
        FROM payments
        ORDER BY payment_date DESC
    """)

    payments = cursor.fetchall()

    conn.close()

    return [dict(row) for row in payments]

@router.get("/payments/{payment_id}")
def get_payment(payment_id: int):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM payments
        WHERE payment_id=?
        """,
        (payment_id,)
    )

    payment = cursor.fetchone()

    conn.close()

    if payment is None:

        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    return dict(payment)

@router.post("/payments/verify")
def verify_payment(request: VerifyPaymentRequest):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM payments
        WHERE transaction_id=?
        """,
        (request.transaction_id,)
    )

    payment = cursor.fetchone()

    conn.close()

    if payment is None:

        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return {

        "transaction_id": request.transaction_id,

        "payment_status": payment["payment_status"],

        "verified": payment["payment_status"] == "SUCCESS"

    }

@router.get("/payments/history/{student_name}")
def payment_history(student_name: str):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM payments
        WHERE student_name=?
        ORDER BY payment_date DESC
        """,
        (student_name,)
    )

    payments = cursor.fetchall()

    conn.close()

    return [dict(row) for row in payments]

@router.get("/payments/company/{company}")
def company_payments(company: str):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM payments
        WHERE company=?
        ORDER BY payment_date DESC
        """,
        (company,)
    )

    payments = cursor.fetchall()

    conn.close()

    return [dict(row) for row in payments]

@router.get("/dashboard/student/{student}")
def student_dashboard(student: str):

    conn = get_connection()
    cursor = conn.cursor()

    # -------------------------
    # Get Student ID
    # -------------------------
    cursor.execute(
        """
        SELECT student_id
        FROM students
        WHERE student_name=?
        """,
        (student,)
    )

    student_row = cursor.fetchone()

    if student_row is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    student_id = student_row["student_id"]

    # -------------------------
    # Count Applications
    # -------------------------
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM applications
        WHERE student_id=?
        """,
        (student_id,)
    )

    applications = cursor.fetchone()[0]

    # -------------------------
    # Count Payments
    # -------------------------
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM payments
        WHERE student_name=?
        """,
        (student,)
    )

    payments = cursor.fetchone()[0]

    # -------------------------
    # Latest Successful Plan
    # -------------------------
    cursor.execute(
        """
        SELECT plan
        FROM payments
        WHERE student_name=?
        AND payment_status='SUCCESS'
        ORDER BY payment_date DESC
        LIMIT 1
        """,
        (student,)
    )

    row = cursor.fetchone()

    if row:
        plan = row["plan"]
    else:
        plan = "FREE"

    conn.close()

    return {
        "student": student,
        "current_plan": plan,
        "applications": applications,
        "payments": payments,
        "remaining": "Unlimited" if plan == "PREMIUM_STUDENT" else "Limited"
    }

@router.get("/dashboard/company/{company}")
def company_dashboard(company: str):

    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE company=?
        """,
        (company,)
    )

    jobs = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM payments
        WHERE company=?
        """,
        (company,)
    )

    payment_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT plan
        FROM payments
        WHERE company=?
        AND payment_status='SUCCESS'
        ORDER BY payment_date DESC
        LIMIT 1
        """,
        (company,)
    )

    row = cursor.fetchone()

    plan = row["plan"] if row else "FREE"

    conn.close()

    return {
        "company": company,
        "current_plan": plan,
        "payments": payment_count,
        "jobs_posted": jobs,
        "remaining_jobs": "Unlimited" if plan == "COMPANY_PREMIUM" else 5
    }