# Student Job Matching Marketplace

An AI-powered Student Job Matching Marketplace built with **Python, FastAPI, SQLite, Pandas, and Scikit-learn**. The system intelligently matches students with jobs based on verified skills, ranks candidates, provides explainable recommendations, and supports a complete **Pay-per-Application** workflow.

---

## Features

### AI Matching Engine
- Skill-based student-job matching
- Match score calculation
- Candidate ranking
- Job recommendation
- Threshold validation
- Explainable AI recommendations

### Marketplace
- Company job posting
- Student job application
- Candidate ranking
- Student job recommendations

### Payment System (Task 7)
- Premium subscription plans
- Pay-per-Application flow
- Payment validation
- Payment gateway simulation
- Payment verification
- Payment history
- Duplicate payment prevention

### Dashboard
- Student Dashboard
- Company Dashboard
- Match statistics
- Application statistics
- Payment statistics

---

# Tech Stack

- Python 3.9+
- FastAPI
- SQLite
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Uvicorn

---

# Project Structure

```
student_job_matching/
│
├── api/
│   ├── routes.py
│   ├── schemas.py
│   ├── database.py
│   └── app.py
│
├── payments/
│   ├── payment_service.py
│   ├── payment_gateway.py
│   ├── payment_validator.py
│   └── plans.py
│
├── src/
│   ├── matching.py
│   ├── ranking.py
│   ├── explainability.py
│   ├── threshold_validation.py
│   ├── visualization.py
│   └── evaluation.py
│
├── data/
│   ├── students.csv
│   ├── jobs.csv
│   └── applications.csv
│
├── outputs/
├── plots/
├── database/
├── main.py
├── requirements.txt
└── README.md
```

---

# AI Pipeline

```
Student Dataset
        │
        ▼
Feature Extraction
        │
        ▼
Threshold Validation
        │
        ▼
Match Score Calculation
        │
        ▼
Candidate Ranking
        │
        ▼
Explainability
        │
        ▼
Recommendation
```

---

# Task 7 – Pay-per-Application Flow

The project implements an end-to-end **Pay-per-Application** workflow.

## Flow

```
Student
   │
   ▼
Predict Job Match
   │
   ▼
Choose Premium Plan
   │
   ▼
Payment Validation
   │
   ▼
Payment Gateway (Test Mode)
   │
   ▼
Payment Success
   │
   ▼
Submit Application
   │
   ▼
Application Saved
   │
   ▼
Candidate Ranking Updated
```

---

# Matching Features

- Skill Matching
- Threshold Validation
- Candidate Ranking
- Job Recommendation
- Explainable AI
- Match Score
- Recommendation Category

Recommendation Levels

- Highly Recommended
- Recommended
- Average Match
- Low Match

---

# Payment Features

- Premium Student Plan
- Payment Validation
- Duplicate Payment Detection
- Transaction ID Generation
- Payment Verification
- Payment History
- Company Payment Reports
- Test Payment Gateway

---

# API Endpoints

## Health

```
GET /health
```

---

## Metrics

```
GET /metrics
```

---

## Predict Match

```
POST /predict
```

---

## Job APIs

```
GET /jobs

POST /jobs
```

---

## Application APIs

```
POST /applications

GET /students/{student_id}/jobs

GET /jobs/{job_id}/candidates
```

---

## Payment APIs

```
POST /payments

POST /payments/verify

GET /payments

GET /payments/{payment_id}

GET /payments/history/{student_name}

GET /payments/company/{company}
```

---

## Dashboard APIs

```
GET /dashboard/student/{student_name}

GET /dashboard/company/{company}
```

---

# Evaluation Metrics

The matching system is evaluated using:

- Precision
- Recall
- F1 Score
- False Positive Rate
- Confusion Matrix
- Match Score Distribution

---

# Explainable AI

Every recommendation includes:

- Match Score
- Skill Analysis
- Threshold Validation
- Recommendation Category
- Plain-English Explanation

---

# Running the Project

## Clone Repository

```bash
git clone https://github.com/yourusername/student_job_matching.git
```

```
cd student_job_matching
```

---

## Create Virtual Environment

```bash
python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux/Mac

```bash
source venv/bin/activate
```

---

## Install Requirements

```bash
pip install -r requirements.txt
```

---

## Run FastAPI

```bash
uvicorn main:app --reload
```

---

## Swagger UI

```
http://127.0.0.1:8000/docs
```

---

## ReDoc

```
http://127.0.0.1:8000/redoc
```

---

# Sample Workflow

1. Company creates a job.
2. Student checks job recommendations.
3. Student purchases a premium plan.
4. Payment is validated.
5. Payment is processed.
6. Student applies for the job.
7. Match score is calculated.
8. Candidate is ranked.
9. Dashboard updates automatically.

---

# Outputs

- Match Scores
- Candidate Ranking
- Job Recommendations
- Explainability Report
- Threshold Validation
- Payment Records
- Student Dashboard
- Company Dashboard
- Evaluation Metrics

---

# Future Improvements

- Real payment gateway integration (Razorpay/Stripe)
- JWT Authentication
- Role-based authorization
- PostgreSQL/MySQL support
- MLflow experiment tracking
- Resume parsing using NLP
- Vector similarity search
- Cloud deployment (AWS/Azure)

---

# Author

**Abdul Basith**

B.Tech Artificial Intelligence & Data Science

---

# License

This project is developed for educational and internship purposes.