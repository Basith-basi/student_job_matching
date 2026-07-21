"""
Payment Validation Module
"""


class PaymentValidator:
    """
    Validates payment requests.
    """

    def __init__(self):
        pass

    def validate(
        self,
        amount: float,
        plan: str,
        available_plans: dict,
        payment_exists: bool = False,
        payment_completed: bool = False
    ):
        """
        Validate payment request.
        """

        # Amount validation
        if amount <= 0:
            return False, "Amount must be greater than 0."

        # Plan validation
        if plan not in available_plans:
            return False, "Invalid subscription plan."

        # Duplicate payment
        if payment_exists:
            return False, "Duplicate payment detected."

        # Already paid
        if payment_completed:
            return False, "Payment already completed."

        return True, "Validation Successful"