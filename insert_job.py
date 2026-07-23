import sqlite3

conn = sqlite3.connect("student_job_matching.db")
cursor = conn.cursor()

cursor.execute("""

INSERT INTO jobs
(
company,
role,
skills,
Python_Threshold,
SQL_Threshold,
ML_Threshold,
Communication_Threshold,
Experience_Threshold,
Minimum_CGPA
)

VALUES
(
'Google',
'AI Engineer',
'Python,ML,SQL',
85,
70,
80,
60,
2,
7.5
)

""")

conn.commit()

conn.close()

print("Done")
