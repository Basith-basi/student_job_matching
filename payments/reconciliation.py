import sqlite3

DATABASE = "student_job_matching.db"


class Reconciliation:

    def summary(self):

        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        total = cursor.execute(
            "SELECT COUNT(*) FROM payments"
        ).fetchone()[0]

        success = cursor.execute(
            "SELECT COUNT(*) FROM payments WHERE payment_status='SUCCESS'"
        ).fetchone()[0]

        refunded = cursor.execute(
            "SELECT COUNT(*) FROM payments WHERE payment_status='REFUNDED'"
        ).fetchone()[0]

        conn.close()

        return {

            "total_transactions": total,

            "successful": success,

            "refunded": refunded
        }