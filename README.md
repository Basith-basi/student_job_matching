#  Student Job Matching System

A Machine Learning-based Student Job Matching System that recommends suitable job roles for students based on their skills, academic performance, communication ability, and experience.

The project follows a complete AI/ML pipeline including data loading, preprocessing, feature engineering, recommendation, ranking, explainability, visualization, and FastAPI deployment.

---

##  Features

- Load student and job datasets
- Data preprocessing and cleaning
- Feature engineering
- Rule-based job matching
- Candidate ranking
- Explainable recommendations
- Performance evaluation
- Data visualizations
- FastAPI REST API
- Interactive Swagger documentation

---

##  Tech Stack

- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- FastAPI
- Uvicorn

---

##  Project Structure

```
student_job_matching/
│
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
│   └── skill_gap.png
│
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── matching.py
│   ├── ranking.py
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

##  Installation

Clone the repository

```bash
git clone https://github.com/your-username/student_job_matching.git
```

Move into the project

```bash
cd student_job_matching
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

##  Run the Project

Execute the main program

```bash
python main.py
```

---

##  Run the API

Start the FastAPI server

```bash
uvicorn api.app:app --reload
```

Open Swagger UI

```
http://127.0.0.1:8000/docs
```

---

##  API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | API health status |
| POST | `/predict` | Predict job match |
| GET | `/rankings` | Rank students for a job |

---

##  Workflow

```
Students CSV
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
Matching Engine
       │
       ▼
Ranking
       │
       ▼
Explainability
       │
       ▼
Evaluation
       │
       ▼
Visualization
       │
       ▼
FastAPI Deployment
```

---

##  Output

The system provides:

- Match Score
- Recommendation Status
- Matching Reasons
- Student Rankings
- Performance Visualizations

---

##  Concepts Covered

- Data Loading
- Data Cleaning
- Feature Engineering
- Recommendation Systems
- Ranking Algorithms
- Explainable AI (XAI)
- Data Visualization
- FastAPI
- REST API Development
- Model Evaluation

---

##  Visualizations

The project generates:

- Candidate Ranking Chart
- Match Score Distribution
- Skill Gap Analysis
- Confusion Matrix

These plots are saved in the **plots/** directory.

---

##  Future Improvements

- Machine Learning-based recommendation model
- Random Forest / XGBoost implementation
- Model serialization (.pkl)
- Database integration
- Authentication
- Streamlit dashboard
- Docker deployment
- Cloud deployment (AWS/Azure)

---

