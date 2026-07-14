import csv
import os
from datetime import datetime

LOG_FILE = "experiments_log.csv"


def log_experiment(
    model_name,
    dataset,
    accuracy,
    precision,
    recall,
    fpr,
    threshold,
    remarks
):
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Date",
                "Model",
                "Dataset",
                "Accuracy",
                "Precision",
                "Recall",
                "False_Positive_Rate",
                "Threshold",
                "Remarks"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            model_name,
            dataset,
            accuracy,
            precision,
            recall,
            fpr,
            threshold,
            remarks
        ])