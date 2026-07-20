import sqlite3

DATABASE = "student_job_matching.db"


# Returns a database connection
def get_connection():
    conn = sqlite3.connect("student_job_matching.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # --------------------------------------------------
    # JOBS TABLE
    # --------------------------------------------------
    cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    job_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    skills TEXT NOT NULL,

    Python_Threshold INTEGER NOT NULL,
    SQL_Threshold INTEGER NOT NULL,
    ML_Threshold INTEGER NOT NULL,
    Communication_Threshold INTEGER NOT NULL,
    Experience_Threshold INTEGER NOT NULL,
    Minimum_CGPA REAL NOT NULL
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
    status TEXT
)
""")

    # --------------------------------------------------
    # PREDICTIONS TABLE
    # --------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        match_score REAL,
        recommendation TEXT,
        status TEXT,

        FOREIGN KEY(student_id) REFERENCES students(student_id),
        FOREIGN KEY(job_id) REFERENCES jobs(job_id)
    )
    """)

    conn.commit()
    conn.close()

    print("Database created successfully.")


if __name__ == "__main__":
    create_database()