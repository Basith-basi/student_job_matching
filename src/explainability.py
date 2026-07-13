class Explainability:

    def __init__(self):
        pass

    def explain(self, student, job):

        reasons = []

        # Python
        if student["Python"] >= job["Python_Threshold"]:
            reasons.append(
                f"Python threshold passed ({student['Python']} ≥ {job['Python_Threshold']})"
            )
        else:
            reasons.append(
                f"Python threshold not met ({student['Python']} < {job['Python_Threshold']})"
            )

        # SQL
        if student["SQL"] >= job["SQL_Threshold"]:
            reasons.append(
                f"SQL threshold passed ({student['SQL']} ≥ {job['SQL_Threshold']})"
            )
        else:
            reasons.append(
                f"SQL threshold not met ({student['SQL']} < {job['SQL_Threshold']})"
            )

        # Machine Learning
        if student["Machine Learning"] >= job["ML_Threshold"]:
            reasons.append(
                f"Machine Learning threshold passed ({student['Machine Learning']} ≥ {job['ML_Threshold']})"
            )
        else:
            reasons.append(
                f"Machine Learning threshold not met ({student['Machine Learning']} < {job['ML_Threshold']})"
            )

        # Communication
        if student["Communication"] >= job["Communication_Threshold"]:
            reasons.append(
                f"Communication threshold passed ({student['Communication']} ≥ {job['Communication_Threshold']})"
            )
        else:
            reasons.append(
                f"Communication threshold not met ({student['Communication']} < {job['Communication_Threshold']})"
            )

        # Experience
        if student["Experience"] >= job["Experience_Threshold"]:
            reasons.append(
                f"Experience requirement satisfied ({student['Experience']} ≥ {job['Experience_Threshold']})"
            )
        else:
            reasons.append(
                f"Experience requirement not satisfied ({student['Experience']} < {job['Experience_Threshold']})"
            )

        # CGPA
        if student["CGPA"] >= job["Minimum_CGPA"]:
            reasons.append(
                f"CGPA above minimum ({student['CGPA']} ≥ {job['Minimum_CGPA']})"
            )
        else:
            reasons.append(
                f"CGPA below minimum ({student['CGPA']} < {job['Minimum_CGPA']})"
            )

        return reasons