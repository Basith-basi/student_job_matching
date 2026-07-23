"""Held-out evaluation and tuning evidence for Task 7."""

import csv
import json
from datetime import datetime
from itertools import product
from pathlib import Path

import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from src.baseline import BaselineRanker
from src.matching import DEFAULT_CONFIG_PATH, DEFAULT_WEIGHTS, FEATURES, JobMatcher
from src.threshold_validation import ThresholdValidator


class Evaluator:
    """Tune only on validation data, then report once on held-out test data."""

    def __init__(self, output_folder="outputs"):
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)
        self.validator = ThresholdValidator()
        self.baseline = BaselineRanker()

    def build_labeled_pairs(self, students, jobs):
        rows = []
        for _, student in students.iterrows():
            for _, job in jobs.iterrows():
                features = JobMatcher.feature_scores(student, job)
                rows.append({
                    "Student_ID": student["Student_ID"],
                    "Job_ID": job["Job_ID"],
                    "ground_truth": int(self.validator.validate(student, job)["passed"]),
                    "baseline_pred": self.baseline.predict(student, job, cutoff=50),
                    **features,
                })
        return pd.DataFrame(rows)

    @staticmethod
    def _split(frame, test_size, random_state):
        labels = frame["ground_truth"]
        stratify = labels if labels.nunique() > 1 and labels.value_counts().min() >= 2 else None
        return train_test_split(frame, test_size=test_size, random_state=random_state, stratify=stratify)

    @staticmethod
    def _metrics(y_true, predictions):
        tn, fp, fn, tp = confusion_matrix(y_true, predictions, labels=[0, 1]).ravel()
        return {
            "precision": float(precision_score(y_true, predictions, zero_division=0)),
            "recall": float(recall_score(y_true, predictions, zero_division=0)),
            "f1": float(f1_score(y_true, predictions, zero_division=0)),
            "fpr": float(fp / (fp + tn)) if fp + tn else 0.0,
            "confusion_matrix": {"tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn)},
        }

    @staticmethod
    def _weight_grid():
        # 126 positive, reproducible combinations in 0.1 increments.
        grid = []
        for values in product(range(1, 11), repeat=6):
            if sum(values) == 10:
                grid.append({feature: value / 10 for feature, value in zip(FEATURES, values)})
        return grid

    @staticmethod
    def _scores(frame, weights):
        return sum(frame[feature] * weights[feature] for feature in FEATURES)

    def _tune(self, validation):
        results = []
        for weights in self._weight_grid():
            scores = self._scores(validation, weights)
            for threshold in range(45, 91, 5):
                metrics = self._metrics(validation["ground_truth"], (scores >= threshold).astype(int))
                results.append({**weights, "threshold": threshold, **metrics, "confusion_matrix": json.dumps(metrics["confusion_matrix"])})
        results_df = pd.DataFrame(results)
        best = results_df.sort_values(["f1", "precision", "fpr"], ascending=[False, False, True]).iloc[0]
        return ({feature: float(best[feature]) for feature in FEATURES}, float(best["threshold"]), results_df)

    def evaluate(self, students, jobs, test_size=0.2, validation_size=0.25, random_state=42):
        pairs = self.build_labeled_pairs(students, jobs)
        train_validation, test = self._split(pairs, test_size, random_state)
        train, validation = self._split(train_validation, validation_size, random_state + 1)
        weights, threshold, experiments = self._tune(validation)

        model_predictions = (self._scores(test, weights) >= threshold).astype(int)
        model_metrics = self._metrics(test["ground_truth"], model_predictions)
        baseline_metrics = self._metrics(test["ground_truth"], test["baseline_pred"])

        config = {
            "weights": weights,
            "match_threshold": threshold,
            "selection_metric": "validation_f1_then_precision_then_lowest_fpr",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        with DEFAULT_CONFIG_PATH.open("w", encoding="utf-8") as file:
            json.dump(config, file, indent=2)

        experiments.drop(columns=["confusion_matrix"]).to_csv(self.output_folder / "ranking_experiments.csv", index=False)
        summary = {
            "data_split": {"train_pairs": len(train), "validation_pairs": len(validation), "test_pairs": len(test)},
            "selected_config": config,
            "baseline": baseline_metrics,
            "tuned_model": model_metrics,
        }
        with (self.output_folder / "evaluation_summary.json").open("w", encoding="utf-8") as file:
            json.dump(summary, file, indent=2)
        self._append_experiment(summary)
        return summary

    def _append_experiment(self, summary):
        path = Path("experiments_log.csv")
        header = ["timestamp", "train_pairs", "validation_pairs", "test_pairs", "precision", "recall", "f1", "fpr", "baseline_f1"]
        write_header = not path.exists() or path.stat().st_size == 0
        model = summary["tuned_model"]
        with path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if write_header:
                writer.writerow(header)
            writer.writerow([datetime.now().isoformat(timespec="seconds"), *summary["data_split"].values(), model["precision"], model["recall"], model["f1"], model["fpr"], summary["baseline"]["f1"]])
