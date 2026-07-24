# Student Job Matching Marketplace API

An AI-powered Student Job Matching Marketplace built with **FastAPI**, **Machine Learning**, and **SQLite**. The project recommends suitable jobs for students based on skill matching, provides explainable rankings, supports a pay-per-application workflow, and includes receipts, refunds, reconciliation, and spend-quality guardrails.

---

## Features

### Task 1 – Student & Job Matching
- Student and Job dataset loading
- Data preprocessing
- Skill matching
- Match score prediction
- Candidate ranking
- Job recommendations

### Task 2 – Feature Engineering
- Skill overlap calculation
- Feature extraction
- Improved matching accuracy
- Threshold-based matching

### Task 3 – Ranking & Evaluation
- Candidate ranking
- Job ranking
- Precision, Recall and F1-score
- Confusion Matrix
- Threshold validation
- Match score visualization

### Task 4 – Explainability
- Explainable AI recommendations
- Skill gap analysis
- Feature importance
- Candidate recommendation reasons

### Task 5 – Marketplace API
- FastAPI REST API
- Student APIs
- Job APIs
- Candidate APIs
- Metrics API
- Ranking API

### Task 6 – Subscription & Premium Plans
- Student subscription plans
- Company premium plans
- Plan validation
- Premium access control

### Task 7 – Pay-per-Application Flow
- ₹100 Pay-per-Application
- Payment Gateway Simulation
- Payment Validation
- Payment Verification
- Payment History
- Student Dashboard
- Company Dashboard
- Payment Database
- Duplicate Payment Prevention

### Task 8 – Receipts, Refunds & Reconciliation
- Spend Quality Guardrail
- Low-Fit Warning before payment
- Receipt Generation
- Refund Processing
- Payment Reconciliation
- Receipt Storage
- Refund History
- Transaction Tracking
- End-to-End Payment Workflow

---

# Project Structure

```
student_job_matching/
│
├── api/
│   ├── app.py
│   ├── routes.py
│   ├── schemas.py
│   ├── database.py
│
├── payments/
│   ├── payment_gateway.py
│   ├── payment_service.py
│   ├── payment_validator.py
│   ├── receipt_service.py
│   ├── refund_service.py
│   ├── reconciliation_service.py
│   ├── plans.py
│
├── src/
│   ├── matching.py
│   ├── ranking.py
│   ├── spend_guardrail.py
│   ├── explainability.py
│
├── data/
│   ├── students.csv
│   ├── jobs.csv
│   ├── applications.csv
│
├── outputs/
├── plots/
├── models/
├── main.py
├── requirements.txt
└── README.md
```

---

# Technologies Used

- Python 3.9+
- FastAPI
- SQLite
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Uvicorn

---

# Installation

Clone the repository

```bash
git clone https://github.com/yourusername/student_job_matching.git
```

Move into the project

```bash
cd student_job_matching
```

Create Virtual Environment

```bash
python -m venv venv
```

Activate Virtual Environment

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
uvicorn main:app --reload
```

Open Swagger UI

```
http://127.0.0.1:8000/docs
```

---

# API Endpoints

## Health

- GET `/health`

## Prediction

- POST `/predict`

## Jobs

- GET `/jobs`
- POST `/jobs`
- GET `/jobs/{job_id}/candidates`

## Students

- GET `/students/{student_id}/jobs`

## Applications

- POST `/applications`

## Payments

- GET `/payments`
- POST `/payments`
- POST `/payments/verify`
- GET `/payments/{payment_id}`
- GET `/payments/history/{student_name}`
- GET `/payments/company/{company}`

## Dashboards

- GET `/dashboard/student/{student}`
- GET `/dashboard/company/{company}`

## Task 8 APIs

### Receipt

```
GET /receipt/{transaction_id}
```

Returns payment receipt after successful transaction.

### Refund

```
POST /refund/{transaction_id}
```

Processes refund for a completed payment.

### Reconciliation

```
GET /reconciliation
```

Compares payment records, receipts, and refunds to verify consistency.

---

# Spend Quality Guardrail

Before allowing payment, the matching score is evaluated.

| Match Score | Result |
|-------------|--------|
| 75–100 | Payment Allowed |
| 50–74 | Payment Allowed with Average Match Warning |
| Below 50 | Low-Fit Warning / Payment Blocked |

This prevents students from paying for jobs that are poor matches.

---

# Machine Learning Workflow

```
Student Skills
      │
      ▼
Feature Engineering
      │
      ▼
Skill Matching
      │
      ▼
Match Score
      │
      ▼
Candidate Ranking
      │
      ▼
Spend Guardrail
      │
      ▼
Payment
      │
      ▼
Receipt
      │
      ▼
Refund
      │
      ▼
Reconciliation
```

---

# Evaluation Metrics

The project evaluates matching quality using:

- Precision
- Recall
- F1 Score
- False Positive Rate
- Threshold Validation
- Candidate Ranking
- Explainability Reports

---

# Key Features

- AI-based Job Recommendation
- Explainable Matching
- Candidate Ranking
- Job Ranking
- Match Score Prediction
- Payment Verification
- Premium Subscription Support
- Spend Quality Guardrail
- Receipt Generation
- Refund Processing
- Payment Reconciliation
- REST API using FastAPI
- SQLite Database

---

# Future Improvements

- Real Payment Gateway Integration (Stripe/Razorpay)
- Email Receipts
- PDF Receipt Download
- MLflow Experiment Tracking
- JWT Authentication
- Docker Deployment
- CI/CD Pipeline
- Recommendation using Embeddings
- Vector Database Integration

---

# Author

**Abdul Basith**

B.Tech Artificial Intelligence and Data Science

Student Job Matching Marketplace API