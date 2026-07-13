import pandas as pd

from src.matching import JobMatcher


class JobRanker:

    def __init__(self):

        self.matcher = JobMatcher()

    def rank_students(self, students, job):

        results = []

        for _, student in students.iterrows():

            score, reasons = self.matcher.calculate_match_score(
                student,
                job
            )

            status = self.matcher.get_recommendation(score)

            results.append({

                "Student ID": student["Student_ID"],

                "Student": student["Name"],

                "Score": score,

                "Status": status,

                "Reasons": reasons

            })

        ranking = pd.DataFrame(results)

        ranking = ranking.sort_values(

            by="Score",

            ascending=False

        ).reset_index(drop=True)

        ranking.insert(

            0,

            "Rank",

            range(1, len(ranking)+1)

        )

        return ranking