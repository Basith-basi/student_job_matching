"""FastAPI routes for the Task 7 matching and pay-per-application flow."""

from fastapi import APIRouter, HTTPException
import pandas as pd

from api.database import get_connection
from api.schemas import ApplicationCreate, JobCreate, PaymentRequest, PaymentResponse, PredictionRequest, VerifyPaymentRequest
from payments.payment_service import PaymentService
from src.evaluation import Evaluator
from src.explainability import Explainability
from src.matching import JobMatcher
from src.threshold_validation import ThresholdValidator


router = APIRouter()
payment_service = PaymentService()
validator = ThresholdValidator()
explainer = Explainability()
evaluator = Evaluator()

STUDENTS_CSV = "data/students.csv"
JOBS_CSV = "data/jobs.csv"
APPLICATION_FEE = 100.0
JOB_COLUMN_MAP = {
    "job_id": "Job_ID", "company": "Company", "role": "Role",
    "python_threshold": "Python_Threshold", "sql_threshold": "SQL_Threshold",
    "ml_threshold": "ML_Threshold", "communication_threshold": "Communication_Threshold",
    "experience_threshold": "Experience_Threshold", "minimum_cgpa": "Minimum_CGPA",
}


def load_students():
    return pd.read_csv(STUDENTS_CSV)


def get_student_by_id(student_id):
    students = load_students()
    rows = students[students["Student_ID"] == student_id]
    if rows.empty:
        raise HTTPException(status_code=404, detail="Student not found")
    return rows.iloc[0]


def get_student_by_name(name):
    students = load_students()
    rows = students[students["Name"].str.casefold() == name.casefold()]
    if rows.empty:
        raise HTTPException(status_code=404, detail="Student not found")
    return rows.iloc[0]


