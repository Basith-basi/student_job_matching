import sqlite3

DATABASE = "student_job_matching.db"


class RetryPayment:

    def retry(self):

        conn = sqlite3.connect(DATABASE)

        cursor = conn.cursor()

        transaction_id = "TXN_RETRY_001"

        cursor.execute("""
        INSERT INTO payment_attempts
        (transaction_id,status,attempt)
        VALUES(?,?,?)
        """,
        (
            transaction_id,
            "SUCCESS",
            1
        ))

        conn.commit()

        conn.close()

        return {

            "attempt": 1,

            "transaction_id": transaction_id,

            "status": "Retry Successful"

        }