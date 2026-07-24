class SpendGuardrail:
    """
    Checks whether the student should pay for applying
    based on the match score.
    """

    def evaluate(self, score: float):

        if score >= 90:
            return {
                "allow_payment": True,
                "risk": "LOW",
                "warning": None,
                "message": "Excellent match. Payment recommended."
            }

        elif score >= 75:
            return {
                "allow_payment": True,
                "risk": "MEDIUM",
                "warning": None,
                "message": "Good match. Payment is recommended."
            }

        elif score >= 50:
            return {
                "allow_payment": True,
                "risk": "HIGH",
                "warning": "Average Match",
                "message": "This job is only an average match. Apply carefully."
            }

        else:
            return {
                "allow_payment": False,
                "risk": "VERY HIGH",
                "warning": "Low-fit Warning",
                "message": "This job is a poor match. Paying may not be worthwhile."
            }