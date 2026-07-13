class Explainability:

    def explain(

        self,

        student,

        job

    ):

        explanation = []

        if student["Python"] >= job["Required Python"]:

            explanation.append(

                f"Python exceeds requirement by "

                f"{student['Python']-job['Required Python']}"

            )

        if student["SQL"] >= job["Required SQL"]:

            explanation.append(

                "SQL meets requirement"

            )

        if student["Machine Learning"] >= job["Required ML"]:

            explanation.append(

                "Strong Machine Learning score"

            )

        if student["CGPA"] >= job["Minimum CGPA"]:

            explanation.append(

                "CGPA exceeds minimum"

            )

        return explanation