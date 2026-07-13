class FeatureEngineer:

    def __init__(self):
        pass

    # -------------------------------
    # Gap Features (Task 1)
    # -------------------------------

    def python_gap(self, student, job):
        return student["Python"] - job["Python_Threshold"]

    def sql_gap(self, student, job):
        return student["SQL"] - job["SQL_Threshold"]

    def ml_gap(self, student, job):
        return student["Machine Learning"] - job["ML_Threshold"]

    def communication_gap(self, student, job):
        return student["Communication"] - job["Communication_Threshold"]

    def cgpa_difference(self, student, job):
        return student["CGPA"] - job["Minimum_CGPA"]

    def experience_difference(self, student, job):
        return student["Experience"] - job["Experience_Threshold"]

    def skill_overlap(self, student, job):
        skills = [skill.strip().lower() for skill in student["Skills"].split(",")]

        overlap = 0

        if "python" in skills:
            overlap += 1

        if "sql" in skills:
            overlap += 1

        if "ml" in skills or "machine learning" in skills:
            overlap += 1

        return overlap

    # -------------------------------
    # Match Vector (Task 2)
    # -------------------------------

    def create_match_vector(self, student, job):

        return {
            "python_match": student["Python"] >= job["Python_Threshold"],
            "sql_match": student["SQL"] >= job["SQL_Threshold"],
            "ml_match": student["Machine Learning"] >= job["ML_Threshold"],
            "communication_match": student["Communication"] >= job["Communication_Threshold"],
            "experience_match": student["Experience"] >= job["Experience_Threshold"],
            "cgpa_match": student["CGPA"] >= job["Minimum_CGPA"]
        }

    # -------------------------------
    # Complete Feature Vector
    # -------------------------------

    def create_feature_vector(self, student, job):

        features = {

            "Python Gap":
                self.python_gap(student, job),

            "SQL Gap":
                self.sql_gap(student, job),

            "ML Gap":
                self.ml_gap(student, job),

            "Communication Gap":
                self.communication_gap(student, job),

            "CGPA Difference":
                self.cgpa_difference(student, job),

            "Experience Difference":
                self.experience_difference(student, job),

            "Skill Overlap":
                self.skill_overlap(student, job)
        }

        # Add Match Vector
        features.update(
            self.create_match_vector(student, job)
        )

        return features