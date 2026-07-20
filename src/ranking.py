from src.matching import JobMatcher
from src.threshold_validation import ThresholdValidator
from src.explainability import Explainability

import pandas as pd


class JobRanker:

    def __init__(self):

        self.matcher = JobMatcher()
        self.validator = ThresholdValidator()
        self.explainer = Explainability()

    # =====================================================
    # Rank Students for a Job
    # =====================================================

    def rank_students(self, students, job):

        rankings = []

        for _, student in students.iterrows():

            # ----------------------------------------
            # Match Score
            # ----------------------------------------

            score, _ = self.matcher.calculate_match_score(
                student,
                job
            )

            # ----------------------------------------
            # Recommendation
            # ----------------------------------------

            status = self.matcher.get_recommendation(score)

            # ----------------------------------------
            # Threshold Validation
            # ----------------------------------------

            validation = self.validator.validate(
                student,
                job
            )

            passed = sum(validation.values())
            total = len(validation)

            # ----------------------------------------
            # Explainability
            # ----------------------------------------

            explanation = self.explainer.explain(
                student,
                job,
                score
            )

            rankings.append({

                "Student": student["Name"].title(),

                "Passed Thresholds": f"{passed}/{total}",

                "Threshold Count": passed,

                "Score": round(score, 2),

                "Status": status,

                "Recommendation":
                    explanation["Recommendation"],

                "Matched Skills":
                    ", ".join(explanation["Matched Skills"]),

                "Missing Skills":
                    ", ".join(explanation["Missing Skills"]),

                "Explanation":
                    "\n".join(explanation["Explanation"])

            })

        ranking = pd.DataFrame(rankings)

        ranking = ranking.sort_values(

            by=["Threshold Count", "Score"],

            ascending=False

        )

        ranking.reset_index(drop=True, inplace=True)

        ranking["Rank"] = ranking.index + 1

        return ranking[
            [

                "Rank",

                "Student",

                "Passed Thresholds",

                "Score",

                "Status",

                "Recommendation",

                "Matched Skills",

                "Missing Skills",

                "Explanation"

            ]
        ]

    # =====================================================
    # Rank Jobs for a Student
    # =====================================================

    def rank_jobs_for_student(self, student, jobs):

        rankings = []

        for _, job in jobs.iterrows():

            # ----------------------------------------
            # Match Score
            # ----------------------------------------

         score, _ = self.matcher.calculate_match_score(
         student,
         job
    )

            # ----------------------------------------
            # Recommendation
            # ----------------------------------------

         status = self.matcher.get_recommendation(score)

            # ----------------------------------------
            # Threshold Validation
            # ----------------------------------------

         validation = self.validator.validate(

                student,

                job

            )

         passed = sum(validation.values())
         total = len(validation)

            # ----------------------------------------
            # Explainability
            # ----------------------------------------

         explanation = self.explainer.explain(

                student,

                job,

                score

            )

         rankings.append({

                "Company": job["Company"].title(),

                "Role": job["Role"].title(),

                "Passed Thresholds": f"{passed}/{total}",

                "Threshold Count": passed,

                "Score": round(score, 2),

                "Status": status,

                "Recommendation":
                    explanation["Recommendation"],

                "Matched Skills":
                    ", ".join(explanation["Matched Skills"]),

                "Missing Skills":
                    ", ".join(explanation["Missing Skills"]),

                "Explanation":
                    "\n".join(explanation["Explanation"])

            })

        ranking = pd.DataFrame(rankings)

        ranking = ranking.sort_values(

            by=["Threshold Count", "Score"],

            ascending=False

        )

        ranking.reset_index(drop=True, inplace=True)

        ranking["Rank"] = ranking.index + 1

        return ranking[
            [

                "Rank",

                "Company",

                "Role",

                "Passed Thresholds",

                "Score",

                "Status",

                "Recommendation",

                "Matched Skills",

                "Missing Skills",

                "Explanation"

            ]
        ]