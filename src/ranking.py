from src.matching import JobMatcher
from src.threshold_validation import ThresholdValidator


class JobRanker:

    def __init__(self):

        self.matcher = JobMatcher()
        self.validator = ThresholdValidator()

    # =====================================================
    # Rank Students
    # =====================================================

    def rank_students(self, students, job):

        rankings = []

        for _, student in students.iterrows():

            # Match Score
            score, _ = self.matcher.calculate_match_score(
                student,
                job
            )

            # Recommendation
            status = self.matcher.get_recommendation(score)

            # Threshold Validation
            validation = self.validator.validate(
                student,
                job
            )

            # Count Passed Thresholds
            passed = sum(validation.values())
            total = len(validation)

            rankings.append({

                "Student": student["Name"].title(),

                "Passed Thresholds": f"{passed}/{total}",

                "Threshold Count": passed,

                "Score": round(score, 2),

                "Status": status

            })

        # Convert list to DataFrame
        import pandas as pd

        ranking = pd.DataFrame(rankings)

        # Sort by Threshold Count first, then Score
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
                "Status"
            ]
        ]

    # =====================================================
    # Rank Jobs for a Student   (Task 3 — new direction)
    # =====================================================
    #
    # This is the mirror image of rank_students: instead of holding a
    # job fixed and ranking every student against it (candidate ranking
    # for companies), we hold a student fixed and rank every job against
    # them (job ranking for students). Same scoring engine, same
    # explainability, opposite direction — this is what lets a student
    # search and see jobs ranked by fit.

    def rank_jobs_for_student(self, student, jobs):

        rankings = []

        for _, job in jobs.iterrows():

            # Match Score
            score, _ = self.matcher.calculate_match_score(
                student,
                job
            )

            # Recommendation
            status = self.matcher.get_recommendation(score)

            # Threshold Validation
            validation = self.validator.validate(
                student,
                job
            )

            # Count Passed Thresholds
            passed = sum(validation.values())
            total = len(validation)

            rankings.append({

                "Company": job["Company"].title(),

                "Role": job["Role"].title(),

                "Passed Thresholds": f"{passed}/{total}",

                "Threshold Count": passed,

                "Score": round(score, 2),

                "Status": status

            })

        import pandas as pd

        ranking = pd.DataFrame(rankings)

        # Sort by Threshold Count first, then Score — same ordering rule
        # as the candidate-ranking direction, for consistency.
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
                "Status"
            ]
        ]