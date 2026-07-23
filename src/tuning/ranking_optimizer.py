import os
import json
import math

import pandas as pd

from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

from src.threshold_validation import ThresholdValidator
from src.tuning.threshold_optimizer import ThresholdOptimizer


class RankingOptimizer:
    """
    Tunes the weights used to combine the project's six real matching
    features into a single "Final Score" for candidate ranking:

        Python, SQL, Machine Learning, Communication, Experience, CGPA

    This class sweeps weight combinations across those six features,
    evaluates each on real precision / recall / F1 / FPR against the
    same ground-truth definition used elsewhere in the project
    (ThresholdValidator), logs every combo, and picks the best one.

    IMPORTANT — column names:
    JobMatcher only exposes calculate_match_score() and
    get_recommendation(); it has no per-feature scorers. So this class
    reads the six raw values straight off the student/job rows and
    computes each feature's match score itself, as:

        match_score = min(student_value / job_requirement, 1.0) * 100

    That ratio is scale-independent by construction — it works the
    same whether the underlying field is "Python = 85" (out of 100),
    "Experience = 2" (years), or "CGPA = 8.2" (out of 10) — so no
    hardcoded max-value constants are needed (see class docstring
    Problem 3 in review notes).

    STUDENT_COLUMNS / JOB_COLUMNS below map each of the six features
    to the actual column names in your student_df / job_df. Update
    these two dicts to match your real CSV headers — everything else
    in this class is written against the feature names in FEATURES,
    not the raw column names, so no other code needs to change.

    Pipeline:
      1. extract_features()      -> six match scores + ground truth
                                     for every student x job pair
      2. generate_weight_grid()  -> programmatically build many valid
                                     weight combinations (Step 5.4)
      3. run_experiments()       -> sweep the grid, log each combo to
                                     outputs/ranking_experiments.csv
      4. select_best()           -> pick the strongest combo, save to
                                     outputs/best_weights.json
      5. optimize()              -> convenience wrapper for 3 + 4
    """

    # The six real features used across the project.
    FEATURES = [
        "python",
        "sql",
        "ML",
        "communication",
        "experience",
        "cgpa",
    ]

    # Map each feature -> the student's raw column name.
    # >>> Update these to match your actual student dataframe headers. <<<
    STUDENT_COLUMNS = {
        "python": "Python",
        "sql": "SQL",
        "ML": "Machine Learning",
        "communication": "Communication",
        "experience": "Experience",
        "cgpa": "CGPA",
    }

    # Map each feature -> the job's raw "required" column name.
    # >>> Update these to match your actual job dataframe headers. <<<
    JOB_COLUMNS = {
        "python": "Python_Threshold",
        "sql": "SQL_Threshold",
        "ML": "ML_Threshold",
        "communication": "Communication_Threshold",
        "experience": "Experience_Threshold",
        "cgpa": "Minimum_CGPA",
    }

    def __init__(self, threshold=None, output_folder="outputs"):
        self.validator = ThresholdValidator()

        # Connect to the already-tuned match threshold (Task 7 /
        # Step 4) instead of hardcoding one, so threshold optimization
        # and ranking-weight optimization stay in sync. Pass an
        # explicit `threshold=` only if you deliberately want to test
        # against a fixed cutoff instead of the tuned one.
        if threshold is None:
            self.threshold = ThresholdOptimizer().load_best_threshold()
        else:
            self.threshold = threshold

        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)

        self.experiments_path = os.path.join(self.output_folder, "ranking_experiments.csv")
        self.best_weights_path = os.path.join(self.output_folder, "best_weights.json")

    # ======================================================
    # Step 5.2 — extract per-feature match scores
    # ======================================================
    @staticmethod
    def _feature_match_score(student_value, job_value):
        """
        Scale-independent match score for one feature on one
        student x job pair: what fraction of the job's requirement
        does the student meet, capped at 100%.

        Handles missing/zero requirements by treating "no requirement"
        as fully satisfied (100), and missing student values as 0.
        """
        if pd.isna(job_value) or job_value == 0:
            return 100.0

        if pd.isna(student_value):
            return 0.0

        ratio = student_value / job_value
        return float(min(ratio, 1.0) * 100)

    def extract_features(self, students, jobs):
        """
        Cross-join students and jobs and compute the six match scores
        (0-100 each) for every pair, plus the ground-truth label from
        ThresholdValidator (same "clears every minimum threshold"
        definition used by Evaluator).
        """
        rows = []

        for _, student in students.iterrows():
            for _, job in jobs.iterrows():

                feature_scores = {}
                for feature in self.FEATURES:
                    student_col = self.STUDENT_COLUMNS[feature]
                    job_col = self.JOB_COLUMNS[feature]

                    student_value = student.get(student_col)
                    job_value = job.get(job_col)

                    feature_scores[feature] = self._feature_match_score(
                        student_value, job_value
                    )

                validation = self.validator.validate(student, job)
                ground_truth = 1 if all(validation.values()) else 0

                row = {
                    "Student_ID": student["Student_ID"],
                    "Job_ID": job["Job_ID"],
                    "ground_truth": ground_truth,
                }
                row.update(feature_scores)
                rows.append(row)

        return pd.DataFrame(rows)

    # ======================================================
    # Step 5.5 — recompute Final Score for a given weight combo
    # ======================================================
    def score_with_weights(self, features_df, weights):
        score = 0
        for feature in self.FEATURES:
            score = score + features_df[feature] * weights[feature]
        return score

    # ======================================================
    # Step 5.6 — Prediction -> Threshold -> Evaluation for one combo
    # ======================================================
    def evaluate_weights(self, features_df, weights):
        scores = self.score_with_weights(features_df, weights)
        preds = (scores >= self.threshold).astype(int)

        y_true = features_df["ground_truth"]

        cm = confusion_matrix(y_true, preds, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()

        precision = precision_score(y_true, preds, zero_division=0)
        recall = recall_score(y_true, preds, zero_division=0)
        f1 = f1_score(y_true, preds, zero_division=0)
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "fpr": fpr,
            "tp": int(tp),
            "fp": int(fp),
            "tn": int(tn),
            "fn": int(fn),
        }

    # ======================================================
    # Step 5.4 — programmatically generate weight combinations
    # ======================================================
    def generate_weight_grid(self, step=0.1, min_weight=None):
        """
        Enumerate every valid combination of the six weights, at a
        given step size, where each weight is >= min_weight and all
        six sum to exactly 1.0.

        This replaces a short hand-picked list with a full sweep of
        the weight space, so "tune the weights" (Task 7) isn't limited
        to 5 guesses. Runtime is cheap even for large grids, because
        extract_features() only runs once per call to run_experiments()
        — each combo just re-weights the already-computed feature
        scores (vectorized pandas ops).

        step=0.1 (default) with min_weight defaulting to `step` -> 126
        combos. Lower `step` for a finer sweep — the combo count grows
        fast (compositions of 1/step into 6 positive parts), so check
        len(grid) before running it on a large student x job dataset.
        """
        if min_weight is None:
            min_weight = step

        units = round(1.0 / step)
        # ceil (with a small epsilon) instead of round: round() uses
        # banker's rounding, so round(0.05 / 0.1) == 0, which would
        # silently disable the min_weight floor entirely.
        min_units = max(1, math.ceil(min_weight / step - 1e-9))
        n_features = len(self.FEATURES)

        compositions = []

        def recurse(remaining_features, remaining_units, current):
            if remaining_features == 1:
                if remaining_units >= min_units:
                    compositions.append(current + [remaining_units])
                return

            max_u = remaining_units - min_units * (remaining_features - 1)
            for u in range(min_units, max_u + 1):
                recurse(remaining_features - 1, remaining_units - u, current + [u])

        recurse(n_features, units, [])

        weight_grid = []
        for combo in compositions:
            weights = {
                feature: round(units_i * step, 4)
                for feature, units_i in zip(self.FEATURES, combo)
            }
            weight_grid.append(weights)

        return weight_grid

    # ======================================================
    # Step 5.4 + 5.7 — sweep the weight grid, log every combo
    # ======================================================
    def run_experiments(self, students, jobs, weight_grid=None, verbose=None):
        weight_grid = weight_grid or self.generate_weight_grid()

        # Auto-quiet per-combo logging once the grid gets large, so a
        # 300-combo sweep doesn't flood stdout.
        if verbose is None:
            verbose = len(weight_grid) <= 30

        features_df = self.extract_features(students, jobs)

        print("\n============================================================")
        print("RANKING WEIGHT OPTIMIZATION")
        print("============================================================")
        print(f"Total student x job pairs : {len(features_df)}")
        print(f"Positive rate             : {features_df['ground_truth'].mean():.2%}")
        print(f"Score threshold used      : {self.threshold}")
        print(f"Weight combinations       : {len(weight_grid)}\n")

        results = []

        for weights in weight_grid:

            missing = [f for f in self.FEATURES if f not in weights]
            if missing:
                print(f"Skipping {weights} — missing weight(s) for {missing}")
                continue

            total = sum(weights[f] for f in self.FEATURES)
            if abs(total - 1.0) > 1e-6:
                print(f"Skipping {weights} — weights sum to {total:.3f}, not 1.0")
                continue

            metrics = self.evaluate_weights(features_df, weights)

            if verbose:
                weight_str = "  ".join(f"{f}={weights[f]:.2f}" for f in self.FEATURES)
                print(
                    f"{weight_str}  |  "
                    f"P={metrics['precision']:.3f} "
                    f"R={metrics['recall']:.3f} "
                    f"F1={metrics['f1']:.3f} "
                    f"FPR={metrics['fpr']:.3f}"
                )

            row = {f: weights[f] for f in self.FEATURES}
            row.update({
                "precision": round(metrics["precision"], 4),
                "recall": round(metrics["recall"], 4),
                "f1": round(metrics["f1"], 4),
                "fpr": round(metrics["fpr"], 4),
                "tp": metrics["tp"],
                "fp": metrics["fp"],
                "tn": metrics["tn"],
                "fn": metrics["fn"],
            })
            results.append(row)

        results_df = pd.DataFrame(results)

        if not verbose and not results_df.empty:
            print("Top 5 combinations by F1:")
            top5 = results_df.sort_values("f1", ascending=False).head(5)
            print(top5[self.FEATURES + ["precision", "recall", "f1", "fpr"]]
                  .to_string(index=False))

        self._save_experiments(results_df)

        return results_df

    def _save_experiments(self, results_df):
        results_df.to_csv(self.experiments_path, index=False)
        print(f"\nSaved experiment log -> {self.experiments_path}")

    # ======================================================
    # Step 5.8 — choose the best combination
    # ======================================================
    def select_best(self, results_df, min_precision=0.0, max_fpr=1.0):
        """
        Best combo = highest F1 among combos that meet the precision
        floor and FPR ceiling (both optional). Ties broken by
        precision, then by lowest FPR.
        """
        if results_df.empty:
            raise ValueError("No experiment results to select from — "
                              "did every weight combo fail to sum to 1.0?")

        candidates = results_df[
            (results_df["precision"] >= min_precision)
            & (results_df["fpr"] <= max_fpr)
        ]

        if candidates.empty:
            print("\nNo combination met the precision/FPR constraints; "
                  "selecting best F1 from all combinations instead.")
            candidates = results_df

        best_row = candidates.sort_values(
            by=["f1", "precision", "fpr"],
            ascending=[False, False, True]
        ).iloc[0]

        best_weights = {feature: float(best_row[feature]) for feature in self.FEATURES}

        print("\nBest weight combination:")
        print(json.dumps(best_weights, indent=4))
        print(
            f"Precision={best_row['precision']:.3f}  "
            f"Recall={best_row['recall']:.3f}  "
            f"F1={best_row['f1']:.3f}  "
            f"FPR={best_row['fpr']:.3f}"
        )

        with open(self.best_weights_path, "w") as f:
            json.dump(best_weights, f, indent=4)

        print(f"Saved best weights -> {self.best_weights_path}")

        return best_weights

    # ======================================================
    # Convenience: run the whole Step 5 pipeline in one call
    # ======================================================
    def optimize(self, students, jobs, weight_grid=None,
                 min_precision=0.0, max_fpr=1.0):
        """
        Runs Steps 5.4 - 5.8 end to end:
        sweep weights -> log experiments -> pick + save the best combo.
        """
        results_df = self.run_experiments(students, jobs, weight_grid=weight_grid)
        best_weights = self.select_best(
            results_df, min_precision=min_precision, max_fpr=max_fpr
        )
        return best_weights, results_df


if __name__ == "__main__":
    # Example usage — swap in your real student/job loading logic.
    #
    # from src.data_loader import load_students, load_jobs
    # students = load_students()
    # jobs = load_jobs()
    #
    # optimizer = RankingOptimizer()  # threshold auto-loaded from ThresholdOptimizer
    # best_weights, results_df = optimizer.optimize(students, jobs)
    #
    # Or run a coarser/finer sweep explicitly:
    # grid = optimizer.generate_weight_grid(step=0.05, min_weight=0.05)
    # best_weights, results_df = optimizer.optimize(students, jobs, weight_grid=grid)
    pass
