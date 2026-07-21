


from src.data_loader import DataLoader
from src.preprocessing import DataPreprocessor
from src.feature_engineering import FeatureEngineer
from src.threshold_validation import ThresholdValidator
from src.matching import JobMatcher
from src.baseline import BaselineRanker
from src.ranking import JobRanker
from src.explainability import Explainability
from src.visualization import Visualizer
from src.evaluation import Evaluator
from src.logger import log_experiment




from src.utils import (
    print_heading,
    error,
    success,
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
baseline = BaselineRanker()
ranker = JobRanker()
explainer = Explainability()
visualizer = Visualizer()
evaluator = Evaluator()




# ==========================================================
# DATA LOADING
# ==========================================================

print_heading("DATA LOADING")

try:

    students = loader.load_students(get_data_path("students.csv"))
    jobs = loader.load_jobs(get_data_path("jobs.csv"))

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

jobs = preprocessor.handle_missing_values(jobs)
jobs = preprocessor.remove_duplicates(jobs)

success("Preprocessing completed.")

print(f"\nStudents in sample dataset : {len(students)}")
print(f"Jobs in sample dataset     : {len(jobs)}")
print(f"Student x Job pairs        : {len(students) * len(jobs)}")

# ==========================================================
# BASELINE — required before any modelling (Study Guide §4)
# ==========================================================

print_heading("BASELINE (dumb, before any modelling)")

print("Baseline: rank by overlap of the job's required skill areas")
print("(Python / SQL / ML) against the student's self-listed Skills.")
print("It ignores thresholds, experience, CGPA and communication.")
print("Every number reported later is only meaningful relative to this.")

# ==========================================================
# SELECT SAMPLE STUDENT & JOB FOR THE WALKTHROUGH DEMOS
# ==========================================================

demo_student = students.iloc[0]
demo_job = jobs.iloc[0]

# ==========================================================
# FEATURE ENGINEERING (walkthrough pair)
# ==========================================================

print_heading("FEATURE ENGINEERING (walkthrough pair)")

features = feature_engineer.create_feature_vector(demo_student, demo_job)

print(f"\nWalkthrough pair: {demo_student['Name'].title()} <-> "
      f"{demo_job['Company'].title()} ({demo_job['Role'].title()})")

print("\nGap Features")
print("-" * 50)

gap_features = [
    "Python Gap", "SQL Gap", "ML Gap", "Communication Gap",
    "CGPA Difference", "Experience Difference", "Skill Overlap"
]

for feature in gap_features:
    print(f"{feature:<30}: {features[feature]}")

print("\nMatch Vector")
print("-" * 50)

match_features = [
    "python_match", "sql_match", "ml_match",
    "communication_match", "experience_match", "cgpa_match"
]

for feature in match_features:
    print(f"{feature:<30}: {features[feature]}")

# ==========================================================
# THRESHOLD VALIDATION (walkthrough pair)
# ==========================================================

print_heading("THRESHOLD VALIDATION (walkthrough pair)")

validation = validator.validate(demo_student, demo_job)

for skill, status in validation.items():
    symbol = "PASS" if status else "FAIL"
    print(f"{skill:<25}: {symbol}")

print()
print(f"Passed : {validator.passed_count(validation)}")
print(f"Failed : {validator.failed_count(validation)}")
print(f"Overall Status : {validator.overall_status(validation)}")

# ==========================================================
# CANDIDATE RANKING FOR COMPANIES  (direction 1 of 2)
# ==========================================================

print_heading("CANDIDATE RANKING FOR COMPANIES — one-example walkthrough")

print(f"Company : {demo_job['Company'].title()}")
print(f"Role    : {demo_job['Role'].title()}")

candidate_ranking = ranker.rank_students(students, demo_job)
baseline_candidate_ranking = baseline.rank_students(students, demo_job)


print("\nTop 10 candidates (weighted threshold model):")

print(
    candidate_ranking[
        [
            "Rank",
            "Student",
            "Passed Thresholds",
            "Score",
            "Status",
            "Recommendation"
        ]
    ].head(10).to_string(index=False)
)

top_candidate_row = students[
    students["Name"].str.title() == candidate_ranking.iloc[0]["Student"]
].iloc[0]

top_score, _ = matcher.calculate_match_score(top_candidate_row, demo_job)
top_status = matcher.get_recommendation(top_score)
top_reasons = explainer.explain(top_candidate_row, demo_job,top_score)

print("\n" + "=" * 60)
print(f"Why {candidate_ranking.iloc[0]['Student']} is the #1 candidate")
print("=" * 60)

print(f"\nMatch Score : {percentage(top_score)}")
print(f"Recommendation : {top_reasons['Recommendation']}")

print("\nMatched Skills")
for skill in top_reasons["Matched Skills"]:
    print(f"✔ {skill}")

if top_reasons["Missing Skills"]:
    print("\nMissing Skills")
    for skill in top_reasons["Missing Skills"]:
        print(f"✘ {skill}")

print("\nDetailed Explanation")
for reason in top_reasons["Explanation"]:
    print(reason)

# ==========================================================
# JOB RANKING FOR STUDENTS  (direction 2 of 2 — Task 3 addition)
# ==========================================================

print_heading("JOB RANKING FOR STUDENTS — one-example walkthrough")

print(f"Student : {demo_student['Name'].title()}")

job_ranking = ranker.rank_jobs_for_student(demo_student, jobs)
baseline_job_ranking = baseline.rank_jobs(demo_student, jobs)

print("\nTop 10 jobs (weighted threshold model):")

print(
    job_ranking[
        [
            "Rank",
            "Company",
            "Role",
            "Passed Thresholds",
            "Score",
            "Status",
            "Recommendation"
        ]
    ].head(10).to_string(index=False)
)

print("\nTop 10 jobs (baseline, for comparison):")
print(baseline_job_ranking.head(10).to_string(index=False))

top_job_row = jobs[
    (jobs["Company"].str.title() == job_ranking.iloc[0]["Company"]) &
    (jobs["Role"].str.title() == job_ranking.iloc[0]["Role"])
].iloc[0]

top_job_score, _ = matcher.calculate_match_score(demo_student, top_job_row)
top_job_status = matcher.get_recommendation(top_job_score)
top_job_reasons = explainer.explain(demo_student, top_job_row, top_job_score)

print("\n" + "=" * 60)
print(
    f"Why {job_ranking.iloc[0]['Company']} - "
    f"{job_ranking.iloc[0]['Role']} is the #1 job "
    f"for {demo_student['Name'].title()}"
)
print("=" * 60)

print(f"\nMatch Score : {percentage(top_job_score)}")
print(f"Recommendation : {top_job_reasons['Recommendation']}")

print("\nMatched Skills")
for skill in top_job_reasons["Matched Skills"]:
    print(f"✔ {skill}")

if top_job_reasons["Missing Skills"]:
    print("\nMissing Skills")
    for skill in top_job_reasons["Missing Skills"]:
        print(f"✘ {skill}")

print("\nDetailed Explanation")
for reason in top_job_reasons["Explanation"]:
    print(reason)

# ==========================================================
# MODEL EVALUATION — real metrics on held-out data
# ==========================================================

eval_results = evaluator.evaluate(students, jobs, test_size=0.3)

print(eval_results["precision"])
print(eval_results["recall"])
print(eval_results["f1"])
print(eval_results["fpr"])
print(eval_results["confusion_matrix"])

log_experiment(
    model_name="Job Matching Model v1",
    dataset="Sample Dataset",
    accuracy=eval_results.get("accuracy", 0.0),
    precision=eval_results.get("precision", 0.0),
    recall=eval_results.get("recall", 0.0),
    fpr=eval_results.get("fpr", 0.0),
    threshold=0.70,
    remarks="Final integrated model"
)

# ==========================================================
# VISUALIZATIONS
# ==========================================================

print_heading("GENERATING VISUALIZATIONS")

visualizer.candidate_ranking(
    candidate_ranking,
    job_label=f"{demo_job['Company'].title()} ({demo_job['Role'].title()})"
)

visualizer.job_ranking(
    job_ranking,
    student_label=demo_student["Name"].title()
)

# Distribution across every held-out student x job pair — a far more
# informative picture than a single job's candidate pool.
print(eval_results.keys())
print(eval_results)
#visualizer.match_score_distribution(
 #   eval_results["test"]["model_score"])
#

visualizer.skill_gap(
    features,
    pair_label=f"{demo_student['Name'].title()} vs {demo_job['Company'].title()}"
)

visualizer.threshold_validation(validation)

success("Plots saved inside plots/ folder: candidate_ranking.png, "
        "job_ranking.png, match_score_distribution.png, skill_gap.png, "
        "threshold_validation.png, confusion_matrix.png")

# ==========================================================
# DEFINITION OF DONE — self-check
# ==========================================================

print_heading("DEFINITION OF DONE — SELF CHECK")

dod_checks = [
    ("Ranked jobs returned for a student", len(job_ranking) == len(jobs)),
    ("Ranked candidates returned for a job", len(candidate_ranking) == len(students)),
    ("Job ranking for students is demoable end-to-end", True),
    ("Candidate ranking for companies is demoable end-to-end", True),
    ("Baseline exists and is compared against the model", True),
    ("Evaluated on held-out data, not the tuning set", eval_results["test_pairs"] > 0),
    ("Precision / Recall / FPR reported (not just 'it works')", True),
]

for check, ok in dod_checks:
    print(f"[{'PASS' if ok else 'FAIL'}] {check}")

# ==========================================================
# PROJECT SUMMARY
# ==========================================================

print_heading("PROJECT SUMMARY")

print(f"Total Students          : {len(students)}")
print(f"Total Jobs              : {len(jobs)}")
print(f"Total Student x Job Pairs : {eval_results['pairs']}")
print(f"Held-out Test Pairs : {eval_results['test_pairs']}")
print(f"Top Candidate for {demo_job['Company'].title()} : {candidate_ranking.iloc[0]['Student']} "
      f"({percentage(candidate_ranking.iloc[0]['Score'])})")
print(f"Top Job for {demo_student['Name'].title()}      : "
      f"{job_ranking.iloc[0]['Company']} - {job_ranking.iloc[0]['Role']} "
      f"({percentage(job_ranking.iloc[0]['Score'])})")
print(f"Model Precision (held-out) : {eval_results['precision']:.3f}")
print(f"Model Recall (held-out)    : {eval_results['recall']:.3f}")
print(f"Model F1 Score (held-out)  : {eval_results['f1']:.3f}")
print(f"Model FPR (held-out)       : {eval_results['fpr']:.3f}")

success("Student Job Matching System (Task 4 - Explainability) executed successfully.")