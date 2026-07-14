"""
explainability.py
-----------------
Generates human-readable explanations for candidate-job matches.
"""

from typing import Dict, List


class Explainability:
    """Generates explanations for candidate-job matching."""

    def __init__(self):
        self.skill_mapping = [
            ("Python", "Python_Threshold"),
            ("SQL", "SQL_Threshold"),
            ("Machine Learning", "ML_Threshold"),
            ("Communication", "Communication_Threshold"),
        ]

    def explain(self, student: Dict, job: Dict, match_score: float) -> Dict:
        """
        Generate explanation for a candidate.

        Parameters
        ----------
        student : dict
            Student information

        job : dict
            Job information

        match_score : float
            Final similarity score

        Returns
        -------
        dict
            Explanation payload
        """

        explanations: List[str] = []

        matched_skills = []
        missing_skills = []

        passed = 0
        total = len(self.skill_mapping) + 2  # Skills + Experience + CGPA

        # ---------------------------------------------------
        # Skill Evaluation
        # ---------------------------------------------------

        for student_col, threshold_col in self.skill_mapping:

            student_score = student[student_col]
            threshold = job[threshold_col]

            if student_score >= threshold:

                passed += 1
                matched_skills.append(student_col)

                explanations.append(
                    f"✔ {student_col} matched ({student_score} ≥ {threshold})"
                )

            else:

                missing_skills.append(student_col)

                explanations.append(
                    f"✘ {student_col} below threshold ({student_score} < {threshold})"
                )

        # ---------------------------------------------------
        # Experience
        # ---------------------------------------------------

        if student["Experience"] >= job["Experience_Threshold"]:

            passed += 1

            explanations.append(
                f"✔ Experience requirement satisfied "
                f"({student['Experience']} ≥ {job['Experience_Threshold']})"
            )

        else:

            explanations.append(
                f"✘ Experience requirement not satisfied "
                f"({student['Experience']} < {job['Experience_Threshold']})"
            )

        # ---------------------------------------------------
        # CGPA
        # ---------------------------------------------------

        if student["CGPA"] >= job["Minimum_CGPA"]:

            passed += 1

            explanations.append(
                f"✔ CGPA above minimum "
                f"({student['CGPA']} ≥ {job['Minimum_CGPA']})"
            )

        else:

            explanations.append(
                f"✘ CGPA below minimum "
                f"({student['CGPA']} < {job['Minimum_CGPA']})"
            )

        # ---------------------------------------------------
        # Overall Recommendation
        # ---------------------------------------------------

        if match_score >= 90:

            recommendation = "Excellent Match"

        elif match_score >= 80:

            recommendation = "Strong Match"

        elif match_score >= 70:

            recommendation = "Good Match"

        elif match_score >= 60:

            recommendation = "Moderate Match"

        else:

            recommendation = "Low Match"

         # ---------------------------------------------------
# Return Explanation Payload
# ---------------------------------------------------

        return {
          "Match Score": round(match_score, 2),  
         "Recommendation": recommendation,
         "Matched Skills": matched_skills,
         "Missing Skills": missing_skills,
         "Explanation": explanations
}   

        # ---------------------------------------------------
        # Summary
        # ---------------------------------------------------

        summary = {
            "Student": student.get("Student_Name", "Unknown"),
            "Job": job.get("Job_Role", "Unknown"),
            "Match Score": round(match_score, 2),
            "Matched Criteria": f"{passed}/{total}",
            "Matched Skills": matched_skills,
            "Missing Skills": missing_skills,
            "Recommendation": recommendation,
            "Explanation": explanations,
        }

        return summary

    def print_explanation(self, explanation: Dict):
        """
        Print explanation in a readable format.
        """

        print("\n" + "=" * 60)
        print("MATCH EXPLANATION")
        print("=" * 60)

        print(f"Student           : {explanation['Student']}")
        print(f"Job               : {explanation['Job']}")
        print(f"Match Score       : {explanation['Match Score']}%")
        print(f"Matched Criteria  : {explanation['Matched Criteria']}")
        print(f"Recommendation    : {explanation['Recommendation']}")

        print("\nMatched Skills:")

        if explanation["Matched Skills"]:

            for skill in explanation["Matched Skills"]:
                print(f"   ✔ {skill}")

        else:
            print("   None")

        print("\nMissing Skills:")

        if explanation["Missing Skills"]:

            for skill in explanation["Missing Skills"]:
                print(f"   ✘ {skill}")

        else:
            print("   None")

        print("\nDetailed Explanation:")

        for item in explanation["Explanation"]:
            print(f"  {item}")

        print("=" * 60)