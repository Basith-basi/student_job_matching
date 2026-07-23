from src.database import Database
from src.payment import PaymentGateway
from src.matching import JobMatcher

class ApplicationService:

    def __init__(self):

        self.db = Database()
        self.payment = PaymentGateway()
        self.matcher = JobMatcher()

    def apply(self, student, job):

        student_id = student["Student_ID"]
        job_id = job["Job_ID"]

        payment = self.payment.process_payment(student_id, job_id)

        if payment["status"] == "SUCCESS":

            score, recommendation, _ = self.matcher.calculate_match_score(student, job)

            self.db.save_application(
                student_id,
                job_id,
                "SUCCESS",
                payment["amount"],
                payment["transaction_id"],
                score,
                recommendation
            )

            print("Application Submitted Successfully")

        else:

            print("Payment Failed")
            print("Application Cancelled")
            