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


# ==========================================================
# Helper Function
# ==========================================================

def load_data():

    students = loader.load_students(STUDENT_FILE)
    jobs = loader.load_jobs(JOB_FILE)

    students = preprocessor.handle_missing_values(students)
    students = preprocessor.remove_duplicates(students)
    students = preprocessor.format_strings(students)

    jobs = preprocessor.handle_missing_values(jobs)
    jobs = preprocessor.remove_duplicates(jobs)
    jobs = preprocessor.format_strings(jobs)

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

        student = students[
            students["Student_ID"] == request.student_id
        ]

        if student.empty:

            raise HTTPException(

                status_code=404,

                detail="Student not found."

            )

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

        feature_engineer.create_feature_vector(
            student,
            job
        )

        score, reasons = matcher.calculate_match_score(
            student,
            job
        )

        recommendation = matcher.get_recommendation(score)

        explanation = explainer.explain(
            student,
            job
        )

        logger.info("Prediction completed successfully.")

        return PredictionResponse(

            student_name=student["Name"],

            company=job["Company"],

            role=job["Role"],

            match_score=score,

            status=recommendation,

            reason=explanation

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
# Ranking Endpoint
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

        return ranking.to_dict(

            orient="records"

        )

    except HTTPException:

        raise

    except Exception as e:

        logger.error(str(e))

        raise HTTPException(

            status_code=500,

            detail="Internal Server Error."

        )