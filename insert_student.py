import sqlite3

conn = sqlite3.connect("student_job_matching.db")
cursor = conn.cursor()

cursor.execute("""

INSERT INTO students
(
student_name,
skills,
cgpa,
experience,
communication
)

VALUES
(
'Michael',
'Python,SQL,ML',
8.4,
2,
85
)

""")

conn.commit()

conn.close()

print("Inserted")
