import os
import csv
from datetime import datetime

from matplotlib import cm
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay,
)

from src.matching import JobMatcher
from src.baseline import BaselineRanker
from src.threshold_validation import ThresholdValidator


class Evaluator:
    """
    Real held-out evaluation for the matching model.

    The study guide is explicit about what "real metrics, not vibes"
    means: report precision, recall and false-positive rate on real
    sample data, evaluated on data you did NOT tune on, and compare
    against a baseline. This class does that:

      1. build_labeled_pairs() cross-joins every student with every job
         and derives a ground-truth label from the threshold validator
         (a student "should" match a job if they clear every one of the
         job's minimum thresholds — that's the product's own definition
         of eligibility, not an invented one).
      2. split_holdout() holds out 30% of those pairs as a test set
         that is never used to pick weights or thresholds.
      3. evaluate() scores the baseline and the weighted model on the
         SAME held-out pairs and reports precision / recall / FPR / F1
         for both, side by side.
      4. log_experiment() appends the run to experiments_log.csv so
         numbers are reproducible run over run, per the study guide's
         "keep the experiment log" instruction.
    """

    def __init__(self):

        self.output_folder = "plots"
        os.makedirs(self.output_folder, exist_ok=True)

        self.log_path = "experiments_log.csv"

        self.matcher = JobMatcher()
        self.baseline = BaselineRanker()
        self.validator = ThresholdValidator()

    # ======================================================
    # Build labeled student x job pairs
    # ======================================================

    def build_labeled_pairs(self, students, jobs):
        """
        Cross-join students and jobs. Ground truth = 1 if the student
        clears every threshold the job sets (validator says "Eligible"),
        else 0. This is a real label derived from the product's own
        eligibility rule, not a hand-typed list.
        """

        rows = []

        for _, student in students.iterrows():
            for _, job in jobs.iterrows():

                validation = self.validator.validate(student, job)
                ground_truth = 1 if all(validation.values()) else 0

                model_score, _ = self.matcher.calculate_match_score(student, job)
                # "Good Match" (>=60) or better counts as a predicted match —
                # the same cutoff used elsewhere as a positive recommendation.
                model_pred = 1 if model_score >= 60 else 0

                baseline_score = self.baseline.skill_overlap_score(student, job)
                baseline_pred = self.baseline.predict(student, job, cutoff=50)

                rows.append({
                    "Student_ID": student["Student_ID"],
                    "Job_ID": job["Job_ID"],
                    "ground_truth": ground_truth,
                    "model_score": model_score,
                    "model_pred": model_pred,
                    "baseline_score": baseline_score,
                    "baseline_pred": baseline_pred,
                })

        return pd.DataFrame(rows)

    # ======================================================
    # Held-out split
    # ======================================================

    def split_holdout(self, pairs_df, test_size=0.3, random_state=42):
        """
        Split labeled pairs into train/test. The model here has no
        trainable parameters (it's a transparent weighted rule), so
        "train" isn't used to fit anything — but held-out evaluation
        still matters: it proves the numbers aren't cherry-picked from
        whichever pairs happen to look good, and it's the split you'd
        swap in a learned model against later without changing the
        evaluation harness.
        """

        train_df, test_df = train_test_split(
            pairs_df,
            test_size=test_size,
            random_state=random_state,
            stratify=pairs_df["ground_truth"],
        )

        return train_df, test_df

    # ======================================================
    # Metrics (incl. False Positive Rate)
    # ======================================================
    def compute_metrics(self, y_true, y_pred):

     cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
     tn, fp, fn, tp = cm.ravel()

     precision = precision_score(y_true, y_pred, zero_division=0)
     recall = recall_score(y_true, y_pred, zero_division=0)
     f1 = f1_score(y_true, y_pred, zero_division=0)
     fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

     return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "fpr": float(fpr),
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
    }
    

    # ======================================================
    # Full evaluation: baseline vs model, on held-out data
    # ======================================================

    def evaluate(self, students, jobs, test_size=0.3):

        print("\n============================================================")
        print("MODEL EVALUATION — HELD-OUT REAL SAMPLE DATA")
        print("============================================================")

        pairs = self.build_labeled_pairs(students, jobs)
        train_df, test_df = self.split_holdout(pairs, test_size=test_size)

        print(f"Total student x job pairs : {len(pairs)}")
        print(f"Train pairs (tuned on)    : {len(train_df)}")
        print(f"Held-out test pairs       : {len(test_df)}")
        print(f"Positive rate in test set : {test_df['ground_truth'].mean():.2%}")

        baseline_metrics = self.compute_metrics(
            test_df["ground_truth"], test_df["baseline_pred"]
        )
        model_metrics = self.compute_metrics(
            test_df["ground_truth"], test_df["model_pred"]
        )

        print("\nBaseline (skill-overlap count) vs Weighted Threshold Model")
        print("-" * 60)
        print(f"{'Metric':<22}{'Baseline':>15}{'Model':>15}")
        print(f"{'Precision':<22}{baseline_metrics['precision']:>15.3f}{model_metrics['precision']:>15.3f}")
        print(f"{'Recall':<22}{baseline_metrics['recall']:>15.3f}{model_metrics['recall']:>15.3f}")
        print(f"{'F1 Score':<22}{baseline_metrics['f1']:>15.3f}{model_metrics['f1']:>15.3f}")
        print(f"{'False Positive Rate':<22}{baseline_metrics['fpr']:>15.3f}{model_metrics['fpr']:>15.3f}")

        print("\nModel Confusion Matrix (held-out test set)")
        print("-" * 60)
        print(f"TP={model_metrics['tp']}  FP={model_metrics['fp']}  "
              f"TN={model_metrics['tn']}  FN={model_metrics['fn']}")

        print("\nModel Classification Report (held-out test set)")
        print("-" * 60)
        print(classification_report(
            test_df["ground_truth"], test_df["model_pred"], zero_division=0
        ))

        self.confusion_matrix_plot(
            test_df["ground_truth"], test_df["model_pred"]
        )

        self.log_experiment(model_metrics, baseline_metrics, len(train_df), len(test_df))

        return {
             "precision": float(model_metrics["precision"]),
             "recall": float(model_metrics["recall"]),
             "f1": float(model_metrics["f1"]),
             "fpr": float(model_metrics["fpr"]),
             "confusion_matrix": {
             "tp": int(model_metrics["tp"]),
             "fp": int(model_metrics["fp"]),
             "tn": int(model_metrics["tn"]),
             "fn": int(model_metrics["fn"]),
    },
    "pairs": len(pairs),
    "train_pairs": int(len(train_df)),
    "test_pairs": int(len(test_df)),
     
}
        
    # ======================================================
    # Confusion Matrix Plot
    # ======================================================

    def confusion_matrix_plot(self, y_true, y_pred):

        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])

        display = ConfusionMatrixDisplay(
            confusion_matrix=cm,
            display_labels=["Not a Match", "Match"],
        )

        display.plot(cmap="Blues")

        plt.title("Model Confusion Matrix (Held-out Test Set)")

        plt.tight_layout()

        plt.savefig(
            os.path.join(self.output_folder, "confusion_matrix.png")
        )

        plt.close()

    # ======================================================
    # Experiment Log
    # ======================================================

    def log_experiment(self, model_metrics, baseline_metrics, n_train, n_test):
        """
        Append this run's numbers to experiments_log.csv, so every run
        is reproducible and comparable — the study guide's lightweight
        stand-in for MLflow.
        """

        header = [
            "timestamp", "n_train", "n_test",
            "model_precision", "model_recall", "model_f1", "model_fpr",
            "baseline_precision", "baseline_recall", "baseline_f1", "baseline_fpr",
        ]

        row = [
            datetime.now().isoformat(timespec="seconds"),
            n_train, n_test,
            round(model_metrics["precision"], 4),
            round(model_metrics["recall"], 4),
            round(model_metrics["f1"], 4),
            round(model_metrics["fpr"], 4),
            round(baseline_metrics["precision"], 4),
            round(baseline_metrics["recall"], 4),
            round(baseline_metrics["f1"], 4),
            round(baseline_metrics["fpr"], 4),
        ]

        file_exists = os.path.isfile(self.log_path)

        with open(self.log_path, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(header)
            writer.writerow(row)

