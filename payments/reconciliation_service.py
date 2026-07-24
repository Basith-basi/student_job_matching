import sqlite3

DATABASE = "student_job_matching.db"


class ReconciliationService:

    def generate_report(self):

        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
        SELECT
            COUNT(*) as total_transactions,
            SUM(amount) as total_amount
        FROM payments
        WHERE payment_status='SUCCESS'
        """)

        payments = dict(cursor.fetchone())

        cursor.execute("""
        SELECT
            COUNT(*) as refunded_transactions,
            SUM(amount) as refunded_amount
        FROM payments
        WHERE payment_status='REFUNDED'
        """)

        refunds = dict(cursor.fetchone())

        conn.close()

        return {
            "payments": payments,
            "refunds": refunds,
            "difference":
                (payments["total_amount"] or 0) -
                (refunds["refunded_amount"] or 0)
        }