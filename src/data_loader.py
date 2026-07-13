import pandas as pd


class DataLoader:
    """
    Loads and validates student and job datasets.
    """

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

    # ======================================================
    # Load Students
    # ======================================================

    def load_students(self, filepath):

        try:

            df = pd.read_csv(filepath)

            self.validate_columns(
                df,
                self.student_columns,
                "Students"
            )

            df = self.handle_missing_values(df)

            print("✅ Students dataset loaded successfully.")

            return df

        except Exception as e:

            print(f"❌ Error loading students dataset: {e}")

            return None

    # ======================================================
    # Load Jobs
    # ======================================================

    def load_jobs(self, filepath):

        try:

            df = pd.read_csv(filepath)

            self.validate_columns(
                df,
                self.job_columns,
                "Jobs"
            )

            df = self.handle_missing_values(df)

            print("✅ Jobs dataset loaded successfully.")

            return df

        except Exception as e:

            print(f"❌ Error loading jobs dataset: {e}")

            return None

    # ======================================================
    # Validate Columns
    # ======================================================

    def validate_columns(
        self,
        df,
        required_columns,
        dataset_name
    ):

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            raise ValueError(
                f"{dataset_name} dataset is missing columns: {missing_columns}"
            )

    # ======================================================
    # Missing Values
    # ======================================================

    def handle_missing_values(self, df):

        numeric_columns = df.select_dtypes(
            include=["number"]
        ).columns

        object_columns = df.select_dtypes(
            include=["object"]
        ).columns

        df[numeric_columns] = df[numeric_columns].fillna(0)

        df[object_columns] = df[object_columns].fillna("Unknown")

        return df