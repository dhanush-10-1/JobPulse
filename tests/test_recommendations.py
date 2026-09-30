import unittest
from unittest.mock import patch
from uuid import UUID

from jobpulse.ai.matching import MatchError, MatchResult
from jobpulse.ai.recommendations import recommend_jobs


RESUME_ID = UUID("11111111-1111-1111-1111-111111111111")


def result(job_id, match_score, similarity):
    return MatchResult(
        resume_id=RESUME_ID,
        job_id=job_id,
        similarity=similarity,
        matched_skills=[],
        missing_skills=[],
        experience_match=None,
        explanation="",
        match_score=match_score,
    )


class RecommendationTests(unittest.TestCase):
    @patch("jobpulse.ai.recommendations.match_resume_to_job")
    @patch("jobpulse.ai.recommendations.get_active_enriched_job_ids", return_value=[1, 2, 3])
    @patch("jobpulse.ai.recommendations.get_resume_profile", return_value=object())
    def test_successful_recommendation_ranking(self, get_profile, get_jobs, match):
        match.side_effect = [result(1, 70, 0.8), result(2, 90, 0.4), result(3, 80, 0.9)]

        recommendations = recommend_jobs(RESUME_ID)

        self.assertEqual([item.job_id for item in recommendations], [2, 3, 1])

    @patch("jobpulse.ai.recommendations.match_resume_to_job")
    @patch("jobpulse.ai.recommendations.get_active_enriched_job_ids", return_value=[1, 2, 3])
    @patch("jobpulse.ai.recommendations.get_resume_profile", return_value=object())
    def test_top_k_limits_results(self, get_profile, get_jobs, match):
        match.side_effect = [result(1, 70, 0.8), result(2, 90, 0.4), result(3, 80, 0.9)]

        recommendations = recommend_jobs(RESUME_ID, top_k=2)

        self.assertEqual([item.job_id for item in recommendations], [2, 3])

    @patch("jobpulse.ai.recommendations.match_resume_to_job")
    @patch("jobpulse.ai.recommendations.get_active_enriched_job_ids", return_value=[1, 2])
    @patch("jobpulse.ai.recommendations.get_resume_profile", return_value=object())
    def test_equal_match_scores_use_similarity(self, get_profile, get_jobs, match):
        match.side_effect = [result(1, 85, 0.4), result(2, 85, 0.9)]

        recommendations = recommend_jobs(RESUME_ID)

        self.assertEqual([item.job_id for item in recommendations], [2, 1])

    @patch("jobpulse.ai.recommendations.get_active_enriched_job_ids", return_value=[])
    @patch("jobpulse.ai.recommendations.get_resume_profile", return_value=object())
    def test_no_eligible_jobs(self, get_profile, get_jobs):
        self.assertEqual(recommend_jobs(RESUME_ID), [])

    @patch("jobpulse.ai.recommendations.get_resume_profile", return_value=None)
    def test_missing_resume(self, get_profile):
        with self.assertRaisesRegex(MatchError, "resume profile not found"):
            recommend_jobs(RESUME_ID)

    @patch("jobpulse.ai.recommendations.get_resume_profile", return_value=object())
    def test_invalid_top_k(self, get_profile):
        for top_k in (0, 51, True):
            with self.subTest(top_k=top_k), self.assertRaises(ValueError):
                recommend_jobs(RESUME_ID, top_k=top_k)


if __name__ == "__main__":
    unittest.main()