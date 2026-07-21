# Student Job Matching Marketplace

A FastAPI-based **Student Job Matching Marketplace** that connects students with companies based on skills, CGPA, and experience. The project also includes job applications, payment processing, subscription plans, dashboards, and REST APIs using SQLite.

---

## Features

- Student Management
- Job Management
- AI-based Job Recommendation
- Student Job Applications
- Premium Student Subscription
- Payment Processing & Verification
- Student Dashboard
- Company Dashboard
- REST APIs using FastAPI
- SQLite Database
- Interactive Swagger Documentation

---

## Tech Stack

- Python 3.x
- FastAPI
- Uvicorn
- SQLite3
- Pydantic
- Pandas
- NumPy
- Scikit-learn

---

## Project Structure

```text
student_job_matching/
│
├── api/
│   ├── app.py
│   ├── routes.py
│   ├── schemas.py
│   └── database.py
│
├── payments/
│   ├── payment_service.py
│   ├── payment_gateway.py
│   ├── plans.py
│   └── validator.py
│
├── src/
│   ├── matching.py
│   ├── ranking.py
│   ├── preprocessing.py
│   ├── recommendation.py
│   └── utils.py
│
├── data/
│   ├── students.csv
│   └── jobs.csv
│
├── student_job_matching.db
├── requirements.txt
├── README.md
└── main.py
```

---

## Installation

### Clone Repository

```bash
git clone <your-github-repository>
cd student_job_matching
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

**Windows**

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run the Project

```bash
uvicorn api.app:app --reload
```

Server:

```
http://127.0.0.1:8000
```

Swagger Documentation:

```
http://127.0.0.1:8000/docs
```

---

# Database Tables

- students
- jobs
- applications
- predictions
- payments

---

# Available APIs

## Health

| Method | Endpoint |
|---------|----------|
| GET | /health |
| GET | /metrics |

---

## Students

| Method | Endpoint |
|---------|----------|
| GET | /students |
| GET | /students/{id} |
| GET | /students/{id}/jobs |

---

## Jobs

| Method | Endpoint |
|---------|----------|
| GET | /jobs |
| POST | /jobs |
| GET | /jobs/{job_id} |
| GET | /jobs/{job_id}/candidates |

---

## Applications

| Method | Endpoint |
|---------|----------|
| POST | /applications |

---

## Payments

| Method | Endpoint |
|---------|----------|
| POST | /payments |
| POST | /payments/verify |
| GET | /payments/{payment_id} |
| GET | /payments/history/{student_name} |
| GET | /payments/company/{company} |

---

## Dashboard

| Method | Endpoint |
|---------|----------|
| GET | /dashboard/student/{student_name} |
| GET | /dashboard/company/{company} |

---

# Example Request

### Create Job

```json
{
  "company": "Google",
  "title": "AI Engineer",
  "skills": "Python,ML,SQL",
  "min_cgpa": 7.5,
  "min_experience": 1
}
```

---

### Create Payment

```json
{
  "student_name": "Michael",
  "company": "Google",
  "job_id": 1,
  "plan": "PREMIUM_STUDENT",
  "amount": 299
}
```

---

### Apply for Job

```json
{
  "student": "Michael",
  "job_id": 1
}
```

---

# Project Workflow

1. Register students and jobs.
2. Store records in SQLite.
3. Recommend matching jobs.
4. Students apply for jobs.
5. Premium subscription payment.
6. Verify payment.
7. Track applications.
8. View Student Dashboard.
9. View Company Dashboard.

---

# Current Progress

- Student APIs
- Job APIs
- Recommendation APIs
- Payment APIs
- Payment Verification
- Student Dashboard
- Company Dashboard
- SQLite Integration
- Swagger Documentation

---

# Future Improvements

- JWT Authentication
- Resume Upload
- Email Notifications
- Machine Learning Match Score
- Docker Deployment
- CI/CD Pipeline
- PostgreSQL Support

---

# Author

**Abdul Basith**

B.Tech – Artificial Intelligence and Data Science