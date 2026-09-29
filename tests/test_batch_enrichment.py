import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from jobpulse.ai.batch_enrichment import enrich_jobs_batch


def job(job_id):
    return SimpleNamespace(id=job_id, description=f"Description {job_id}")


class BatchEnrichmentTests(unittest.TestCase):
    @patch("jobpulse.ai.batch_enrichment.generate_and_save_job_enrichment")
    @patch("jobpulse.ai.batch_enrichment.get_jobs_for_enrichment_batch")
    def test_eligible_jobs_are_selected_with_model(self, select, enrich):
        select.return_value = [{"job": job(1), "status": None, "model": None}]

        stats = enrich_jobs_batch(3, model="model-a")

        select.assert_called_once_with(3, model="model-a")
        enrich.assert_called_once()
        self.assertEqual(stats.selected, 1)

    @patch("jobpulse.ai.batch_enrichment.generate_and_save_job_enrichment")
    @patch("jobpulse.ai.batch_enrichment.get_jobs_for_enrichment_batch")
    def test_completed_jobs_are_skipped_for_current_model(self, select, enrich):
        select.return_value = [
            {"job": job(1), "status": "completed", "model": "model-a"}
        ]

        stats = enrich_jobs_batch(3, model="model-a")

        enrich.assert_not_called()
        self.assertEqual(
            stats.as_dict(),
            {"selected": 1, "succeeded": 0, "failed": 0, "skipped": 1},
        )

    @patch("jobpulse.ai.batch_enrichment.generate_and_save_job_enrichment")
    @patch("jobpulse.ai.batch_enrichment.get_jobs_for_enrichment_batch")
    def test_successful_enrichment_is_counted(self, select, enrich):
        select.return_value = [{"job": job(1), "status": None, "model": None}]

        stats = enrich_jobs_batch(1, client=Mock(), model="model-a")

        self.assertEqual(stats.succeeded, 1)
        self.assertEqual(stats.failed, 0)

    @patch("jobpulse.ai.batch_enrichment.save_job_ai_enrichment")
    @patch("jobpulse.ai.batch_enrichment.generate_and_save_job_enrichment")
    @patch("jobpulse.ai.batch_enrichment.get_jobs_for_enrichment_batch")
    def test_one_job_failure_does_not_stop_batch(self, select, enrich, save_failed):
        select.return_value = [
            {"job": job(1), "status": None, "model": None},
            {"job": job(2), "status": None, "model": None},
        ]
        enrich.side_effect = [RuntimeError("bad job"), None]

        stats = enrich_jobs_batch(2, model="model-a")

        self.assertEqual(stats.succeeded, 1)
        self.assertEqual(stats.failed, 1)
        save_failed.assert_called_once()
        self.assertEqual(save_failed.call_args.kwargs["status"], "failed")

    @patch("jobpulse.ai.batch_enrichment.generate_and_save_job_enrichment")
    @patch("jobpulse.ai.batch_enrichment.get_jobs_for_enrichment_batch")
    def test_different_model_is_not_skipped(self, select, enrich):
        select.return_value = [
            {"job": job(1), "status": "completed", "model": "old-model"}
        ]

        stats = enrich_jobs_batch(1, model="model-a")

        enrich.assert_called_once()
        self.assertEqual(stats.succeeded, 1)
        self.assertEqual(stats.skipped, 0)


if __name__ == "__main__":
    unittest.main()