"""Ranking views built from the same persisted matcher used by the API."""

import pandas as pd

from src.explainability import Explainability
from src.matching import JobMatcher
from src.threshold_validation import ThresholdValidator


class JobRanker:
    def __init__(self):
        self.matcher = JobMatcher()
        self.validator = ThresholdValidator()
        self.explainer = Explainability()

    def _details(self, student, job):
        score, recommendation, _ = self.matcher.calculate_match_score(student, job)
        validation = self.validator.validate(student, job)
        explanation = self.explainer.explain(student, job, score)
        return score, recommendation, validation, explanation

    def rank_students(self, students, job):
        rows = []
        for _, student in students.iterrows():
            score, recommendation, validation, explanation = self._details(student, job)
            rows.append({"Student": student["Name"], "Passed Thresholds": f"{self.validator.passed_count(validation)}/6", "Threshold Count": self.validator.passed_count(validation), "Score": score, "Status": self.validator.overall_status(validation), "Recommendation": recommendation, "Explanation": explanation["Explanation"]})
        return self._sorted(rows, "Student")

    def rank_jobs_for_student(self, student, jobs):
        rows = []
        for _, job in jobs.iterrows():
            score, recommendation, validation, explanation = self._details(student, job)
            rows.append({"Company": job["Company"], "Role": job["Role"], "Passed Thresholds": f"{self.validator.passed_count(validation)}/6", "Threshold Count": self.validator.passed_count(validation), "Score": score, "Status": self.validator.overall_status(validation), "Recommendation": recommendation, "Explanation": explanation["Explanation"]})
        return self._sorted(rows, "Company")

    @staticmethod
    def _sorted(rows, _label):
        frame = pd.DataFrame(rows).sort_values(["Threshold Count", "Score"], ascending=False).reset_index(drop=True)
        frame.insert(0, "Rank", frame.index + 1)
        return frame
