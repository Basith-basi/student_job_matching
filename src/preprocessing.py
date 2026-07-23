import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler, MinMaxScaler


class DataPreprocessor:

    def __init__(self):
        self.label_encoder = LabelEncoder()
        self.standard_scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()

    # --------------------------------------------------
    # Missing Values
    # --------------------------------------------------
    def handle_missing_values(self, df):

        numeric_columns = df.select_dtypes(include=["number"]).columns
        categorical_columns = df.select_dtypes(include=["object"]).columns

        # Fill numeric values with column mean
        df[numeric_columns] = df[numeric_columns].fillna(
            df[numeric_columns].mean()
        )

        # Fill categorical values with Unknown
        df[categorical_columns] = df[categorical_columns].fillna("Unknown")

        return df

    # --------------------------------------------------
    # Duplicate Rows
    # --------------------------------------------------
    def remove_duplicates(self, df):

        before = len(df)

        df = df.drop_duplicates()

        after = len(df)

        print(f"Removed {before-after} duplicate rows.")

        return df

    # --------------------------------------------------
    # String Formatting
    # --------------------------------------------------
    def format_strings(self, df):

        string_columns = df.select_dtypes(include=["object"]).columns

        for col in string_columns:

            df[col] = (
                df[col]
                .str.strip()
                .str.lower()
            )

        return df

    # --------------------------------------------------
    # Label Encoding
    # --------------------------------------------------
    def label_encode(self, df, column):

        df[column] = self.label_encoder.fit_transform(df[column])

        return df

    # --------------------------------------------------
    # One Hot Encoding
    # --------------------------------------------------
    def one_hot_encode(self, df, columns):

        df = pd.get_dummies(df,
                            columns=columns,
                            drop_first=True)

        return df

    # --------------------------------------------------
    # Standard Scaling
    # --------------------------------------------------
    def standard_scale(self, df, columns):

        df[columns] = self.standard_scaler.fit_transform(df[columns])

        return df

    # --------------------------------------------------
    # Min-Max Scaling
    # --------------------------------------------------
    def minmax_scale(self, df, columns):

        df[columns] = self.minmax_scaler.fit_transform(df[columns])

        return df