import uuid
import random

class PaymentGateway:

    def process_payment(self, student_id, job_id, amount=100):

        success = random.choice([True, True, True, False])

        if success:
            return {
                "status": "SUCCESS",
                "transaction_id": str(uuid.uuid4()),
                "amount": amount
            }

        return {
            "status": "FAILED",
            "transaction_id": None,
            "amount": amount
        }