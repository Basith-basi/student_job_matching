import sqlite3
import os

DB_FOLDER = "database"
DB_NAME = "job_matching.db"

os.makedirs(DB_FOLDER, exist_ok=True)

DB_PATH = os.path.join(DB_FOLDER, DB_NAME)


class Database:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (

            application_id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id INTEGER NOT NULL,

            job_id INTEGER NOT NULL,

            payment_status TEXT NOT NULL,

            amount REAL NOT NULL,

            transaction_id TEXT,

            match_score REAL,

            recommendation TEXT,

            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)

        self.conn.commit()

    def save_application(
        self,
        student_id,
        job_id,
        payment_status,
        amount,
        transaction_id,
        match_score,
        recommendation
    ):

        self.cursor.execute("""
        INSERT INTO applications
        (
            student_id,
            job_id,
            payment_status,
            amount,
            transaction_id,
            match_score,
            recommendation
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            student_id,
            job_id,
            payment_status,
            amount,
            transaction_id,
            match_score,
            recommendation
        ))

        self.conn.commit()

    def get_all_applications(self):

        self.cursor.execute("SELECT * FROM applications")

        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
if __name__ == "__main__":
    db = Database()
    print("Database created successfully!")
    db.close()