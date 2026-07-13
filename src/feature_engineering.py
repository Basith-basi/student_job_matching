import pandas as pd


class FeatureEngineer:

    def __init__(self):
        pass

    # --------------------------------------------------
    # Skill Gap Features
    # --------------------------------------------------

    def calculate_skill_gaps(self, student, job):

        features = {}

        features["Python Gap"] = (
            student["Python"] -
            job["Required Python"]
        )

        features["SQL Gap"] = (
            student["SQL"] -
            job["Required SQL"]
        )

        features["ML Gap"] = (
            student["Machine Learning"] -
            job["Required ML"]
        )

        features["Communication Gap"] = (
            student["Communication"] -
            job["Required Communication"]
        )

        return features

    # --------------------------------------------------
    # Experience Difference
    # --------------------------------------------------

    def experience_difference(self, student, job):

        if "Required Experience" in job.index:

            return (
                student["Experience"] -
                job["Required Experience"]
            )

        return student["Experience"]

    # --------------------------------------------------
    # CGPA Difference
    # --------------------------------------------------

    def cgpa_difference(self, student, job):

        return (
            student["CGPA"] -
            job["Minimum CGPA"]
        )

    # --------------------------------------------------
    # Skill Overlap
    # --------------------------------------------------

    def skill_overlap(self, student, job):

        student_skills = set(
            student["Skills"].split(",")
        )

        role = job["Role"].lower()

        required_skills = []

        if "ml" in role or "ai" in role:
            required_skills = [
                "python",
                "ml",
                "sql"
            ]

        elif "data" in role:
            required_skills = [
                "python",
                "sql"
            ]

        elif "developer" in role:
            required_skills = [
                "python",
                "sql"
            ]

        student_skills = {
            skill.strip().lower()
            for skill in student_skills
        }

        overlap = len(
            student_skills.intersection(required_skills)
        )

        return overlap

    # --------------------------------------------------
    # Final Feature Vector
    # --------------------------------------------------

    def create_feature_vector(self, student, job):

        features = {}

        features.update(
            self.calculate_skill_gaps(student, job)
        )

        features["CGPA Difference"] = (
            self.cgpa_difference(student, job)
        )

        features["Experience Difference"] = (
            self.experience_difference(student, job)
        )

        features["Skill Overlap"] = (
            self.skill_overlap(student, job)
        )

        return features