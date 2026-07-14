"""
Generates a larger, real-shaped sample dataset for Task 3.

Why: the Task 2 dataset had 10 students x 10 jobs. That's fine for wiring
plumbing together, but the study guide explicitly flags "only works on a
toy example" as a failure mode, and you cannot get a meaningful
train/held-out split or stable precision/recall/FPR numbers out of 10 rows.

This script generates 120 students and 30 jobs with plausible, correlated
skill/threshold distributions (not uniform noise) and writes them to
data/students.csv and data/jobs.csv, overwriting the toy files.
The original 10x10 files are preserved as data/students_original_task2.csv
and data/jobs_original_task2.csv.
"""

import numpy as np
import pandas as pd
import os

rng = np.random.default_rng(42)

FIRST_NAMES = [
    "John", "Alice", "David", "Sarah", "Michael", "Emma", "James", "Sophia",
    "Daniel", "Olivia", "Ethan", "Ava", "Noah", "Mia", "Liam", "Isabella",
    "Mason", "Grace", "Lucas", "Chloe", "Aditya", "Priya", "Rohan", "Ananya",
    "Karan", "Neha", "Arjun", "Divya", "Rahul", "Sneha", "Vikram", "Pooja",
    "Sanjay", "Kavya", "Aarav", "Ishita", "Varun", "Riya", "Nikhil", "Meera",
]

COMPANIES_ROLES = [
    ("Google", "ML Engineer"), ("Microsoft", "Data Scientist"),
    ("Amazon", "Data Analyst"), ("Infosys", "Python Developer"),
    ("TCS", "AI Engineer"), ("Accenture", "ML Engineer"),
    ("IBM", "Backend Developer"), ("Wipro", "Data Engineer"),
    ("Meta", "AI Research Intern"), ("Oracle", "Software Engineer"),
    ("Adobe", "Data Scientist"), ("Flipkart", "ML Engineer"),
    ("Swiggy", "Backend Developer"), ("Zomato", "Data Analyst"),
    ("Paytm", "Python Developer"), ("HCL", "Data Engineer"),
    ("Capgemini", "AI Engineer"), ("Deloitte", "Data Analyst"),
    ("Cognizant", "Software Engineer"), ("Salesforce", "ML Engineer"),
    ("Uber", "Data Scientist"), ("Ola", "Backend Developer"),
    ("Byjus", "AI Research Intern"), ("Razorpay", "Python Developer"),
    ("Freshworks", "Software Engineer"), ("Zoho", "Data Engineer"),
    ("PhonePe", "ML Engineer"), ("Myntra", "Data Analyst"),
    ("Nykaa", "Python Developer"), ("CRED", "AI Engineer"),
]


def generate_students(n=120):
    rows = []
    for i in range(1, n + 1):
        # A student's overall ability level drives correlated skill scores,
        # plus per-skill noise, so the data has real (not random) structure.
        ability = rng.normal(78, 10)

        python = np.clip(ability + rng.normal(0, 8), 40, 99)
        sql = np.clip(ability + rng.normal(0, 9), 35, 99)
        ml = np.clip(ability + rng.normal(0, 9), 35, 99)
        comm = np.clip(ability + rng.normal(5, 8), 45, 99)
        experience = int(np.clip(rng.poisson(1.4), 0, 5))
        cgpa = np.round(np.clip(ability / 100 * 3 + 6.3 + rng.normal(0, 0.3), 6.0, 9.9), 2)

        python, sql, ml, comm = (int(round(x)) for x in (python, sql, ml, comm))

        skills = []
        if python >= 65:
            skills.append("Python")
        if sql >= 65:
            skills.append("SQL")
        if ml >= 65:
            skills.append("ML")
        if comm >= 80:
            skills.append("Communication")
        if not skills:
            skills.append("Python")  # every student has at least one listed skill

        name = FIRST_NAMES[(i - 1) % len(FIRST_NAMES)]
        if i > len(FIRST_NAMES):
            name = f"{name}{(i - 1) // len(FIRST_NAMES) + 1}"

        rows.append({
            "Student_ID": i,
            "Name": name,
            "Skills": ",".join(skills),
            "Python": python,
            "SQL": sql,
            "Machine Learning": ml,
            "Communication": comm,
            "Experience": experience,
            "CGPA": cgpa,
        })

    return pd.DataFrame(rows)


def generate_jobs(n=30):
    rows = []
    for i in range(n):
        company, role = COMPANIES_ROLES[i % len(COMPANIES_ROLES)]
        job_id = 101 + i

        # Role difficulty drives correlated thresholds, same idea as ability above.
        difficulty = rng.normal(76, 7)

        python_t = int(np.clip(difficulty + rng.normal(0, 6), 55, 95))
        sql_t = int(np.clip(difficulty + rng.normal(-4, 7), 50, 92))
        ml_t = int(np.clip(difficulty + rng.normal(2, 7), 50, 95))
        comm_t = int(np.clip(difficulty + rng.normal(0, 5), 55, 90))
        exp_t = int(np.clip(rng.poisson(1.1), 0, 3))
        min_cgpa = np.round(np.clip(difficulty / 100 * 2.6 + 6.2 + rng.normal(0, 0.25), 6.0, 9.0), 2)

        rows.append({
            "Job_ID": job_id,
            "Company": company,
            "Role": f"{role} {i + 1}" if role in [r for _, r in COMPANIES_ROLES[:i % len(COMPANIES_ROLES)]] else role,
            "Python_Threshold": python_t,
            "SQL_Threshold": sql_t,
            "ML_Threshold": ml_t,
            "Communication_Threshold": comm_t,
            "Minimum_CGPA": min_cgpa,
            "Experience_Threshold": exp_t,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base, "data")

    students = generate_students(120)
    jobs = generate_jobs(30)

    students.to_csv(os.path.join(data_dir, "students.csv"), index=False)
    jobs.to_csv(os.path.join(data_dir, "jobs.csv"), index=False)

    print(f"Wrote {len(students)} students -> data/students.csv")
    print(f"Wrote {len(jobs)} jobs -> data/jobs.csv")
