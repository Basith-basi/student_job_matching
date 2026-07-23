# Task 7 — Pay-per-Application Matching Tune

## Delivered

- Explainable six-feature matching using persisted tuned weights and a persisted match threshold.
- ₹100 pay-per-application endpoint: an application is created only after a successful test-gateway charge.
- Payment records retain the exact gateway transaction ID, amount, student, job, and status for reconciliation.
- Baseline comparison, experiment log, selected model configuration, and held-out evaluation outputs.

## Held-out evaluation evidence

Dataset: `data/students.csv` × `data/jobs.csv` (3,630 student-job pairs).

| Split | Pairs |
| --- | ---: |
| Training | 2,178 |
| Validation / tuning | 726 |
| Untouched test | 726 |

| Model | Precision | Recall | F1 | False-positive rate |
| --- | ---: | ---: | ---: | ---: |
| Skills-overlap baseline | 0.185 | 1.000 | 0.313 | 0.905 |
| Tuned matcher | 0.316 | 1.000 | 0.481 | 0.445 |

Selected configuration: Python 0.10, SQL 0.10, Machine Learning 0.40, Communication 0.10, Experience 0.20, CGPA 0.10; match threshold 90.

The tuned model improved held-out F1 by 0.168 and reduced false-positive rate by 0.460 versus the baseline. Full evidence is saved in `outputs/evaluation_summary.json`, `outputs/model_config.json`, `outputs/ranking_experiments.csv`, and `experiments_log.csv`.

## Live demo

1. Run `uvicorn api.app:app --reload`.
2. Open `/docs` and call `POST /predict` with `{"student_id": 1, "job_id": 101}`. The response includes score, eligibility, six criterion checks, and a plain-English explanation.
3. Call `POST /applications` with `{"student": "John", "job_id": 101}`. The server charges exactly ₹100 in test mode.
4. If the simulated gateway returns `SUCCESS`, the response contains the transaction ID and created application. `FAILED` or `PENDING` responses are recorded as payments but create no application.
5. Use `POST /payments/verify` with the transaction ID to reconcile the stored result with the gateway result.

## Limitations

The gateway is intentionally simulated and randomly returns `SUCCESS`, `FAILED`, or `PENDING`; it never collects real money. Automated tests mock these outcomes to cover each path reliably. The current labels use the product's explicit eligibility rules; production training should use reviewed hiring outcomes and add fairness/drift monitoring.
