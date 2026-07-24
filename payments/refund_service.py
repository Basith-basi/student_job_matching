import sqlite3

DATABASE = "student_job_matching.db"


class RefundService:

    def refund(self, transaction_id):

        conn = sqlite3.connect(DATABASE)

        conn.execute(
            """
            UPDATE payments
            SET payment_status='REFUNDED'
            WHERE transaction_id=?
            """,
            (transaction_id,)
        )

        conn.commit()

        conn.close()

        return {
            "message": "Refund Successful"
        }