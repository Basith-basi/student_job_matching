# Student Job Matching & Payment System

A FastAPI-based AI-powered Student Job Matching System developed as part of the PlaceMux AI/ML Engineer Industry Immersion Program.

The project recommends suitable jobs to students using skill matching, ranking, explainable AI, and integrates a complete payment workflow including subscriptions, pay-per-application, receipts, refunds, reconciliation, spend-quality guardrails, and payment resilience.

---

## Features

### AI/ML
- Student-Job Matching
- Candidate Ranking
- Match Score Prediction
- Explainable Recommendations
- Skill Gap Analysis
- Spend Quality Guardrail
- Conversion Quality Check

### Payment System
- Premium Student Subscription
- Pay-per-Application
- Payment Verification
- Duplicate Payment Detection
- Receipt Generation
- Refund Processing
- Reconciliation
- Payment Retry
- Payment Failure Handling
- Payment Logs

### APIs
- Student Prediction
- Job Management
- Candidate Ranking
- Applications
- Student Dashboard
- Company Dashboard
- Payments
- Receipts
- Refunds
- Reconciliation
- Conversion Quality
- Payment Retry
- Payment Logs

---

## Tech Stack

- Python 3
- FastAPI
- SQLite
- Pandas
- NumPy
- Scikit-learn
- Uvicorn

---

## Project Structure

```
student_job_matching/
│
├── api/
│   ├── routes.py
│   ├── database.py
│   ├── schemas.py
│
├── payments/
│   ├── payment_service.py
│   ├── payment_gateway.py
│   ├── payment_validator.py
│   ├── receipt_service.py
│   ├── refund_service.py
│   ├── reconciliation.py
│   ├── spend_guardrail.py
│   ├── conversion_quality.py
│   └── payment_logger.py
│
├── data/
├── database/
├── outputs/
├── main.py
└── requirements.txt
```

---

## Installation

Clone the repository

```bash
git clone <your-github-repository-link>
```

Go to project

```bash
cd student_job_matching
```

Create virtual environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
uvicorn main:app --reload
```

Open Swagger

```
http://127.0.0.1:8000/docs
```

---

## Important APIs

### Matching

- POST /predict
- GET /jobs
- POST /jobs
- POST /applications
- GET /jobs/{job_id}/candidates
- GET /students/{student_id}/jobs

### Payments

- POST /payments
- POST /payments/verify
- GET /payments
- GET /payments/history/{student}
- GET /payments/company/{company}
- GET /payments/{payment_id}

### Receipts & Refunds

- GET /receipt/{transaction_id}
- POST /refund/{transaction_id}
- GET /reconciliation

### Task 8

- GET /conversion-quality
- POST /payments/fail
- POST /payments/retry
- GET /logs/payments

---

## Tasks Completed

- Task 1 – Student Job Matching
- Task 2 – Feature Engineering
- Task 3 – Candidate Ranking
- Task 4 – Explainable AI
- Task 5 – Marketplace APIs
- Task 6 – Subscription Payment System
- Task 7 – Pay-per-Application
- Task 8 – Receipts, Refunds & Reconciliation
- Task 9 – Payment Failure Handling & Conversion Quality

---

## GitHub Repository

Add your repository link here

```
https://github.com/yourusername/student_job_matching
```

---

## Author

Abdul Basith

B.Tech Artificial Intelligence & Data Science