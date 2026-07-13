class JobMatcher:

    def __init__(self):

        # Weightage of each feature
        self.weights = {
            "Python": 0.30,
            "SQL": 0.20,
            "ML": 0.30,
            "Communication": 0.20
        }

    # ---------------------------------------------------
    # Calculate Match Score
    # ---------------------------------------------------

    def calculate_match_score(self, student, job):

        score = 0

        reasons = []

        # -------------------------------
        # Python
        # -------------------------------

        if student["Python"] >= job["Required Python"]:

            score += self.weights["Python"] * 100

            reasons.append("Python requirement satisfied")

        # -------------------------------
        # SQL
        # -------------------------------

        if student["SQL"] >= job["Required SQL"]:

            score += self.weights["SQL"] * 100

            reasons.append("SQL requirement satisfied")

        # -------------------------------
        # Machine Learning
        # -------------------------------

        if student["Machine Learning"] >= job["Required ML"]:

            score += self.weights["ML"] * 100

            reasons.append("Machine Learning requirement satisfied")

        # -------------------------------
        # Communication
        # -------------------------------

        if student["Communication"] >= job["Required Communication"]:

            score += self.weights["Communication"] * 100

            reasons.append("Communication requirement satisfied")

        # -------------------------------
        # Bonus for CGPA
        # -------------------------------

        if student["CGPA"] >= job["Minimum CGPA"]:

            score += 5

            reasons.append("CGPA above minimum")

        # -------------------------------
        # Bonus for Experience
        # -------------------------------

        if student["Experience"] >= 1:

            score += 5

            reasons.append("Has relevant experience")

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
            return "Moderate Match"

        else:
            return "Not Recommended"