def get_job_by_id(job_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
    conn.close()
    if row is not None:
        return pd.Series(dict(row)).rename(JOB_COLUMN_MAP)
    jobs = pd.read_csv(JOBS_CSV)
    rows = jobs[jobs["Job_ID"] == job_id]
    if rows.empty:
        raise HTTPException(status_code=404, detail="Job not found")
    return rows.iloc[0]


def match_details(student, job):
    # Reload the persisted configuration so /metrics tuning is immediately
    # reflected by every live prediction and ranking response.
    score, recommendation, reasons = JobMatcher().calculate_match_score(student, job)
    validation = validator.validate(student, job)
    return {
        "score": float(score),
        "recommendation": recommendation,
        "status": validator.overall_status(validation),
        "reasons": reasons,
        "validation": validation,
        "explanation": explainer.explain(student, job, score),
    }


@router.get("/health")
def health():
    return {"status": "healthy", "service": "student-job-matching", "payment_mode": "test"}


@router.get("/metrics")
def get_metrics():
    summary = evaluator.evaluate(pd.read_csv(STUDENTS_CSV), pd.read_csv(JOBS_CSV))
    return summary


@router.post("/predict")
def predict(request: PredictionRequest):
    student = get_student_by_id(request.student_id)
    job = get_job_by_id(request.job_id)
    return {"student": student["Name"], "company": job["Company"], "role": job["Role"], **match_details(student, job)}


@router.get("/jobs")
def get_jobs():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM jobs ORDER BY job_id").fetchall()
    conn.close()
    if rows:
        return {"total_jobs": len(rows), "jobs": [dict(row) for row in rows]}
    jobs = pd.read_csv(JOBS_CSV)
    return {"total_jobs": len(jobs), "jobs": jobs.to_dict(orient="records")}


@router.post("/jobs", status_code=201)
def create_job(job: JobCreate):
    if not all((0 <= job.python_threshold <= 100, 0 <= job.sql_threshold <= 100, 0 <= job.ml_threshold <= 100, 0 <= job.communication_threshold <= 100, job.experience_threshold >= 0, 0 <= job.minimum_cgpa <= 10)):
        raise HTTPException(status_code=422, detail="Invalid job thresholds")
    conn = get_connection()
    premium = conn.execute("SELECT 1 FROM payments WHERE company = ? AND plan = 'COMPANY_PREMIUM' AND payment_status = 'SUCCESS'", (job.company,)).fetchone()
    if premium is None:
        conn.close()
        raise HTTPException(status_code=403, detail="Company Premium Subscription Required")
    job_id = (conn.execute("SELECT COALESCE(MAX(job_id), 0) + 1 FROM jobs").fetchone()[0])
    conn.execute("""INSERT INTO jobs (job_id, company, role, skills, Python_Threshold, SQL_Threshold, ML_Threshold, Communication_Threshold, Experience_Threshold, Minimum_CGPA)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (job_id, job.company, job.role, ",".join(job.skills), job.python_threshold, job.sql_threshold, job.ml_threshold, job.communication_threshold, job.experience_threshold, job.minimum_cgpa))
    conn.commit()
    conn.close()
    return {"message": "Job created", "job_id": job_id, "company": job.company, "role": job.role}


@router.post("/applications", status_code=201)
def apply_job(application: ApplicationCreate):
    """Charge exactly 100 INR and create an application only after success."""
    student = get_student_by_name(application.student)
    job = get_job_by_id(application.job_id)
    conn = get_connection()
    duplicate = conn.execute("SELECT 1 FROM applications WHERE student_id = ? AND job_id = ?", (int(student["Student_ID"]), application.job_id)).fetchone()
    if duplicate:
        conn.close()
        raise HTTPException(status_code=409, detail="Student has already applied for this job")

    gateway_result = payment_service.charge_application()
    try:
        conn.execute("BEGIN")
        conn.execute("""INSERT INTO payments (student_name, company, job_id, plan, amount, payment_status, transaction_id)
                        VALUES (?, ?, ?, 'PAY_PER_APPLICATION', ?, ?, ?)""", (student["Name"], job["Company"], application.job_id, APPLICATION_FEE, gateway_result["status"], gateway_result["transaction_id"]))
        if gateway_result["status"] != "SUCCESS":
            conn.commit()
            return {"application_created": False, "payment_status": gateway_result["status"], "amount": APPLICATION_FEE, "transaction_id": gateway_result["transaction_id"], "message": "Payment was not successful; no application was created."}
        details = match_details(student, job)
        conn.execute("INSERT INTO applications (student_id, job_id, score, status) VALUES (?, ?, ?, ?)", (int(student["Student_ID"]), application.job_id, details["score"], details["status"]))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return {"application_created": True, "payment_status": "SUCCESS", "amount": APPLICATION_FEE, "transaction_id": gateway_result["transaction_id"], "student": student["Name"], "company": job["Company"], **details}


@router.get("/jobs/{job_id}/candidates")
def get_job_candidates(job_id: int):
    job = get_job_by_id(job_id)
    candidates = []
    for _, student in load_students().iterrows():
        details = match_details(student, job)
        candidates.append({"student": student["Name"], "passed_thresholds": validator.passed_count(details["validation"]), **details})
    candidates.sort(key=lambda item: (item["passed_thresholds"], item["score"]), reverse=True)
    for rank, candidate in enumerate(candidates, 1):
        candidate["rank"] = rank
        candidate.pop("passed_thresholds")
    return {"job_id": job_id, "company": job["Company"], "role": job["Role"], "total_candidates": len(candidates), "top_candidates": candidates[:10]}


@router.get("/students/{student_id}/jobs")
def get_student_jobs(student_id: int):
    student = get_student_by_id(student_id)
    ranked = []
    for _, job in pd.read_csv(JOBS_CSV).iterrows():
        ranked.append({"job_id": int(job["Job_ID"]), "company": job["Company"], "role": job["Role"], **match_details(student, job)})
    return sorted(ranked, key=lambda item: item["score"], reverse=True)


@router.post("/payments", response_model=PaymentResponse)
def create_subscription_payment(payment: PaymentRequest):
    result = payment_service.process_payment(payment.student_name, payment.company, payment.job_id, payment.plan)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.get("/payments")
def get_payments():
    """List all payment attempts, newest first."""
    conn = get_connection()
    payments = conn.execute("SELECT * FROM payments ORDER BY payment_date DESC, payment_id DESC").fetchall()
    conn.close()
    return [dict(payment) for payment in payments]


@router.post("/payments/verify")
def verify_payment(request: VerifyPaymentRequest):
    conn = get_connection()
    payment = conn.execute("SELECT * FROM payments WHERE transaction_id = ?", (request.transaction_id,)).fetchone()
    conn.close()
    if payment is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"transaction_id": request.transaction_id, "payment_status": payment["payment_status"], "verified": payment["payment_status"] == "SUCCESS"}


@router.get("/payments/history/{student_name}")
def payment_history(student_name: str):
    """Return all payment attempts for a student."""
    conn = get_connection()
    payments = conn.execute("SELECT * FROM payments WHERE student_name = ? COLLATE NOCASE ORDER BY payment_date DESC, payment_id DESC", (student_name,)).fetchall()
    conn.close()
    return [dict(payment) for payment in payments]


@router.get("/payments/company/{company}")
def company_payments(company: str):
    """Return all payment attempts associated with a company."""
    conn = get_connection()
    payments = conn.execute("SELECT * FROM payments WHERE company = ? COLLATE NOCASE ORDER BY payment_date DESC, payment_id DESC", (company,)).fetchall()
    conn.close()
    return [dict(payment) for payment in payments]


@router.get("/payments/{payment_id:int}")
def get_payment(payment_id: int):
    conn = get_connection()
    payment = conn.execute("SELECT * FROM payments WHERE payment_id = ?", (payment_id,)).fetchone()
    conn.close()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return dict(payment)


@router.get("/dashboard/student/{student}")
def student_dashboard(student: str):
    """Summarise a CSV-backed student's applications and payment activity."""
    student_row = get_student_by_name(student)
    student_id = int(student_row["Student_ID"])
    conn = get_connection()
    application_count = conn.execute("SELECT COUNT(*) FROM applications WHERE student_id = ?", (student_id,)).fetchone()[0]
    payment_count = conn.execute("SELECT COUNT(*) FROM payments WHERE student_name = ? COLLATE NOCASE", (student_row["Name"],)).fetchone()[0]
    latest_plan = conn.execute("SELECT plan FROM payments WHERE student_name = ? COLLATE NOCASE AND payment_status = 'SUCCESS' ORDER BY payment_date DESC, payment_id DESC LIMIT 1", (student_row["Name"],)).fetchone()
    conn.close()
    plan = latest_plan["plan"] if latest_plan else "FREE"
    return {
        "student": student_row["Name"],
        "current_plan": plan,
        "applications": application_count,
        "payments": payment_count,
        "remaining": "Pay per application" if plan == "PAY_PER_APPLICATION" else "Limited",
    }


@router.get("/dashboard/company/{company}")
def company_dashboard(company: str):
    """Summarise company job postings and subscription payments."""
    conn = get_connection()
    jobs_posted = conn.execute("SELECT COUNT(*) FROM jobs WHERE company = ? COLLATE NOCASE", (company,)).fetchone()[0]
    payment_count = conn.execute("SELECT COUNT(*) FROM payments WHERE company = ? COLLATE NOCASE", (company,)).fetchone()[0]
    latest_plan = conn.execute("SELECT plan FROM payments WHERE company = ? COLLATE NOCASE AND payment_status = 'SUCCESS' ORDER BY payment_date DESC, payment_id DESC LIMIT 1", (company,)).fetchone()
    conn.close()
    plan = latest_plan["plan"] if latest_plan else "FREE"
    return {
        "company": company,
        "current_plan": plan,
        "payments": payment_count,
        "jobs_posted": jobs_posted,
        "remaining_jobs": "Unlimited" if plan == "COMPANY_PREMIUM" else 5,
    }
