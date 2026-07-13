import os
import matplotlib.pyplot as plt

from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay


class Visualizer:

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

        plt.barh(labels, values)

        plt.xlim(0, 100)

        plt.xlabel("Validation (%)")

        plt.title("Threshold Validation")

        for i, value in enumerate(values):
            plt.text(
                value + 2,
                i,
                f"{value}%",
                va="center"
            )

        plt.tight_layout()

        plt.savefig(
            os.path.join(
                self.output_folder,
                "threshold_validation.png"
            )
        )

        plt.show()
    def candidate_ranking(self, ranking):
        pass

    def match_score_distribution(self, ranking):
        pass

    def skill_gap(self, features):
        pass

    def confusion_matrix_plot(self, y_true, y_pred):

        cm = confusion_matrix(y_true, y_pred)

        ConfusionMatrixDisplay(
            confusion_matrix=cm
        ).plot()

        plt.title("Confusion Matrix")

        plt.savefig(
            os.path.join(
                self.output_folder,
                "confusion_matrix.png"
            )
        )

        plt.show()