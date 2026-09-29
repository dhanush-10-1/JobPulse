import unittest
from types import SimpleNamespace
from uuid import UUID
from unittest.mock import patch

from jobpulse.ai.matching import MatchError, MatchResult, match_resume_to_job
from jobpulse.ai.resume import ResumeProfile


RESUME_ID = UUID("11111111-1111-1111-1111-111111111111")
JOB_ID = 1


class MatchingTests(unittest.TestCase):
    def setUp(self):
        self.profile = ResumeProfile(
            name="Alex Smith",
            skills=["Python", "SQL"],
            technologies=["PostgreSQL", "FastAPI"],
            experience=[{
                "company": "DataWorks",
                "role": "Engineer",
                "duration": "5 years",
                "description": "Built data services",
            }],
        )
        self.job = SimpleNamespace(id=JOB_ID)
        self.enrichment = {"skills": ["python", "PostgreSQL", "Kafka"], "experience_years": 4}

    def match(self, enrichment=None, resume_embedding=None, job_embedding=None):
        with patch("jobpulse.ai.matching.get_resume_profile", return_value=self.profile), patch(
            "jobpulse.ai.matching.get_job_by_id", return_value=self.job
        ), patch(
            "jobpulse.ai.matching.get_job_ai_enrichment",
            return_value=self.enrichment if enrichment is None else enrichment,
        ), patch(
            "jobpulse.ai.matching.get_resume_embedding",
            return_value=resume_embedding or {"embedding": [1.0, 0.0]},
        ), patch(
            "jobpulse.ai.matching.get_job_embedding",
            return_value=job_embedding or {"embedding": [1.0, 0.0]},
        ):
            return match_resume_to_job(RESUME_ID, JOB_ID)

    def test_strong_match(self):
        result = self.match()

        self.assertIsInstance(result, MatchResult)
        self.assertEqual(result.similarity, 1.0)
        self.assertEqual(result.matched_skills, ["python", "PostgreSQL"])
        self.assertEqual(result.missing_skills, ["Kafka"])
        self.assertTrue(result.experience_match)
        self.assertGreater(result.match_score, 70)

    def test_partial_match(self):
        result = self.match(job_embedding={"embedding": [1.0, 1.0]})

        self.assertAlmostEqual(result.similarity, 0.707106, places=5)
        self.assertEqual(result.matched_skills, ["python", "PostgreSQL"])
        self.assertEqual(result.missing_skills, ["Kafka"])

    def test_high_skill_coverage_increases_score(self):
        high = self.match()
        self.enrichment = {"skills": ["Python", "Kafka"], "experience_years": None}
        low = self.match()

        self.assertGreater(high.match_score, low.match_score)

    def test_low_skill_coverage_produces_lower_score(self):
        self.enrichment = {
            "skills": ["Python", "Kafka", "Rust", "Go"],
            "experience_years": None,
        }

        result = self.match()

        self.assertLess(result.match_score, 70)

    def test_experience_match_increases_score(self):
        matched = self.match()
        self.enrichment = {"skills": ["Python"], "experience_years": 10}
        mismatched = self.match()

        self.assertGreater(matched.match_score, mismatched.match_score)

    def test_experience_mismatch_has_negative_contribution(self):
        self.enrichment = {"skills": ["Python"], "experience_years": 10}

        result = self.match()
        unknown = self.match(
            enrichment={"skills": ["Python"], "experience_years": None}
        )

        self.assertFalse(result.experience_match)
        self.assertLess(result.match_score, unknown.match_score)

    def test_unknown_experience_does_not_change_score(self):
        unknown = self.match(enrichment={"skills": ["Python"], "experience_years": None})
        self.enrichment = {"skills": ["Python"], "experience_years": 0}
        matched = self.match()

        self.assertIsNone(unknown.experience_match)
        self.assertGreater(matched.match_score, unknown.match_score)

    def test_no_required_skills_uses_zero_skill_coverage(self):
        result = self.match(enrichment={"skills": [], "experience_years": None})

        self.assertEqual(result.matched_skills, [])
        self.assertEqual(result.missing_skills, [])
        self.assertEqual(result.match_score, 50.0)

    def test_score_is_clamped_to_bounds(self):
        result = self.match(
            enrichment={"skills": ["Python"], "experience_years": 0},
            resume_embedding={"embedding": [100.0, 0.0]},
            job_embedding={"embedding": [-100.0, 0.0]},
        )

        self.assertGreaterEqual(result.match_score, 0.0)
        self.assertLessEqual(result.match_score, 100.0)

    def test_resume_technology_matches_job_skill(self):
        self.profile.technologies.append("Kafka")

        result = self.match()

        self.assertEqual(result.matched_skills, ["python", "PostgreSQL", "Kafka"])
        self.assertEqual(result.missing_skills, [])

    def test_aliases_match_and_return_job_terminology(self):
        self.profile.skills = ["REST APIs"]
        self.profile.technologies = ["PostgreSQL", "FastAPI"]
        self.enrichment = {
            "skills": ["HTTP/REST", "Postgres", "Fast API"],
            "experience_years": None,
        }

        result = self.match()

        self.assertEqual(result.matched_skills, ["HTTP/REST", "Postgres", "Fast API"])
        self.assertEqual(result.missing_skills, [])

    def test_case_and_whitespace_differences_match(self):
        self.profile.skills = ["  PYTHON  "]
        self.profile.technologies = ["  postgresql"]
        self.enrichment = {"skills": ["python", "PostgreSQL"], "experience_years": None}

        result = self.match()

        self.assertEqual(result.matched_skills, ["python", "PostgreSQL"])
        self.assertEqual(result.missing_skills, [])

    def test_genuinely_missing_skill_remains_missing(self):
        self.enrichment = {"skills": ["Python", "Rust"], "experience_years": None}

        result = self.match()

        self.assertEqual(result.matched_skills, ["Python"])
        self.assertEqual(result.missing_skills, ["Rust"])

    @patch("jobpulse.ai.matching.get_resume_profile", return_value=None)
    def test_missing_resume(self, get_profile):
        with self.assertRaisesRegex(MatchError, "resume profile not found"):
            match_resume_to_job(RESUME_ID, JOB_ID)

    @patch("jobpulse.ai.matching.get_resume_profile")
    @patch("jobpulse.ai.matching.get_job_by_id", return_value=None)
    def test_missing_job(self, get_job, get_profile):
        get_profile.return_value = self.profile
        with self.assertRaisesRegex(MatchError, "job not found"):
            match_resume_to_job(RESUME_ID, JOB_ID)

    @patch("jobpulse.ai.matching.get_resume_embedding", return_value=None)
    @patch("jobpulse.ai.matching.get_job_embedding")
    @patch("jobpulse.ai.matching.get_job_ai_enrichment")
    @patch("jobpulse.ai.matching.get_job_by_id")
    @patch("jobpulse.ai.matching.get_resume_profile")
    def test_missing_embedding(
        self, get_profile, get_job, get_enrichment, get_job_embedding, get_resume_embedding
    ):
        get_profile.return_value = self.profile
        get_job.return_value = self.job
        get_enrichment.return_value = self.enrichment
        with self.assertRaisesRegex(MatchError, "resume embedding not found"):
            match_resume_to_job(RESUME_ID, JOB_ID)

    @patch("jobpulse.ai.matching.get_job_embedding", return_value=None)
    @patch("jobpulse.ai.matching.get_resume_embedding")
    @patch("jobpulse.ai.matching.get_job_ai_enrichment")
    @patch("jobpulse.ai.matching.get_job_by_id")
    @patch("jobpulse.ai.matching.get_resume_profile")
    def test_missing_job_embedding(
        self, get_profile, get_job, get_enrichment, get_resume_embedding, get_job_embedding
    ):
        get_profile.return_value = self.profile
        get_job.return_value = self.job
        get_enrichment.return_value = self.enrichment
        get_resume_embedding.return_value = {"embedding": [1.0, 0.0]}
        with self.assertRaisesRegex(MatchError, "job embedding not found"):
            match_resume_to_job(RESUME_ID, JOB_ID)

    @patch("jobpulse.ai.matching.get_job_ai_enrichment", return_value=None)
    @patch("jobpulse.ai.matching.get_job_by_id")
    @patch("jobpulse.ai.matching.get_resume_profile")
    def test_missing_ai_enrichment(self, get_profile, get_job, get_enrichment):
        get_profile.return_value = self.profile
        get_job.return_value = self.job
        with self.assertRaisesRegex(MatchError, "job enrichment not found"):
            match_resume_to_job(RESUME_ID, JOB_ID)

    def test_experience_match_is_unknown_without_explicit_resume_years(self):
        self.profile.experience[0].duration = ""
        result = self.match()

        self.assertIsNone(result.experience_match)
        self.assertIn("Experience alignment: not determined", result.explanation)

    def test_explanation_includes_overall_score_and_strengths(self):
        result = self.match()

        self.assertIn("Overall match score:", result.explanation)
        self.assertIn("with cosine similarity", result.explanation)
        self.assertIn("Matched strengths: python, PostgreSQL", result.explanation)
        self.assertIn("Missing skills: Kafka", result.explanation)
        self.assertIn("matches the stated requirement", result.explanation)

    def test_explanation_handles_no_matched_skills(self):
        self.profile.skills = []
        self.profile.technologies = []
        self.enrichment = {"skills": ["Rust"], "experience_years": None}

        result = self.match()

        self.assertIn("Matched strengths: none identified", result.explanation)
        self.assertIn("Missing skills: Rust", result.explanation)

    def test_explanation_handles_no_missing_skills(self):
        self.enrichment = {"skills": ["Python"], "experience_years": None}

        result = self.match()

        self.assertIn("Missing skills: none identified", result.explanation)

    def test_explanation_handles_no_required_job_skills(self):
        result = self.match(enrichment={"skills": [], "experience_years": None})

        self.assertIn("No required job skills identified", result.explanation)

    def test_explanation_handles_experience_mismatch(self):
        result = self.match(enrichment={"skills": ["Python"], "experience_years": 10})

        self.assertIn("does not match the stated requirement", result.explanation)


if __name__ == "__main__":
    unittest.main()