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

    # -------------------------------
    # Drop old tables (Development)
    # -------------------------------
    cursor.execute("DROP TABLE IF EXISTS jobs")
    cursor.execute("DROP TABLE IF EXISTS students")
    cursor.execute("DROP TABLE IF EXISTS applications")
    cursor.execute("DROP TABLE IF EXISTS predictions")

    # --------------------------------------------------
    # JOBS TABLE
    # --------------------------------------------------
    cursor.execute("""
    CREATE TABLE jobs (
        job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    skills TEXT,
    min_cgpa REAL,
    min_experience INTEGER
    )
    """)

    # --------------------------------------------------
    # STUDENTS TABLE
    # --------------------------------------------------
    cursor.execute("""
    CREATE TABLE students (
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
    CREATE TABLE applications (
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

    print("Database created successfully.")


if __name__ == "__main__":
    create_database()