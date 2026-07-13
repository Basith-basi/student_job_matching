import os
import matplotlib.pyplot as plt

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay,
    RocCurveDisplay
)


class Evaluator:

    def __init__(self):

        self.output_folder = "plots"

        os.makedirs(
            self.output_folder,
            exist_ok=True
        )

    # ======================================================
    # Model Evaluation
    # ======================================================

    def evaluate(
        self,
        y_true,
        y_pred
    ):

        print("\n============================================================")
        print("MODEL EVALUATION")
        print("============================================================")

        # ----------------------------
        # Metrics
        # ----------------------------

        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)

        print(f"Precision            : {precision:.2f}")
        print(f"Recall               : {recall:.2f}")
        print(f"F1 Score             : {f1:.2f}")

        # ----------------------------
        # Confusion Matrix (Text)
        # ----------------------------

        print("\nConfusion Matrix")
        print("----------------------------------------")
        print(confusion_matrix(y_true, y_pred))

        # ----------------------------
        # Classification Report
        # ----------------------------

        print("\nClassification Report")
        print("----------------------------------------")

        print(
            classification_report(
                y_true,
                y_pred
            )
        )

        # ----------------------------
        # Save Confusion Matrix Plot
        # ----------------------------

        self.confusion_matrix_plot(
            y_true,
            y_pred
        )

    # ======================================================
    # Confusion Matrix Plot
    # ======================================================

    def confusion_matrix_plot(
        self,
        y_true,
        y_pred
    ):

        cm = confusion_matrix(
            y_true,
            y_pred
        )

        display = ConfusionMatrixDisplay(
            confusion_matrix=cm
        )

        display.plot()

        plt.title("Confusion Matrix")

        plt.savefig(
            os.path.join(
                self.output_folder,
                "confusion_matrix.png"
            )
        )

        plt.show()

    # ======================================================
    # ROC Curve (Optional)
    # ======================================================

    def roc_curve_plot(
        self,
        y_true,
        y_scores
    ):

        RocCurveDisplay.from_predictions(
            y_true,
            y_scores
        )

        plt.title("ROC Curve")

        plt.savefig(
            os.path.join(
                self.output_folder,
                "roc_curve.png"
            )
        )

        plt.show()