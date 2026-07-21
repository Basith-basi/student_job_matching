import sqlite3

conn = sqlite3.connect("student_job_matching.db")
cursor = conn.cursor()

cursor.execute("""

INSERT INTO jobs
(
company,
title,
skills,
min_cgpa,
min_experience
)

VALUES
(
'Google',
'AI Engineer',
'Python,ML,SQL',
7.5,
1
)

""")

conn.commit()

conn.close()

print("Done")