class ThresholdValidator:
    """
    Validates whether a student's profile satisfies
    the minimum job requirements.
    """

    def __init__(self):
        pass

    def validate(self, student, job):

        result = {

            "Python":
                student["Python"] >= job["Python_Threshold"],

            "SQL":
                student["SQL"] >= job["SQL_Threshold"],

            "Machine Learning":
                student["Machine Learning"] >= job["ML_Threshold"],

            "Communication":
                student["Communication"] >= job["Communication_Threshold"],

            "Experience":
                student["Experience"] >= job["Experience_Threshold"],

            "CGPA":
                student["CGPA"] >= job["Minimum_CGPA"]

        }

        return result

    def passed_count(self, validation_result):
        """
        Returns number of passed thresholds.
        """

        return sum(validation_result.values())

    def failed_count(self, validation_result):
        """
        Returns number of failed thresholds.
        """

        return len(validation_result) - sum(validation_result.values())

    def overall_status(self, validation_result):
        """
        Overall threshold status.
        """

        if all(validation_result.values()):
            return "Eligible"

        return "Not Eligible"