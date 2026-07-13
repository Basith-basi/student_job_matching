from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix


class Evaluator:

    def evaluate(

        self,

        y_true,

        y_pred

    ):

        print("Precision :",

              precision_score(

                  y_true,

                  y_pred

              ))

        print("Recall :", recall_score(

            y_true,

            y_pred

        ))

        print("F1 Score :", f1_score(

            y_true,

            y_pred

        ))

        print(

            "Confusion Matrix"

        )

        print(

            confusion_matrix(

                y_true,

                y_pred

            )

        )