import sqlite3

from payments.plans import PLANS
from payments.payment_gateway import PaymentGateway
from payments.payment_validator import PaymentValidator


DATABASE = "student_job_matching.db"


class PaymentService:
    """
    Handles complete payment workflow.
    """

    def __init__(self):

        self.gateway = PaymentGateway()
        self.validator = PaymentValidator()

    def process_payment(
        self,
        student_name: str,
        company: str,
        job_id: int,
        plan: str
    ):

        # -----------------------------
        # Check Plan
        # -----------------------------
        if plan not in PLANS:
            return {
                "success": False,
                "message": "Invalid Plan"
            }

        amount = PLANS[plan]["price"]

        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # -----------------------------
        # Check Duplicate Payment
        # -----------------------------
        cursor.execute(
            """
            SELECT *
            FROM payments
            WHERE student_name=?
            AND company=?
            AND job_id=?
            """,
            (
                student_name,
                company,
                job_id
            )
        )

        duplicate = cursor.fetchone()

        valid, message = self.validator.validate(
            amount=amount,
            plan=plan,
            available_plans=PLANS,
            payment_exists=duplicate is not None
        )

        if not valid:

            conn.close()

            return {
                "success": False,
                "message": message
            }
        print("Plan:", plan)
        print("Student:", student_name)
        print("Company:", company)
        print("Job:", job_id)

        # -----------------------------
        # Gateway
        # -----------------------------
        gateway_response = self.gateway.process_payment(amount)

        # -----------------------------
        # Save Payment
        # -----------------------------
        cursor.execute(
            """
            INSERT INTO payments
            (
                student_name,
                company,
                job_id,
                plan,
                amount,
                payment_status,
                transaction_id
            )
            VALUES
            (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student_name,
                company,
                job_id,
                plan,
                gateway_response["amount"],
                gateway_response["status"],
                gateway_response["transaction_id"]
            )
        )

        conn.commit()
        conn.close()

        return {
            "success": True,
            "student": student_name,
            "company": company,
            "job_id": job_id,
            "plan": plan,
            "amount": gateway_response["amount"],
            "status": gateway_response["status"],
            "transaction_id": gateway_response["transaction_id"]
        }

    def charge_application(self):
        """Charge the fixed Task 7 application amount through the test gateway.

        Persistence is deliberately handled by the application endpoint so the
        payment record and successful application are committed together.
        """
        return self.gateway.process_payment(100.0)
