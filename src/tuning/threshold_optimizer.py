import os
import json
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

from src.matching import JobMatcher
from src.threshold_validation import ThresholdValidator


class ThresholdOptimizer:
    """
    Task 7
    --------
    Finds the best match threshold using held-out data.

    The optimizer evaluates multiple thresholds and chooses the one
    with the highest F1 Score while also minimizing False Positive Rate.
    """

    def __init__(self):

        self.matcher = JobMatcher()
        self.validator = ThresholdValidator()

        self.output_folder = "outputs"

        os.makedirs(self.output_folder, exist_ok=True)

        self.thresholds = [
            45,
            50,
            55,
            60,
            65,
            70
        ]

    # ==========================================================
    # Build labelled student-job pairs
    # ==========================================================

    def build_dataset(self, students, jobs):

        rows = []

        for _, student in students.iterrows():

            for _, job in jobs.iterrows():

                validation = self.validator.validate(student, job)

                ground_truth = 1 if all(validation.values()) else 0

                score, _, _ = self.matcher.calculate_match_score(student, job)

                rows.append({

                    "Student_ID": student["Student_ID"],

                    "Job_ID": job["Job_ID"],

                    "GroundTruth": ground_truth,

                    "Score": score

                })

        return pd.DataFrame(rows)

    # ==========================================================
    # Calculate metrics
    # ==========================================================

    def calculate_metrics(self, y_true, y_pred):

        precision = precision_score(
            y_true,
            y_pred,
            zero_division=0
        )

        recall = recall_score(
            y_true,
            y_pred,
            zero_division=0
        )

        f1 = f1_score(
            y_true,
            y_pred,
            zero_division=0
        )

        cm = confusion_matrix(
            y_true,
            y_pred,
            labels=[0, 1]
        )

        tn, fp, fn, tp = cm.ravel()

        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

        return {

            "Precision": precision,

            "Recall": recall,

            "F1": f1,

            "FPR": fpr,

            "TP": tp,

            "FP": fp,

            "TN": tn,

            "FN": fn

        }

    # ==========================================================
    # Evaluate every threshold
    # ==========================================================

    def evaluate_thresholds(self, students, jobs):

        dataset = self.build_dataset(
            students,
            jobs
        )

        y_true = dataset["GroundTruth"]

        results = []

        print("\n")
        print("=" * 65)
        print("TASK 7 - THRESHOLD OPTIMIZATION")
        print("=" * 65)

        for threshold in self.thresholds:

            y_pred = (
                dataset["Score"] >= threshold
            ).astype(int)

            metrics = self.calculate_metrics(
                y_true,
                y_pred
            )

            metrics["Threshold"] = threshold

            results.append(metrics)

            print(
                f"Threshold {threshold:>2} | "
                f"Precision={metrics['Precision']:.3f} | "
                f"Recall={metrics['Recall']:.3f} | "
                f"F1={metrics['F1']:.3f} | "
                f"FPR={metrics['FPR']:.3f}"
            )

        results = pd.DataFrame(results)

        return results
    
        # ==========================================================
    # Find Best Threshold
    # ==========================================================

    def find_best_threshold(self, students, jobs):

        results = self.evaluate_thresholds(
            students,
            jobs
        )

        best_row = results.sort_values(
            by=["F1", "Precision", "Recall"],
            ascending=False
        ).iloc[0]

        best_threshold = int(best_row["Threshold"])

        print("\n" + "=" * 65)
        print("BEST THRESHOLD FOUND")
        print("=" * 65)

        print(f"Threshold : {best_threshold}")
        print(f"Precision : {best_row['Precision']:.3f}")
        print(f"Recall    : {best_row['Recall']:.3f}")
        print(f"F1 Score  : {best_row['F1']:.3f}")
        print(f"FPR       : {best_row['FPR']:.3f}")

        self.save_results(results)
        self.save_best_threshold(best_row)
        self.plot_metrics(results)

        return best_threshold

    # ==========================================================
    # Save Results
    # ==========================================================

    def save_results(self, results):

        csv_path = os.path.join(
            self.output_folder,
            "threshold_metrics.csv"
        )

        results.to_csv(
            csv_path,
            index=False
        )

        print(f"\nThreshold metrics saved to : {csv_path}")

    # ==========================================================
    # Save Best Threshold
    # ==========================================================

    def save_best_threshold(self, best_row):

        json_path = os.path.join(
            self.output_folder,
            "best_threshold.json"
        )

        data = {

            "best_threshold": int(best_row["Threshold"]),

            "precision": float(best_row["Precision"]),

            "recall": float(best_row["Recall"]),

            "f1_score": float(best_row["F1"]),

            "false_positive_rate": float(best_row["FPR"])

        }

        with open(
            json_path,
            "w"
        ) as f:

            json.dump(
                data,
                f,
                indent=4
            )

        print(f"Best threshold saved to : {json_path}")

    # ==========================================================
    # Plot Metrics
    # ==========================================================

    def plot_metrics(self, results):

        plt.figure(figsize=(8,5))

        plt.plot(
            results["Threshold"],
            results["Precision"],
            marker="o",
            label="Precision"
        )

        plt.plot(
            results["Threshold"],
            results["Recall"],
            marker="o",
            label="Recall"
        )

        plt.plot(
            results["Threshold"],
            results["F1"],
            marker="o",
            label="F1 Score"
        )

        plt.xlabel("Threshold")

        plt.ylabel("Score")

        plt.title("Threshold Optimization")

        plt.grid(True)

        plt.legend()

        plt.tight_layout()

        plot_path = os.path.join(
            self.output_folder,
            "threshold_optimization.png"
        )

        plt.savefig(plot_path)

        plt.close()

        print(f"Threshold optimization plot saved to : {plot_path}")

    # ==========================================================
    # Load Best Threshold
    # ==========================================================

    def load_best_threshold(self):

        json_path = os.path.join(
            self.output_folder,
            "best_threshold.json"
        )

        if not os.path.exists(json_path):

            return 60

        with open(json_path, "r") as f:

            data = json.load(f)

        return data["best_threshold"]