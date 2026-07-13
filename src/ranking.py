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