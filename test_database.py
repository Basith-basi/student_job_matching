from src.database import Database

db = Database()

db.save_application(
    student_id=1,
    job_id=2,
    payment_status="SUCCESS",
    amount=100,
    transaction_id="TXN1001",
    match_score=92.5,
    recommendation="Excellent Match"
)

print(db.get_all_applications())

db.close()