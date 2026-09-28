import unittest
from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient

import api
from jobpulse.ingestion.models import Job


class APISemanticSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database_patch = patch("api.ensure_job_freshness_schema")
        cls.database_patch.start()
        cls.client = TestClient(api.app)

    @classmethod
    def tearDownClass(cls):
        cls.database_patch.stop()

    def test_valid_query_returns_serialized_jobs_and_metadata(self):
        job = Job(
            "Backend Engineer",
            "JobPulse",
            "Remote",
            date(2026, 9, 28),
            "https://example.test/jobs/1",
        )
        matches = [{"job": job, "distance": 0.123, "similarity": 0.877}]
        with patch("api.semantic_search", return_value=matches) as search:
            response = self.client.get(
                "/jobs/semantic-search", params={"q": "backend", "top_k": 5}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "query": "backend",
            "results": [{
                "job": job.to_dict(),
                "distance": 0.123,
                "similarity": 0.877,
            }],
        })
        search.assert_called_once_with("backend", top_k=5)

    def test_blank_query_returns_400(self):
        with patch("api.semantic_search") as search:
            response = self.client.get("/jobs/semantic-search?q=   ")

        self.assertEqual(response.status_code, 400)
        search.assert_not_called()

    def test_top_k_must_be_between_one_and_fifty(self):
        for top_k in (0, 51):
            with self.subTest(top_k=top_k):
                response = self.client.get(
                    "/jobs/semantic-search", params={"q": "backend", "top_k": top_k}
                )
                self.assertEqual(response.status_code, 400)

    def test_service_failure_returns_generic_502(self):
        with patch(
            "api.semantic_search",
            side_effect=RuntimeError("provider or database failure"),
        ):
            response = self.client.get("/jobs/semantic-search?q=backend")

        self.assertEqual(response.status_code, 502)
        self.assertEqual(
            response.json()["detail"],
            "Semantic search is temporarily unavailable",
        )
        self.assertNotIn("provider or database failure", response.text)


if __name__ == "__main__":
    unittest.main()
