import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

import pandas as pd
from fastapi import HTTPException

import api.routes as routes
from api.schemas import ApplicationCreate, PredictionRequest
from src.evaluation import Evaluator
from src.explainability import Explainability
from src.matching import JobMatcher
from src.threshold_validation import ThresholdValidator


class Task7Tests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "task7.db"
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.executescript("""
            CREATE TABLE jobs (job_id INTEGER PRIMARY KEY, company TEXT, role TEXT, skills TEXT, Python_Threshold INTEGER, SQL_Threshold INTEGER, ML_Threshold INTEGER, Communication_Threshold INTEGER, Experience_Threshold INTEGER, Minimum_CGPA REAL);
            CREATE TABLE applications (application_id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, job_id INTEGER, score REAL, status TEXT);
            CREATE TABLE payments (payment_id INTEGER PRIMARY KEY AUTOINCREMENT, student_name TEXT, company TEXT NOT NULL, job_id INTEGER NOT NULL, plan TEXT, amount REAL NOT NULL, payment_status TEXT NOT NULL, transaction_id TEXT UNIQUE NOT NULL, payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        """)
        connection.commit()
        connection.close()
        self.original_connection = routes.get_connection
        routes.get_connection = self.connection
        self.original_charge = routes.payment_service.charge_application

    def tearDown(self):
        routes.get_connection = self.original_connection
        routes.payment_service.charge_application = self.original_charge
        self.temp_dir.cleanup()

    def connection(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def test_matcher_loads_persisted_weights_and_explains_decision(self):
        config_path = Path(self.temp_dir.name) / "model.json"
        config_path.write_text(json.dumps({"weights": {"Python": 0.1, "SQL": 0.1, "Machine Learning": 0.4, "Communication": 0.1, "Experience": 0.2, "CGPA": 0.1}, "match_threshold": 90}), encoding="utf-8")
        student = pd.read_csv("data/students.csv").iloc[0]
        job = pd.read_csv("data/jobs.csv").iloc[0]
        score, recommendation, reasons = JobMatcher(config_path).calculate_match_score(student, job)
        explanation = Explainability().explain(student, job, score)
        self.assertIsInstance(score, float)
        self.assertTrue(recommendation)
        self.assertEqual(len(reasons), 6)
        self.assertIn("Matched Criteria", explanation)

    def test_validator_counts_only_six_requirements(self):
        student = pd.read_csv("data/students.csv").iloc[0]
        job = pd.read_csv("data/jobs.csv").iloc[0]
        validation = ThresholdValidator().validate(student, job)
        self.assertEqual(ThresholdValidator().passed_count(validation) + ThresholdValidator().failed_count(validation), 6)

    def test_evaluation_keeps_test_pairs_separate(self):
        evaluator = Evaluator(output_folder=Path(self.temp_dir.name) / "outputs")
        pairs = evaluator.build_labeled_pairs(pd.read_csv("data/students.csv"), pd.read_csv("data/jobs.csv"))
        train_validation, test = evaluator._split(pairs, 0.2, 42)
        train, validation = evaluator._split(train_validation, 0.25, 43)
        self.assertTrue(set(test.index).isdisjoint(train.index))
        self.assertTrue(set(test.index).isdisjoint(validation.index))

    def test_successful_payment_creates_application_and_reconciles(self):
        routes.payment_service.charge_application = lambda: {"status": "SUCCESS", "transaction_id": "success-txn", "amount": 100.0}
        result = routes.apply_job(ApplicationCreate(student="John", job_id=101))
        self.assertTrue(result["application_created"])
        self.assertEqual(result["amount"], 100.0)
        connection = self.connection()
        self.assertEqual(connection.execute("SELECT COUNT(*) FROM applications").fetchone()[0], 1)
        payment = connection.execute("SELECT amount, payment_status FROM payments WHERE transaction_id = 'success-txn'").fetchone()
        connection.close()
        self.assertEqual((payment["amount"], payment["payment_status"]), (100.0, "SUCCESS"))

    def test_failed_or_pending_payment_never_creates_application(self):
        for status in ("FAILED", "PENDING"):
            routes.payment_service.charge_application = lambda outcome=status: {"status": outcome, "transaction_id": f"{outcome}-txn", "amount": 100.0}
            result = routes.apply_job(ApplicationCreate(student="John", job_id=101))
            self.assertFalse(result["application_created"])
            self.assertEqual(result["payment_status"], status)
        connection = self.connection()
        self.assertEqual(connection.execute("SELECT COUNT(*) FROM applications").fetchone()[0], 0)
        self.assertEqual(connection.execute("SELECT COUNT(*) FROM payments").fetchone()[0], 2)
        connection.close()

    def test_duplicate_and_missing_records_are_rejected(self):
        routes.payment_service.charge_application = lambda: {"status": "SUCCESS", "transaction_id": "duplicate-txn", "amount": 100.0}
        routes.apply_job(ApplicationCreate(student="John", job_id=101))
        with self.assertRaises(HTTPException) as duplicate:
            routes.apply_job(ApplicationCreate(student="John", job_id=101))
        self.assertEqual(duplicate.exception.status_code, 409)
        with self.assertRaises(HTTPException) as missing_student:
            routes.predict(PredictionRequest(student_id=99999, job_id=101))
        self.assertEqual(missing_student.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
