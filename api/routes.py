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
from src.spend_guardrail import SpendGuardrail
from payments.receipt_service import ReceiptService
from payments.refund_service import RefundService
from payments.reconciliation import Reconciliation
from payments.reconciliation_service import ReconciliationService
from src.conversion_quality import ConversionQualityChecker
from payments.failure_handler import PaymentFailureHandler
from payments.retry import RetryPayment
from payments.payment_logs import PaymentLogs

router = APIRouter()
payment_service = PaymentService()
validator = ThresholdValidator()
explainer = Explainability()
evaluator = Evaluator()
guardrail = SpendGuardrail()
receipt_service = ReceiptService()
refund_service = RefundService()
reconciliation = Reconciliation()
reconciliation_service = ReconciliationService()
quality_checker = ConversionQualityChecker()
failure_handler = PaymentFailureHandler()
retry_service = RetryPayment()
payment_logs = PaymentLogs()

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


@router.post("/jobs")
def create_job(job: JobCreate):
    if not all((0 <= job.python_threshold <= 100, 0 <= job.sql_threshold <= 100, 0 <= job.ml_threshold <= 100, 0 <= job.communication_threshold <= 100, job.experience_threshold >= 0, 0 <= job.minimum_cgpa <= 10)):
        raise HTTPException(status_code=422, detail="Invalid job thresholds")
    if not job.company:
        raise HTTPException(status_code=422, detail="Company is required")
    if not job.skills:
        raise HTTPException(status_code=422, detail="At least one skill is required")
    conn = get_connection()
    if job.job_id:
        existing = conn.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job.job_id,)).fetchone()
        if existing:
            conn.close()
            raise HTTPException(status_code=409, detail=f"Job with ID {job.job_id} already exists")
        job_id = job.job_id
    else:
        job_id = conn.execute("SELECT COALESCE(MAX(job_id), 0) + 1 FROM jobs").fetchone()[0]
    conn.execute("""INSERT INTO jobs (job_id, company, role, skills, Python_Threshold, SQL_Threshold, ML_Threshold, Communication_Threshold, Experience_Threshold, Minimum_CGPA)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (job_id, job.company, job.role, ",".join(job.skills), job.python_threshold, job.sql_threshold, job.ml_threshold, job.communication_threshold, job.experience_threshold, job.minimum_cgpa))
    conn.commit()
    conn.close()
    return {"message": "Job created", "job_id": job_id, "company": job.company, "role": job.role}


@router.post("/applications")
def apply_job(application: ApplicationCreate):
    """
    Pay ₹100 -> Spend Guardrail -> Save Payment ->
    Conversion Quality -> Save Application
    """

    # -----------------------------
    # Get Student
    # -----------------------------
    if application.student_id:
        student = get_student_by_id(application.student_id)
    else:
        student = get_student_by_name(application.student)

    # -----------------------------
    # Get Job
    # -----------------------------
    job = get_job_by_id(application.job_id)

    conn = get_connection()

    # -----------------------------
    # Duplicate Check
    # -----------------------------
    duplicate = conn.execute(
        """
        SELECT 1
        FROM applications
        WHERE student_id=?
        AND job_id=?
        """,
        (
            int(student["Student_ID"]),
            application.job_id
        )
    ).fetchone()

    if duplicate:
        conn.close()
        raise HTTPException(
            status_code=409,
            detail="Student already applied for this job."
        )

    # -----------------------------
    # Match Score
    # -----------------------------
    details = match_details(student, job)

    score = details["score"]

    # -----------------------------
    # Spend Guardrail (Task 8)
    # -----------------------------
    guardrail_result = guardrail.evaluate(score)

    if not guardrail_result["allow_payment"]:

        conn.close()

        raise HTTPException(
            status_code=400,
            detail={
                "warning": guardrail_result["warning"],
                "message": guardrail_result["message"],
                "score": score
            }
        )

    # -----------------------------
    # Payment Gateway (Task 7)
    # -----------------------------
    gateway_result = payment_service.charge_application()

    # -----------------------------
    # Save Payment (always, regardless of status)
    # -----------------------------
    conn.execute(
        """
        INSERT INTO payments
        (
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
            student["Name"],
            job["Company"],
            application.job_id,
            "PAY_PER_APPLICATION",
            APPLICATION_FEE,
            gateway_result["status"],
            gateway_result["transaction_id"]
        )
    )
    conn.commit()

    # -----------------------------
    # Payment Failure Handler (Task 9)
    # -----------------------------
    if gateway_result["status"] != "SUCCESS":

        conn.close()

        return failure_handler.payment_failed(gateway_result["status"])

    try:

        # -----------------------------
        # Conversion Quality (Task 9)
        # -----------------------------
        quality = quality_checker.compare(
            before_score=score,
            after_score=score
        )

        # -----------------------------
        # Save Application
        # -----------------------------
        conn.execute(
            """
            INSERT INTO applications
            (
                student_id,
                job_id,
                score,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                int(student["Student_ID"]),
                application.job_id,
                score,
                details["status"]
            )
        )

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()

    # -----------------------------
    # Response
    # -----------------------------
    return {

        "application_created": True,

        "payment_status": gateway_result["status"],

        "amount": APPLICATION_FEE,

        "transaction_id": gateway_result["transaction_id"],

        "student": student["Name"],

        "company": job["Company"],

        "score": score,

        "recommendation": details["recommendation"],

        "warning": guardrail_result["warning"],

        "message": guardrail_result["message"],

        "conversion_quality": quality,

        **details
    }


@router.get("/rankings/{job_id}")
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

@router.get("/receipt/{transaction_id}")
def receipt(transaction_id: str):

    receipt = receipt_service.generate_receipt(transaction_id)

    if receipt is None:

        raise HTTPException(
            status_code=404,
            detail="Receipt not found"
        )

    return receipt

@router.post("/refund/{transaction_id}")
def refund(transaction_id: str):

    return refund_service.refund(transaction_id)

@router.get("/reconciliation")
def reconciliation_report():
    return reconciliation_service.generate_report()

@router.get("/conversion-quality")
def conversion_quality():

    before_score = 92
    after_score = 92

    result = quality_checker.compare(
        before_score,
        after_score
    )

    return result
@router.post("/payments/fail")
def simulate_payment_failure():

    return failure_handler.payment_failed()
@router.post("/payments/retry")
def retry_payment():

    return retry_service.retry()

@router.get("/logs/payments")
def get_payment_logs():

    return {

        "logs": payment_logs.get_logs()

    }