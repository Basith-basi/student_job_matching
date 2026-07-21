import pandas as pd


class DataLoader:

    def __init__(self):
        self.student_columns = [
            "Student_ID",
            "Name",
            "Skills",
            "Python",
            "SQL",
            "Machine Learning",
            "Communication",
            "Experience",
            "CGPA"
        ]

        self.job_columns = [
            "Job_ID",
            "Company",
            "Role",
            "Python_Threshold",
            "SQL_Threshold",
            "ML_Threshold",
            "Communication_Threshold",
            "Experience_Threshold",
            "Minimum_CGPA"
        ]

    def load_students(self, file_path):
        students = pd.read_csv(file_path)
        self.validate_columns(students, self.student_columns, "Students")
        return self.handle_missing_values(students)

    def load_jobs(self, file_path):
        jobs = pd.read_csv(file_path)
        self.validate_columns(jobs, self.job_columns, "Jobs")
        return self.handle_missing_values(jobs)

    def validate_columns(self, df, required_columns, dataset_name):
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            raise ValueError(
                f"{dataset_name} dataset missing columns: {missing}"
            )

    def handle_missing_values(self, df):
        numeric = df.select_dtypes(include="number").columns
        object_cols = df.select_dtypes(include="object").columns

        df[numeric] = df[numeric].fillna(0)
        df[object_cols] = df[object_cols].fillna("Unknown")

        return df