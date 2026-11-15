#!/usr/bin/env python3
"""Read-only, source-pinned review of seven DE navigation-only subject areas.

Structural coverage/boundary assertions only. No vendor lessons, credentials,
provider grading, learner assignments or technical mastery are certified.
"""
import hashlib
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent.parent
SUBJECTS = (
    ("03. Database Design and Modeling", "03-databases-and-modeling",
     "215c6ddf41469f358b94136171ff987cd93a3e3e", "4db710f5f27e287371cc7b4c0305b6ff911e36de"),
    ("04. Data Pipelines and ETL", "04-data-pipelines",
     "05a997b9d4c09d5ea21a16bdcb213b10fcdc83be", "218394bcb218acbcc4bb7689077e73b5f8e8c270"),
    ("05. Apache Spark", "05-apache-spark",
     "ba8cd95c358edc8944a701cccca115c471a8a3eb", "5a26de48654861b7d4c9fef15e622a6e18bde59f"),
    ("06. Cloud and Orchestration", "06-cloud-and-orchestration",
     "11f33ad7d1a3b375b635fb7690d7e733862654a2", "5a0fa8f0f4932f40d2f465c13403969068568479"),
    ("07. Data System Design", "07-system-design",
     "f3cf7358f2e0f94c5fa1b963abcc0621894a9c32", "b448fe0bfcd999d407c9d883629f86395030d2d0"),
    ("08. Projects", "08-projects",
     "e53094174369888c49abbb80257ec1ea16612a61", "decd51027e1e60142ff661eca76868aaf8315aef"),
    ("09. Interview Preparation", "09-interview-preparation",
     "c02fb34faf5c712cdd58591e4075aa4f7cbb8b87", "fa722660dea3999723d34df9e54d56781e97d812"),
)
ARCHIVE_PREFIX = "99. Reference Materials/Legacy Journey Snapshot"
DE_EXAMPLES = {
    "99. Reference Materials/Original Mastery Snapshot/2. Python Mastry/6. Python for Data Engineering/03. Python and databases.md":
        "02af93e471c9f933274981230981102c72e76d69",
    "99. Reference Materials/Original Mastery Snapshot/2. Python Mastry/6. Python for Data Engineering/04. Build an idempotent ETL pipeline.md":
        "fc859b44748d06318f2d0bdb4ae36266715253e7",
    "99. Reference Materials/Original Mastery Snapshot/2. Python Mastry/6. Python for Data Engineering/05. Testing and data quality.md":
        "05b4ff35d2666ef5908237686f2a517dd718301a",
    "99. Reference Materials/Original Mastery Snapshot/2. Python Mastry/6. Python for Data Engineering/06. From pandas to PySpark and Airflow.md":
        "17b999bcc639f184c5ca7bac4c3a325d4d05e763",
}

def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def exact_file(relative, expected_sha):
    p = ROOT / relative
    data = p.read_bytes()
    got = git_blob_sha(data)
    if got != expected_sha:
        raise AssertionError(f"Git blob mismatch: {relative}: {got} != {expected_sha}")
    return data.decode("utf-8-sig")

