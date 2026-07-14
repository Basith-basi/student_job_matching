"""
Baseline model — required by the study guide (Section 4, "Baseline first"):

    "Before any clever model, build a dumb baseline (e.g. rank by overlap
    of required vs verified skills). Every later number is only
    meaningful relative to this baseline."

This baseline does exactly that and nothing more: it counts how many of
the job's three named skill areas (Python, SQL, Machine Learning) appear
in the student's self-listed `Skills` string, and turns that into a 0-100
score. It ignores thresholds, experience, CGPA, and communication
entirely. It exists purely so the weighted threshold-aware model in
matching.py has something to beat.
"""


class BaselineRanker:

    REQUIRED_SKILLS = ["python", "sql", "ml", "machine learning"]

    def skill_overlap_score(self, student, job):
        """
        Score = (number of job-relevant skills the student lists) /
                (number of skill areas the job cares about) * 100.

        A job "cares about" a skill area if it has a threshold > 0 for it.
        """

        student_skills = {
            s.strip().lower() for s in str(student["Skills"]).split(",")
        }

        # Normalise "machine learning" / "ml" to one concept.
        has_python = "python" in student_skills
        has_sql = "sql" in student_skills
        has_ml = ("ml" in student_skills) or ("machine learning" in student_skills)

        job_cares = {
            "python": job.get("Python_Threshold", 0) > 0,
            "sql": job.get("SQL_Threshold", 0) > 0,
            "ml": job.get("ML_Threshold", 0) > 0,
        }

        total_relevant = sum(job_cares.values()) or 1

        overlap = 0
        if job_cares["python"] and has_python:
            overlap += 1
        if job_cares["sql"] and has_sql:
            overlap += 1
        if job_cares["ml"] and has_ml:
            overlap += 1

        score = (overlap / total_relevant) * 100

        return round(score, 2)

    def predict(self, student, job, cutoff=50):
        """Binary prediction: does the baseline consider this a match?"""

        score = self.skill_overlap_score(student, job)

        return 1 if score >= cutoff else 0

    def rank_students(self, students, job):
        """Baseline version of candidate ranking (job -> students)."""

        import pandas as pd

        rows = []

        for _, student in students.iterrows():
            score = self.skill_overlap_score(student, job)

            rows.append({
                "Student": student["Name"].title(),
                "Baseline Score": score,
            })

        df = pd.DataFrame(rows).sort_values(
            by="Baseline Score", ascending=False
        ).reset_index(drop=True)

        df["Rank"] = df.index + 1

        return df[["Rank", "Student", "Baseline Score"]]

    def rank_jobs(self, student, jobs):
        """Baseline version of job ranking (student -> jobs)."""

        import pandas as pd

        rows = []

        for _, job in jobs.iterrows():
            score = self.skill_overlap_score(student, job)

            rows.append({
                "Company": job["Company"].title(),
                "Role": job["Role"].title(),
                "Baseline Score": score,
            })

        df = pd.DataFrame(rows).sort_values(
            by="Baseline Score", ascending=False
        ).reset_index(drop=True)

        df["Rank"] = df.index + 1

        return df[["Rank", "Company", "Role", "Baseline Score"]]
