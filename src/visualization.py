import os
import matplotlib.pyplot as plt

from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay


class Visualizer:
    """
    NOTE (Task 3 fix): candidate_ranking(), match_score_distribution()
    and skill_gap() were previously empty stubs (`pass`) even though
    main.py called them and plots/ already contained PNGs from an
    earlier run. That's the exact "looks done but isn't" pattern the
    study guide warns about — the files existed, but the code that was
    supposed to produce them didn't run. All four plotting methods
    below are now real.
    """

    def __init__(self):
        self.output_folder = "plots"
        os.makedirs(self.output_folder, exist_ok=True)

    # -------------------------------------------------------
    # Threshold Validation Chart
    # -------------------------------------------------------

    def threshold_validation(self, validation):

        labels = list(validation.keys())

        values = [
            100 if value else 0
            for value in validation.values()
        ]

        plt.figure(figsize=(8, 5))

        plt.barh(labels, values, color=["#2e7d32" if v else "#c62828" for v in values])

        plt.xlim(0, 100)
        plt.xlabel("Validation (%)")
        plt.title("Threshold Validation")

        for i, value in enumerate(values):
            plt.text(value + 2, i, f"{value}%", va="center")

        plt.tight_layout()

        plt.savefig(os.path.join(self.output_folder, "threshold_validation.png"))
        plt.close()

    # -------------------------------------------------------
    # Candidate Ranking (job -> students)
    # -------------------------------------------------------

    def candidate_ranking(self, ranking, top_n=10, job_label=""):
        """Bar chart of the top-N ranked candidates' match scores."""

        top = ranking.head(top_n).iloc[::-1]  # reverse so #1 is on top

        colors = ["#1565c0" if s >= 60 else "#9e9e9e" for s in top["Score"]]

        plt.figure(figsize=(8, max(4, 0.5 * len(top))))

        plt.barh(top["Student"], top["Score"], color=colors)

        plt.xlim(0, 100)
        plt.xlabel("Match Score")
        title = "Candidate Ranking — Top Students"
        if job_label:
            title += f" for {job_label}"
        plt.title(title)

        for i, score in enumerate(top["Score"]):
            plt.text(score + 1, i, f"{score:.1f}", va="center", fontsize=8)

        plt.tight_layout()

        plt.savefig(os.path.join(self.output_folder, "candidate_ranking.png"))
        plt.close()

    # -------------------------------------------------------
    # Job Ranking (student -> jobs)   [Task 3 — new]
    # -------------------------------------------------------

    def job_ranking(self, ranking, top_n=10, student_label=""):
        """Bar chart of the top-N ranked jobs' match scores for a student."""

        top = ranking.head(top_n).iloc[::-1]

        labels = [f"{c} — {r}" for c, r in zip(top["Company"], top["Role"])]
        colors = ["#2e7d32" if s >= 60 else "#9e9e9e" for s in top["Score"]]

        plt.figure(figsize=(9, max(4, 0.5 * len(top))))

        plt.barh(labels, top["Score"], color=colors)

        plt.xlim(0, 100)
        plt.xlabel("Match Score")
        title = "Job Ranking — Top Jobs"
        if student_label:
            title += f" for {student_label}"
        plt.title(title)

        for i, score in enumerate(top["Score"]):
            plt.text(score + 1, i, f"{score:.1f}", va="center", fontsize=8)

        plt.tight_layout()

        plt.savefig(os.path.join(self.output_folder, "job_ranking.png"))
        plt.close()

    # -------------------------------------------------------
    # Match Score Distribution
    # -------------------------------------------------------

    def match_score_distribution(self, scores):
        """
        Histogram of match scores. Accepts either a ranking DataFrame
        with a "Score" column, or a raw list/Series of scores (e.g. the
        held-out test set's model_score column) — the latter gives a
        far more informative picture since it spans many student x job
        pairs rather than one job's candidate pool.
        """

        if hasattr(scores, "columns") and "Score" in getattr(scores, "columns", []):
            values = scores["Score"]
        else:
            values = scores

        plt.figure(figsize=(8, 5))

        plt.hist(values, bins=20, color="#5e35b1", edgecolor="white")

        plt.axvline(60, color="#c62828", linestyle="--", linewidth=1, label="Good Match cutoff (60)")

        plt.xlabel("Match Score")
        plt.ylabel("Number of Student–Job Pairs")
        plt.title("Match Score Distribution")
        plt.legend()

        plt.tight_layout()

        plt.savefig(os.path.join(self.output_folder, "match_score_distribution.png"))
        plt.close()

    # -------------------------------------------------------
    # Skill Gap (one student-job walkthrough pair)
    # -------------------------------------------------------

    def skill_gap(self, features, pair_label=""):

        gap_keys = [
            "Python Gap",
            "SQL Gap",
            "ML Gap",
            "Communication Gap",
            "CGPA Difference",
            "Experience Difference",
        ]

        labels = [k for k in gap_keys if k in features]
        values = [features[k] for k in labels]
        colors = ["#2e7d32" if v >= 0 else "#c62828" for v in values]

        plt.figure(figsize=(8, 5))

        plt.barh(labels, values, color=colors)

        plt.axvline(0, color="black", linewidth=0.8)
        plt.xlabel("Student value minus Job requirement (positive = exceeds requirement)")
        title = "Skill Gap Analysis"
        if pair_label:
            title += f" — {pair_label}"
        plt.title(title)

        plt.tight_layout()

        plt.savefig(os.path.join(self.output_folder, "skill_gap.png"))
        plt.close()

    # -------------------------------------------------------
    # Confusion Matrix
    # -------------------------------------------------------

    def confusion_matrix_plot(self, y_true, y_pred):

        cm = confusion_matrix(y_true, y_pred)

        ConfusionMatrixDisplay(confusion_matrix=cm).plot()

        plt.title("Confusion Matrix")

        plt.savefig(os.path.join(self.output_folder, "confusion_matrix.png"))
        plt.close()
