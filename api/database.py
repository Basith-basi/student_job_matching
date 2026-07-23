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
    conn.commit()
    conn.close()


# Auto-initialize tables on module import
create_database()

if __name__ == "__main__":
    pass