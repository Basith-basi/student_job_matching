class PaymentFailureHandler:

    def payment_failed(self, status="FAILED"):

        return {

            "application_created": False,

            "payment_status": status,

            "success": False,

            "message": "Payment failed",

            "money_deducted": False,

            "application_saved": False

        }