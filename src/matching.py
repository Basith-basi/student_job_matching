"""Explainable, persisted-config job matching."""

import json
from pathlib import Path

from src.threshold_validation import ThresholdValidator


DEFAULT_WEIGHTS = {
    "Python": 0.20,
    "SQL": 0.15,
    "Machine Learning": 0.25,
    "Communication": 0.15,
    "Experience": 0.15,
    "CGPA": 0.10,
}
FEATURES = {
    "Python": "Python_Threshold",
    "SQL": "SQL_Threshold",
    "Machine Learning": "ML_Threshold",
    "Communication": "Communication_Threshold",
    "Experience": "Experience_Threshold",
    "CGPA": "Minimum_CGPA",
}
DEFAULT_CONFIG_PATH = Path("outputs/model_config.json")


class JobMatcher:
    """Scores a student/job pair with persisted, explainable feature weights."""

    def __init__(self, config_path=DEFAULT_CONFIG_PATH):
        self.validator = ThresholdValidator()
        self.config_path = Path(config_path)
        self.weights, self.match_threshold = self._load_config()

    def _load_config(self):
        if not self.config_path.exists():
            return DEFAULT_WEIGHTS.copy(), 70.0

        with self.config_path.open(encoding="utf-8") as file:
            config = json.load(file)

        weights = config.get("weights", DEFAULT_WEIGHTS)
        if set(weights) != set(DEFAULT_WEIGHTS) or sum(weights.values()) <= 0:
            return DEFAULT_WEIGHTS.copy(), 70.0

        total = sum(float(value) for value in weights.values())
        normalised = {name: float(value) / total for name, value in weights.items()}
        return normalised, float(config.get("match_threshold", 70.0))

    @staticmethod
    def feature_scores(student, job):
        """Return six 0-100 requirement-coverage scores for a pair."""
        scores = {}
        for feature, requirement_column in FEATURES.items():
            requirement = float(job[requirement_column])
            value = float(student[feature])
            scores[feature] = 100.0 if requirement <= 0 else min(value / requirement, 1.0) * 100
        return scores

    def calculate_match_score(self, student, job):
        feature_scores = self.feature_scores(student, job)
        score = round(sum(feature_scores[name] * self.weights[name] for name in FEATURES), 2)
        validation = self.validator.validate(student, job)
        reasons = [
            f"{name}: {float(student[name]):g}/{float(job[column]):g} "
            f"({'meets' if validation[name] else 'below'} requirement)"
            for name, column in FEATURES.items()
        ]
        return score, self.get_recommendation(score), reasons

    def get_recommendation(self, score):
        if score >= 90:
            return "Highly Recommended"
        if score >= self.match_threshold:
            return "Recommended"
        if score >= 60:
            return "Potential Match"
        return "Low Match"
