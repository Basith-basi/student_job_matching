import sqlite3

DATABASE = "student_job_matching.db"


class ReceiptService:

    def generate_receipt(self, transaction_id):

        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row

        payment = conn.execute(

            """
            SELECT *
            FROM payments
            WHERE transaction_id=?
            """,

            (transaction_id,)

        ).fetchone()

        conn.close()

        if payment is None:
            return None

        return {

            "Receipt ID": payment["payment_id"],

            "Student": payment["student_name"],

            "Company": payment["company"],

            "Job": payment["job_id"],

            "Amount": payment["amount"],

            "Status": payment["payment_status"],

            "Transaction": payment["transaction_id"],

            "Date": payment["payment_date"]
        }