import sqlite3

conn = sqlite3.connect("student_job_matching.db")
cursor = conn.cursor()

tables = [
    "students",
    "jobs",
    "applications",
    "payments"
]

for table in tables:
    print(f"\n===== {table.upper()} =====")

    cursor.execute(f"PRAGMA table_info({table})")

    rows = cursor.fetchall()

    for row in rows:
        print(row)

conn.close()