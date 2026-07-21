import uuid
import random


class PaymentGateway:
    """
    Simulates an online payment gateway.
    """

    def __init__(self):
        pass

    def process_payment(self, amount: float):
        """
        Simulate payment processing.
        """

        transaction_id = str(uuid.uuid4())

        status = random.choice([
            "SUCCESS",
            "FAILED",
            "PENDING"
        ])

        return {
            "transaction_id": transaction_id,
            "amount": amount,
            "status": status
        }