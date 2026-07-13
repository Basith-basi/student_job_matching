import pandas as pd


class DataLoader:
    """
    Loads and validates CSV datasets.
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
            "CGPA",
        ]

        self.job_columns = [
            "Job_ID",
            "Company",
            "Role",
            "Required Python",
            "Required SQL",
            "Required ML",
            "Required Communication",
            "Minimum CGPA",
        ]

    def load_students(self, filepath):
        """
        Load student dataset.
        """
        try:
            df = pd.read_csv(filepath)
            self.validate_columns(df, self.student_columns, "Students")
            df = self.handle_missing_values(df)
            return df

        except Exception as e:
            print(f"Error loading students dataset: {e}")
            return None

    def load_jobs(self, filepath):
        """
        Load job dataset.
        """
        try:
            df = pd.read_csv(filepath)
            self.validate_columns(df, self.job_columns, "Jobs")
            df = self.handle_missing_values(df)
            return df

        except Exception as e:
            print(f"Error loading jobs dataset: {e}")
            return None

    def validate_columns(self, df, required_columns, dataset_name):
        """
        Validate dataset columns.
        """
        missing_columns = [
            column for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"{dataset_name} dataset is missing columns: {missing_columns}"
            )

    def handle_missing_values(self, df):
        """
        Handle missing values.
        """

        numeric_columns = df.select_dtypes(include=["number"]).columns
        categorical_columns = df.select_dtypes(include=["object"]).columns

        df[numeric_columns] = df[numeric_columns].fillna(0)
        df[categorical_columns] = df[categorical_columns].fillna("Unknown")

        return df