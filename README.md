# Student Job Matching System

A FastAPI-based Student Job Matching System that recommends suitable jobs for students and ranks candidates for companies based on skills, CGPA, experience, and job requirements.

## Features

- Student-to-Job Ranking
- Candidate-to-Job Ranking
- Job Match Prediction
- Threshold Validation
- Explainable Predictions
- Model Evaluation Metrics
- Experiment Logging
- Data Visualization
- REST API with FastAPI

## Project Structure

```
student_job_matching/
│
├── api/
│   └── app.py
├── src/
│   ├── baseline.py
│   ├── data_loader.py
│   ├── evaluation.py
│   ├── explainability.py
│   ├── feature_engineering.py
│   ├── logger.py
│   ├── matching.py
│   ├── preprocessing.py
│   ├── ranking.py
│   ├── threshold_validation.py
│   ├── utils.py
│   └── visualization.py
│
├── scripts/
├── plots/
├── experiments_log.csv
├── config.py
├── main.py
├── requirements.txt
└── README.md
```

## Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/student_job_matching.git
cd student_job_matching
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment

**Windows**

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

## Run the Project

Generate sample data

```bash
python scripts/generate_data.py
```

Run the project

```bash
python main.py
```

Run the FastAPI server

```bash
uvicorn api.app:app --reload
```

Open Swagger UI

```
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | / | Home |
| GET | /health | Health Check |
| POST | /predict | Predict Job Match |
| GET | /jobs-for-student | Recommend Jobs for Student |
| GET | /rankings | Rank Candidates for Job |
| GET | /metrics | Evaluation Metrics |
| GET | /thresholds/{job_id} | Job Threshold Details |

## Outputs

- Student Job Recommendations
- Candidate Rankings
- Match Scores
- Explainable Predictions
- Threshold Validation
- Evaluation Metrics
- Experiment Log
- Visualization Charts

## Technologies Used

- Python
- FastAPI
- Pandas
- NumPy
- Scikit-learn
- Matplotlib

