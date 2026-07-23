"""Plain-English explanations for matching decisions."""

from src.matching import JobMatcher
from src.threshold_validation import ThresholdValidator


class Explainability:
    def __init__(self):
        self.matcher = JobMatcher()
        self.validator = ThresholdValidator()

    def explain(self, student, job, match_score):
        validation = self.validator.validate(student, job)
        matched = [name for name, passed in validation.items() if name != "passed" and passed]
        missing = [name for name, passed in validation.items() if name != "passed" and not passed]
        details = [
            f"{name} {'meets' if passed else 'is below'} the requirement."
            for name, passed in validation.items() if name != "passed"
        ]
        recommendation = self.matcher.get_recommendation(match_score)
        return {
            "Match Score": round(float(match_score), 2),
            "Matched Criteria": f"{len(matched)}/6",
            "Recommendation": recommendation,
            "Matched Skills": matched,
            "Missing Skills": missing,
            "Explanation": details,
        }
