import sqlite3

conn = sqlite3.connect("student_job_matching.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(jobs)")
print("Columns:")
for row in cursor.fetchall():
    print(dict(row))

print("\nData:")
cursor.execute("SELECT * FROM jobs")
for row in cursor.fetchall():
    print(dict(row))

conn.close()