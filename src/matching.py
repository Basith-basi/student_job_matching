from src.threshold_validation import ThresholdValidator


class JobMatcher:

    def __init__(self):

        self.validator = ThresholdValidator()

        # Weightage of each feature
        self.weights = {
            "Python": 20,
            "SQL": 15,
            "Machine Learning": 25,
            "Communication": 15,
            "Experience": 15,
            "CGPA": 10
        }

    # ---------------------------------------------------
    # Calculate Match Score
    # ---------------------------------------------------

    def calculate_match_score(self, student, job):

        score = 0
        reasons = []

        # Validate all thresholds
        validation = self.validator.validate(student, job)

        # Python
        if validation["Python"]:
            score += self.weights["Python"]
            reasons.append(
                f"Python threshold passed ({student['Python']} ≥ {job['Python_Threshold']})"
            )

        # SQL
        if validation["SQL"]:
            score += self.weights["SQL"]
            reasons.append(
                f"SQL threshold passed ({student['SQL']} ≥ {job['SQL_Threshold']})"
            )

        # Machine Learning
        if validation["Machine Learning"]:
            score += self.weights["Machine Learning"]
            reasons.append(
                f"Machine Learning threshold passed ({student['Machine Learning']} ≥ {job['ML_Threshold']})"
            )

        # Communication
        if validation["Communication"]:
            score += self.weights["Communication"]
            reasons.append(
                f"Communication threshold passed ({student['Communication']} ≥ {job['Communication_Threshold']})"
            )

        # Experience
        if validation["Experience"]:
            score += self.weights["Experience"]
            reasons.append(
                f"Experience requirement satisfied ({student['Experience']} ≥ {job['Experience_Threshold']})"
            )

        # CGPA
        if validation["CGPA"]:
            score += self.weights["CGPA"]
            reasons.append(
                f"CGPA above minimum ({student['CGPA']} ≥ {job['Minimum_CGPA']})"
            )

        score = min(score, 100)

        return round(score, 2), reasons

    # ---------------------------------------------------
    # Recommendation
    # ---------------------------------------------------

    def get_recommendation(self, score):

        if score >= 90:
            return "Highly Recommended"

        elif score >= 75:
            return "Recommended"

        elif score >= 60:
            return "Good Match"

        elif score >= 40:
            return "Moderate Match"

        else:
            return "Not Recommended"