class SevenSubjectsNavigationPrimaryGap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nav = {}
        cls.legacy = {}
        for name, old, nav_sha, old_sha in SUBJECTS:
            cls.nav[name] = exact_file(f"{name}/README.md", nav_sha)
            cls.legacy[name] = exact_file(f"{ARCHIVE_PREFIX}/{old}/README.md", old_sha)
        cls.examples = {p: exact_file(p, sha) for p, sha in DE_EXAMPLES.items()}

    def test_01_all_eighteen_archive_and_navigation_git_blobs_verified(self):
        self.assertEqual(len(self.nav) + len(self.legacy) + len(self.examples), 18)

    def test_02_seven_subjects_have_only_navigation_readme_files(self):
        for name, *_ in SUBJECTS:
            present = sorted(p.relative_to(ROOT / name).as_posix()
                             for p in (ROOT / name).rglob("*") if p.is_file())
            self.assertEqual(present, ["README.md"], name)

    def test_03_all_seven_navigations_explicitly_disclaim_curriculum_completion(self):
        for name, s in self.nav.items():
            self.assertIn("not a claim that the curriculum has been completed", s, name)
            self.assertIn("A canonical", s, name)
            self.assertIn("original", s.lower(), name)

    def test_04_all_seven_readme_links_reach_existing_legacy_snapshot_root(self):
        for name, s in self.nav.items():
            self.assertIn("../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/", s, name)
        self.assertTrue((ROOT / ARCHIVE_PREFIX).is_dir())

    def test_05_legacy_readmes_are_outlines_not_verified_course_or_lab_artifacts(self):
        for name, text in self.legacy.items():
            self.assertTrue(text.lstrip().startswith("# "), name)
            self.assertNotIn("**Academy platform completion:** Verified", text, name)
            self.assertNotIn("Learner independently solved:", text, name)
        self.assertIn("Topics: OLTP vs OLAP", self.legacy[SUBJECTS[0][0]])
        self.assertIn("Topics: ETL/ELT", self.legacy[SUBJECTS[1][0]])
        self.assertIn("Topics: distributed execution", self.legacy[SUBJECTS[2][0]])
        self.assertIn("Topics: object storage", self.legacy[SUBJECTS[3][0]])

    def test_06_source_projects_are_explicitly_candidates_not_built(self):
        text = self.legacy["08. Projects"]
        self.assertIn("Candidate projects — not yet built", text)
        self.assertIn("synthetic data", text)
        self.assertIn("pipeline", text)

    def test_07_pipeline_example_is_archived_outside_pipeline_navigation(self):
        p = next(p for p in DE_EXAMPLES if "/04. Build an idempotent ETL pipeline.md" in p)
        source = self.examples[p]
        self.assertIn("def extract(path, day):", source)
        self.assertIn("def transform(rows):", source)
        self.assertIn("def load(connection, day, rows):", source)
        self.assertIn("DELETE FROM fact_orders WHERE order_date = ?", source)
        self.assertIn("with connection:", source)
        self.assertNotIn("04. Build an idempotent ETL pipeline.md", self.nav["04. Data Pipelines and ETL"])

    def test_08_data_quality_is_separate_from_source_etl_load(self):
        good = next(v for k, v in self.examples.items() if "/05. Testing and data quality.md" in k)
        etl = next(v for k, v in self.examples.items() if "/04. Build an idempotent ETL pipeline.md" in k)
        self.assertIn("def normalize_status(raw):", good)
        self.assertIn("def to_amount(text):", good)
        self.assertNotIn("normalize_status(row", etl)
        self.assertNotIn("to_amount(row", etl)

    def test_09_archived_spark_and_airflow_are_not_proven_production_executions(self):
        p74 = next(v for k, v in self.examples.items() if "/06. From pandas to PySpark and Airflow.md" in k)
        self.assertIn("optional external packages", p74)
        self.assertIn("not executed in the source PDF", p74)
        self.assertIn("NotImplementedError('Connect a warehouse MERGE here')", p74)
        self.assertIn("spark.stop()", p74)
        self.assertNotIn("06. From pandas to PySpark and Airflow.md", self.nav["05. Apache Spark"])
        self.assertNotIn("06. From pandas to PySpark and Airflow.md", self.nav["06. Cloud and Orchestration"])

    def test_10_parameterization_example_is_attributed_to_python_not_de_section(self):
        db = next(v for k, v in self.examples.items() if "/03. Python and databases.md" in k)
        self.assertIn("parameter", db.lower())
        self.assertIn("unsafe", db)
        self.assertIn("with connection:", db)
        self.assertNotIn("03. Python and databases.md", self.nav["03. Database Design and Modeling"])

    def test_11_no_subject_navigation_declares_actual_project_or_course_grade(self):
        for name, nav in self.nav.items():
            self.assertNotIn("official answer verified", nav.lower(), name)
            self.assertNotIn("independently solved", nav.lower(), name)
            self.assertNotIn("course complete", nav.lower(), name)

    def test_12_no_subject_specific_foundation_files_are_present(self):
        for name, *_ in SUBJECTS:
            self.assertFalse((ROOT / name / "0. Foundation Notes.md").exists(), name)
            self.assertFalse((ROOT / name / "assignments").exists(), name)

if __name__ == "__main__":
    unittest.main(verbosity=2)
