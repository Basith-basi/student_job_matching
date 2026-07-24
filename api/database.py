import sqlite3

DATABASE = "student_job_matching.db"


# --------------------------------------------------
# Get Database Connection
# --------------------------------------------------
def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------
# Create Database & Tables
# --------------------------------------------------
def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------------------
    # JOBS TABLE
    # --------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (

    job_id INTEGER PRIMARY KEY,

    company TEXT,

    role TEXT,

    skills TEXT,

    Python_Threshold INTEGER,

    SQL_Threshold INTEGER,

    ML_Threshold INTEGER,

    Communication_Threshold INTEGER,

    Experience_Threshold INTEGER,

    Minimum_CGPA REAL

)
""")
    # --------------------------------------------------
    # STUDENTS TABLE
    # --------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY,
        student_name TEXT NOT NULL,
        skills TEXT,
        cgpa REAL,
        experience INTEGER,
        communication INTEGER
    )
    """)

    # --------------------------------------------------
    # APPLICATIONS TABLE
    # --------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        application_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        job_id INTEGER,
        score REAL,
        status TEXT,

        FOREIGN KEY(student_id) REFERENCES students(student_id),
        FOREIGN KEY(job_id) REFERENCES jobs(job_id)
    )
    """)

  
     # Predictions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (

        prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,

        student_id INTEGER NOT NULL,

        job_id INTEGER NOT NULL,

        match_score REAL NOT NULL,

        recommendation TEXT NOT NULL,

        status TEXT NOT NULL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(student_id) REFERENCES students(student_id),

        FOREIGN KEY(job_id) REFERENCES jobs(job_id)

    )
    """)

    # Payments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (

        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,

        student_name TEXT,

        company TEXT NOT NULL,

        job_id INTEGER NOT NULL,
                   
        plan TEXT,          

        amount REAL NOT NULL,

        payment_status TEXT NOT NULL,

        transaction_id TEXT UNIQUE NOT NULL,

        payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(job_id) REFERENCES jobs(job_id)

    )
    """)

    
    cursor.execute("""
CREATE TABLE IF NOT EXISTS receipts (
    receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT,
    student_name TEXT,
    company TEXT,
    amount REAL,
    status TEXT
)
""")
    

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS refunds(

        refund_id INTEGER PRIMARY KEY AUTOINCREMENT,

        payment_id INTEGER,

        reason TEXT,

        amount REAL,

        refund_status TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
          """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reconciliation(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        payment_id INTEGER,

        gateway_amount REAL,
        
        database_amount REAL,

        status TEXT,

        checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payment_attempts(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    transaction_id TEXT,

    status TEXT,

    attempt INTEGER

)
""")
    
    conn.commit()
    conn.close()


def seed_jobs_from_csv(csv_path="data/jobs.csv"):
    """Seed jobs table from CSV if table is empty."""
    import pandas as pd
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    if count > 0:
        conn.close()
        return
    try:
        jobs = pd.read_csv(csv_path)
        for _, row in jobs.iterrows():
            conn.execute("""INSERT OR IGNORE INTO jobs
                (job_id, company, role, skills, Python_Threshold, SQL_Threshold, ML_Threshold, Communication_Threshold, Experience_Threshold, Minimum_CGPA)
                VALUES (?, ?, ?, '', ?, ?, ?, ?, ?, ?)""",
                (int(row["Job_ID"]), row["Company"], row["Role"],
                 int(row["Python_Threshold"]), int(row["SQL_Threshold"]), int(row["ML_Threshold"]),
                 int(row["Communication_Threshold"]), int(row["Experience_Threshold"]), float(row["Minimum_CGPA"])))
        conn.commit()
    except FileNotFoundError:
        pass
    finally:
        conn.close()


# Auto-initialize tables and seed data on module import
create_database()
seed_jobs_from_csv()

if __name__ == "__main__":
    pass