"""Command-line Task 7 matching-tune walkthrough."""

import json

import pandas as pd
from fastapi import FastAPI

from api.routes import router
from src.evaluation import Evaluator
from src.explainability import Explainability
from src.matching import JobMatcher
from src.threshold_validation import ThresholdValidator


# Keep the ASGI application at module level so `uvicorn main:app` can
# import it without executing the command-line walkthrough below.
app = FastAPI(title="Student Job Matching API")
app.include_router(router)


def run_demo():
    students = pd.read_csv("data/students.csv")
    jobs = pd.read_csv("data/jobs.csv")
    summary = Evaluator().evaluate(students, jobs)

    student = students.iloc[0]
    job = jobs.iloc[0]
    matcher = JobMatcher()  # Reloads the configuration persisted by evaluation.
    score, recommendation, reasons = matcher.calculate_match_score(student, job)
    validation = ThresholdValidator().validate(student, job)
    explanation = Explainability().explain(student, job, score)

    print("TASK 7 — PAY-PER-APPLICATION MATCHING TUNE")
    print(json.dumps(summary, indent=2))
    print(f"\nWalkthrough: {student['Name']} -> {job['Company']} ({job['Role']})")
    print(f"Score: {score} | Recommendation: {recommendation}")
    print(f"Eligibility: {'Eligible' if validation['passed'] else 'Not Eligible'}")
    print("Why:")
    for reason in reasons:
        print(f"- {reason}")
    print("\nPayment demo: run `uvicorn api.app:app --reload`, then call POST /applications.")
    print("The endpoint charges exactly INR 100 in test mode and creates an application only on SUCCESS.")
    print(json.dumps(explanation, indent=2))


if __name__ == "__main__":
    run_demo()
