class ThresholdValidator:
    """
    Validates whether a student's profile satisfies
    the minimum job requirements.
    """

    def __init__(self):
        pass

    def validate(self, student, job):
        """
        Returns a dictionary containing the result of each threshold check.
        All values are converted to Python bool to avoid FastAPI JSON errors.
        """

        result = {
            "Python": bool(student["Python"] >= job["Python_Threshold"]),
            "SQL": bool(student["SQL"] >= job["SQL_Threshold"]),
            "Machine Learning": bool(
                student["Machine Learning"] >= job["ML_Threshold"]
            ),
            "Communication": bool(
                student["Communication"] >= job["Communication_Threshold"]
            ),
            "Experience": bool(
                student["Experience"] >= job["Experience_Threshold"]
            ),
            "CGPA": bool(
                student["CGPA"] >= job["Minimum_CGPA"]
            )
        }
         # Add overall result
        result["passed"] = all(result.values())

        return result

    def passed_count(self, validation_result):
        """
        Returns the number of passed thresholds.
        """
        return sum(bool(v) for v in validation_result.values())

    def failed_count(self, validation_result):
        """
        Returns the number of failed thresholds.
        """
        return len(validation_result) - self.passed_count(validation_result)

    def overall_status(self, validation_result):
        """
        Returns overall eligibility status.
        """
        return (
            "Eligible"
            if all(bool(v) for v in validation_result.values())
            else "Not Eligible"
        )