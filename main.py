from src.data_loader import DataLoader
from src.preprocessing import DataPreprocessor
from src.feature_engineering import FeatureEngineer
from src.threshold_validation import ThresholdValidator
from src.matching import JobMatcher
from src.ranking import JobRanker
from src.explainability import Explainability
from src.visualization import Visualizer
from src.evaluation import Evaluator

from src.utils import (
    print_heading,
    success,
    error,
    normalize_score,
    percentage,
    get_data_path
)

# ==========================================================
# INITIALIZE CLASSES
# ==========================================================

loader = DataLoader()
preprocessor = DataPreprocessor()
feature_engineer = FeatureEngineer()
validator = ThresholdValidator()
matcher = JobMatcher()
ranker = JobRanker()
explainer = Explainability()
visualizer = Visualizer()
evaluator = Evaluator()

# ==========================================================
# DATA LOADING
# ==========================================================

print_heading("DATA LOADING")

try:

    students = loader.load_students(
        get_data_path("students.csv")
    )

    jobs = loader.load_jobs(
        get_data_path("jobs.csv")
    )

    success("Datasets loaded successfully.")

except Exception as e:

    error(f"Failed to load datasets : {e}")
    raise

# ==========================================================
# DATA PREPROCESSING
# ==========================================================

print_heading("DATA PREPROCESSING")

students = preprocessor.handle_missing_values(students)
students = preprocessor.remove_duplicates(students)
students = preprocessor.format_strings(students)

jobs = preprocessor.handle_missing_values(jobs)
jobs = preprocessor.remove_duplicates(jobs)
jobs = preprocessor.format_strings(jobs)

success("Preprocessing completed.")

# ==========================================================
# SELECT SAMPLE STUDENT & JOB
# ==========================================================

student = students.iloc[0]
job = jobs.iloc[0]

# ==========================================================
# FEATURE ENGINEERING
# ==========================================================

print_heading("FEATURE ENGINEERING")

features = feature_engineer.create_feature_vector(
    student,
    job
)

print("\nGap Features")
print("-" * 50)

gap_features = [
    "Python Gap",
    "SQL Gap",
    "ML Gap",
    "Communication Gap",
    "CGPA Difference",
    "Experience Difference",
    "Skill Overlap"
]

for feature in gap_features:
    print(f"{feature:<30}: {features[feature]}")

print("\nMatch Vector")
print("-" * 50)

match_features = [
    "python_match",
    "sql_match",
    "ml_match",
    "communication_match",
    "experience_match",
    "cgpa_match"
]

for feature in match_features:
    print(f"{feature:<30}: {features[feature]}")

# ==========================================================
# THRESHOLD VALIDATION
# ==========================================================

print_heading("THRESHOLD VALIDATION")

validation = validator.validate(
    student,
    job
)

for skill, status in validation.items():

    symbol = "PASS" if status else "FAIL"

    print(f"{skill:<25}: {symbol}")

print()

print(f"Passed : {validator.passed_count(validation)}")
print(f"Failed : {validator.failed_count(validation)}")
print(f"Overall Status : {validator.overall_status(validation)}")

# ==========================================================
# MATCHING ENGINE
# ==========================================================

print_heading("MATCHING ENGINE")

score, reasons = matcher.calculate_match_score(
    student,
    job
)

score = normalize_score(score)

status = matcher.get_recommendation(score)

print(f"Student            : {student['Name']}")
print(f"Company            : {job['Company']}")
print(f"Role               : {job['Role']}")
print(f"Match Score        : {percentage(score)}")
print(f"Recommendation     : {status}")

# ==========================================================
# EXPLAINABILITY
# ==========================================================

print_heading("EXPLAINABILITY")

explanations = explainer.explain(
    student,
    job
)

for explanation in explanations:
    print(f"✔ {explanation}")

# ==========================================================
# STUDENT RANKING
# ==========================================================

print_heading("STUDENT RANKING")

ranking = ranker.rank_students(
    students,
    job
)

print()

print(
    ranking[
        [
            "Rank",
            "Student",
            "Passed Thresholds",
            "Score",
            "Status"
        ]
    ]
)

# ==========================================================
# MODEL EVALUATION
# ==========================================================

print_heading("MODEL EVALUATION")

# Dummy labels for demonstration
# Replace these with actual labels if available
y_true = [1, 1, 0, 1, 0, 1, 0, 1, 0, 1]
y_pred = [1, 1, 0, 1, 1, 1, 0, 0, 0, 1]

evaluator.evaluate(
    y_true,
    y_pred
)

# ==========================================================
# VISUALIZATION
# ==========================================================

print_heading("GENERATING VISUALIZATIONS")

visualizer.candidate_ranking(ranking)

visualizer.match_score_distribution(ranking)

visualizer.skill_gap(features)

# Dummy values for confusion matrix

y_true = [1, 1, 0, 1, 0]
y_pred = [1, 1, 1, 0, 0]

visualizer.confusion_matrix_plot(
    y_true,
    y_pred
)

success("Plots saved inside plots/ folder.")

# ==========================================================
# BEST MATCH
# ==========================================================

print_heading("BEST MATCH")

best = ranking.iloc[0]

print(f"Rank               : {best['Rank']}")
print(f"Student            : {best['Student']}")
print(f"Score              : {percentage(best['Score'])}")
print(f"Status             : {best['Status']}")

# ==========================================================
# PROJECT SUMMARY
# ==========================================================

print_heading("PROJECT SUMMARY")

print(f"Total Students     : {len(students)}")
print(f"Total Jobs         : {len(jobs)}")
print(f"Top Candidate      : {best['Student']}")
print(f"Top Match Score    : {percentage(best['Score'])}")

success("Student Job Matching System Executed Successfully.")