class ThresholdValidator:
    """Validates the minimum requirements that define eligibility."""

    REQUIREMENTS = {
        "Python": "Python_Threshold",
        "SQL": "SQL_Threshold",
        "Machine Learning": "ML_Threshold",
        "Communication": "Communication_Threshold",
        "Experience": "Experience_Threshold",
        "CGPA": "Minimum_CGPA",
    }

    def validate(self, student, job):
        result = {
            feature: bool(float(student[feature]) >= float(job[requirement]))
            for feature, requirement in self.REQUIREMENTS.items()
        }
        result["passed"] = all(result.values())
        return result

    def passed_count(self, validation_result):
        return sum(bool(value) for key, value in validation_result.items() if key != "passed")

    def failed_count(self, validation_result):
        return 6 - self.passed_count(validation_result)

    def overall_status(self, validation_result):
        return "Eligible" if validation_result["passed"] else "Not Eligible"
