import unittest
from uuid import UUID
from unittest.mock import patch

from fastapi.testclient import TestClient

import api
from jobpulse.ai.matching import MatchError, MatchResult


class APIMatchingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database_patch = patch("api.ensure_job_freshness_schema")
        cls.database_patch.start()
        cls.client = TestClient(api.app)

    @classmethod
    def tearDownClass(cls):
        cls.database_patch.stop()

    def result(self):
        return MatchResult(
            resume_id=UUID("11111111-1111-1111-1111-111111111111"),
            job_id=7,
            similarity=0.9,
            match_score=88.0,
            matched_skills=["Python"],
            missing_skills=["Kafka"],
            experience_match=True,
            explanation="Overall match score: 88.0/100.",
        )

    def test_successful_match_returns_complete_result(self):
        result = self.result()
        with patch("api.match_resume_to_job", return_value=result) as match:
            response = self.client.get(
                "/resumes/11111111-1111-1111-1111-111111111111/match/7"
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), result.model_dump(mode="json"))
        match.assert_called_once_with(result.resume_id, 7)

    def test_missing_resume_job_profile_or_embedding_returns_404(self):
        with patch(
            "api.match_resume_to_job",
            side_effect=MatchError("internal missing data details"),
        ):
            response = self.client.get(
                "/resumes/11111111-1111-1111-1111-111111111111/match/7"
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Resume, job, or matching data not found")
        self.assertNotIn("internal missing data details", response.text)

    def test_invalid_resume_id_returns_validation_error(self):
        with patch("api.match_resume_to_job") as match:
            response = self.client.get("/resumes/not-a-uuid/match/7")

        self.assertEqual(response.status_code, 422)
        match.assert_not_called()

    def test_invalid_job_id_returns_validation_error(self):
        with patch("api.match_resume_to_job") as match:
            response = self.client.get(
                "/resumes/11111111-1111-1111-1111-111111111111/match/not-an-int"
            )

        self.assertEqual(response.status_code, 422)
        match.assert_not_called()

    def test_unexpected_service_failure_returns_generic_502(self):
        with patch(
            "api.match_resume_to_job",
            side_effect=RuntimeError("database credentials or traceback"),
        ):
            response = self.client.get(
                "/resumes/11111111-1111-1111-1111-111111111111/match/7"
            )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(
            response.json()["detail"],
            "Resume-to-job matching is temporarily unavailable",
        )
        self.assertNotIn("database credentials or traceback", response.text)


if __name__ == "__main__":
    unittest.main()