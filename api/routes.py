from fastapi import APIRouter, HTTPException

from api.schemas import (
    PredictionRequest,
    PredictionResponse
)

from config import STUDENT_FILE, JOB_FILE

from src.data_loader import DataLoader
from src.preprocessing import DataPreprocessor
from src.feature_engineering import FeatureEngineer
from src.matching import JobMatcher
from src.ranking import JobRanker
from src.explainability import Explainability
from src.threshold_validation import ThresholdValidator
from src.evaluation import Evaluator
from src.utils import logger


router = APIRouter()

# ==========================================================
# Initialize Classes
# ==========================================================

loader = DataLoader()
preprocessor = DataPreprocessor()
feature_engineer = FeatureEngineer()
matcher = JobMatcher()
ranker = JobRanker()
explainer = Explainability()
validator = ThresholdValidator()
evaluator = Evaluator()


# ==========================================================
# Helper Function
# ==========================================================

def load_data():

    students = loader.load_students(STUDENT_FILE)
    jobs = loader.load_jobs(JOB_FILE)

    students = preprocessor.handle_missing_values(students)
    students = preprocessor.remove_duplicates(students)
    students = preprocessor.format_strings(students)
    students["Student_ID"] = students["Student_ID"].astype(int)

    jobs = preprocessor.handle_missing_values(jobs)
    jobs = preprocessor.remove_duplicates(jobs)
    jobs = preprocessor.format_strings(jobs)
    jobs["Job_ID"] = jobs["Job_ID"].astype(int)

    return students, jobs


# ==========================================================
# Home Endpoint
# ==========================================================

@router.get("/")
def home():

    return {
        "project": "Student Job Matching System",
        "version": "1.0.0",
        "status": "Running"
    }


# ==========================================================
# Health Endpoint
# ==========================================================

@router.get("/health")
def health():

    return {
        "status": "healthy",
        "message": "API is running successfully."
    }


# ==========================================================
# Prediction Endpoint
# ==========================================================

@router.post(
    "/predict",
    response_model=PredictionResponse
)
def predict(request: PredictionRequest):

    try:

        logger.info("Loading datasets...")

        students, jobs = load_data()

        # ----------------------------------
        # Lookup student
        # ----------------------------------

        student = students[
            students["Student_ID"] == request.student_id
        ]

        if student.empty:
            raise HTTPException(
                status_code=404,
                detail="Student not found."
            )

        # ----------------------------------
        # Lookup job
        # ----------------------------------

        job = jobs[
            jobs["Job_ID"] == request.job_id
        ]

        if job.empty:
            raise HTTPException(
                status_code=404,
                detail="Job not found."
            )

        student = student.iloc[0]
        job = job.iloc[0]

        # ----------------------------------
        # Feature Engineering
        # ----------------------------------

        features = feature_engineer.create_feature_vector(
            student,
            job
        )

        # ----------------------------------
        # Threshold Validation
        # ----------------------------------

        validation = validator.validate(
            student,
            job
        )

        # ----------------------------------
        # Matching
        # ----------------------------------

        score, reasons = matcher.calculate_match_score(
            student,
            job
        )

        recommendation = matcher.get_recommendation(score)

        # ----------------------------------
        # Explainability
        # ----------------------------------

        explanation = explainer.explain(
            student,
            job,
            score
        )

        logger.info("Prediction completed successfully.")

        return PredictionResponse(
            student_name=student["Name"],
            company=job["Company"],
            role=job["Role"],
            match_score=score,
            status=recommendation,
            threshold_validation=validation,
            reasons=explanation
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error."
        )


# ==========================================================
# Ranking Endpoint (company-facing: candidates for a job)
# ==========================================================

@router.get("/rankings")
def rankings(job_id: int):

    try:

        students, jobs = load_data()

        job = jobs[
            jobs["Job_ID"] == job_id
        ]

        if job.empty:
            raise HTTPException(
                status_code=404,
                detail="Job not found."
            )

        ranking = ranker.rank_students(
            students,
            job.iloc[0]
        )

        return ranking.to_dict(orient="records")

    except HTTPException:
        raise

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error."
        )


# ==========================================================
# Job Ranking for a Student Endpoint (student-facing view)
# ==========================================================

@router.get("/jobs-for-student")
def jobs_for_student(student_id: int):
    """
    The other half of Task 3: given a student, return jobs ranked by
    fit for THEM — this is what powers the student-facing search view,
    as opposed to /rankings which powers the company-facing view.
    """

    try:

        students, jobs = load_data()

        student = students[
            students["Student_ID"] == student_id
        ]

        if student.empty:
            raise HTTPException(
                status_code=404,
                detail="Student not found."
            )

        ranking = ranker.rank_jobs_for_student(
            student.iloc[0],
            jobs
        )

        return ranking.to_dict(orient="records")

    except HTTPException:
        raise

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error."
        )


# ==========================================================
# Metrics Endpoint — real held-out numbers, not claims
# ==========================================================

@router.get("/metrics")
def metrics():
    """
    Runs the same held-out evaluation used in main.py (baseline vs
    model, precision/recall/FPR on a 30% held-out split of every
    student x job pair) and returns the numbers. This is what backs
    "show numbers, not vibes" from the API surface too, not just the
    console demo.
    """

    try:

        students, jobs = load_data()

        results = evaluator.evaluate(students, jobs)

        m = results["model_metrics"]
        b = results["baseline_metrics"]

        return {
            "n_train": len(results["train"]),
            "n_test": len(results["test"]),
            "model_precision": round(m["precision"], 4),
            "model_recall": round(m["recall"], 4),
            "model_f1": round(m["f1"], 4),
            "model_fpr": round(m["fpr"], 4),
            "baseline_precision": round(b["precision"], 4),
            "baseline_recall": round(b["recall"], 4),
            "baseline_f1": round(b["f1"], 4),
            "baseline_fpr": round(b["fpr"], 4),
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error."
        )


# ==========================================================
# Job Thresholds Endpoint
# ==========================================================

@router.get("/thresholds/{job_id}")
def get_thresholds(job_id: int):

    try:

        _, jobs = load_data()

        job = jobs[
            jobs["Job_ID"] == job_id
        ]

        if job.empty:
            raise HTTPException(
                status_code=404,
                detail="Job not found."
            )

        job = job.iloc[0]

        return {
            "Job_ID": int(job["Job_ID"]),
            "Company": job["Company"],
            "Role": job["Role"],
            "Thresholds": {
                "Python": int(job["Python_Threshold"]),
                "SQL": int(job["SQL_Threshold"]),
                "Machine Learning": int(job["ML_Threshold"]),
                "Communication": int(job["Communication_Threshold"]),
                "Experience": int(job["Experience_Threshold"]),
                "CGPA": float(job["Minimum_CGPA"])
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error."
        )