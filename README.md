# Student Job Matching System - Task 2

An AI/ML-based Student Job Matching System that recommends suitable candidates for job roles using threshold-based validation, feature engineering, rule-based matching, ranking, explainability, and FastAPI.

---

## Features

- Student and Job dataset loading
- Data preprocessing
- Feature engineering
- Match vector generation
- Threshold validation
- Threshold-aware scoring
- Candidate ranking
- Explainable recommendations
- Evaluation metrics
- FastAPI REST API
- Swagger API documentation
- Data visualizations

---

## Project Structure

```
student_job_matching/

├── api/
│   ├── app.py
│   ├── routes.py
│   └── schemas.py
│
├── data/
│   ├── students.csv
│   └── jobs.csv
│
├── models/
│
├── plots/
│   ├── candidate_ranking.png
│   ├── confusion_matrix.png
│   ├── match_score_distribution.png
│   ├── skill_gap.png
│   └── threshold_validation.png
│
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── matching.py
│   ├── ranking.py
│   ├── threshold_validation.py
│   ├── explainability.py
│   ├── evaluation.py
│   ├── visualization.py
│   └── utils.py
│
├── config.py
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- FastAPI
- Uvicorn

---

## Installation

Clone the repository

```bash
git clone <repository_url>
```

Move into the project

```bash
cd student_job_matching
```

Create virtual environment

```bash
python -m venv venv
```

Activate virtual environment

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run the Project

Execute

```bash
python main.py
```

---

## Run FastAPI

```bash
uvicorn api.app:app --reload
```

Open Swagger

```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | / | Home |
| GET | /health | Health Check |
| POST | /predict | Predict Student-Job Match |
| GET | /rankings | Candidate Ranking |
| GET | /thresholds/{job_id} | View Job Thresholds |

---

## AI/ML Workflow

```
Student Dataset
        │
        ▼
Data Loading
        │
        ▼
Preprocessing
        │
        ▼
Feature Engineering
        │
        ▼
Match Vector
        │
        ▼
Threshold Validation
        │
        ▼
Threshold-aware Scoring
        │
        ▼
Candidate Ranking
        │
        ▼
Explainability
        │
        ▼
Evaluation
        │
        ▼
FastAPI
```

---

## Evaluation Metrics

- Precision
- Recall
- F1 Score
- Classification Report
- Confusion Matrix
- ROC Curve (Optional)

---

## Generated Visualizations

- Candidate Ranking
- Match Score Distribution
- Skill Gap Analysis
- Threshold Validation
- Confusion Matrix

Generated plots are saved in the **plots/** folder.

---

## Task 2 Enhancements

- Threshold Validation
- Match Vector Generation
- Threshold-aware Scoring
- Threshold-based Explainability
- Enhanced Candidate Ranking
- Updated FastAPI Responses
- Threshold Visualization

---

## Future Improvements

- Random Forest Matching Model
- XGBoost Recommendation Engine
- Deep Learning Matching
- Resume Parsing
- Streamlit Dashboard
- Database Integration
- Authentication & Authorization

---

