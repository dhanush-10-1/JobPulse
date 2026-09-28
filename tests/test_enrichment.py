import json
import sys
import types
import unittest
from contextlib import contextmanager
from datetime import date
from types import SimpleNamespace
from unittest.mock import Mock, patch

from jobpulse.ai.enrichment import (
    EnrichmentGenerationError,
    EnrichmentResult,
    GEMINI_ENRICHMENT_RESPONSE_SCHEMA,
    generate_and_save_job_enrichment,
)
from jobpulse.ingestion.models import Job


class FakeGenerateContentConfig:
    def __init__(self, **kwargs):
        self.values = kwargs


@contextmanager
def fake_genai_types():
    fake_types = types.ModuleType("google.genai.types")
    fake_types.GenerateContentConfig = FakeGenerateContentConfig
    fake_genai = types.ModuleType("google.genai")
    fake_genai.types = fake_types
    fake_google = types.ModuleType("google")
    fake_google.genai = fake_genai
    with patch.dict(
        sys.modules,
        {
            "google": fake_google,
            "google.genai": fake_genai,
            "google.genai.types": fake_types,
        },
    ):
        yield


class EnrichmentWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.generate_content = Mock()
        self.client = SimpleNamespace(
            provider_client=SimpleNamespace(
                models=SimpleNamespace(generate_content=self.generate_content)
            ),
            model="configured-gemini-model",
        )
        self.job = Job(
            "Backend Engineer",
            "JobPulse",
            "Remote",
            date.today(),
            "https://example.test/jobs/1",
            description="Build APIs for job seekers.",
            employment_type="Full-time",
            salary="$100k",
        )
        self.job.id = 1

    def valid_payload(self):
        return {
            "skills": ["Python", "PostgreSQL"],
            "category": "Software Engineering",
            "seniority": "Senior",
            "experience_years": 4,
            "employment_type": "Full-time",
            "responsibilities": ["Build APIs"],
            "requirements": ["Python experience"],
            "summary": "A backend engineering role.",
        }

    def test_successful_structured_enrichment_uses_configured_model(self):
        self.generate_content.return_value = SimpleNamespace(
            text=json.dumps(self.valid_payload())
        )
        with fake_genai_types(), patch(
            "jobpulse.ai.enrichment.save_job_ai_enrichment"
        ) as save:
            result = generate_and_save_job_enrichment(self.job, self.client)

        self.assertIsInstance(result, EnrichmentResult)
        self.assertEqual(result.skills, ["Python", "PostgreSQL"])
        call = self.generate_content.call_args
        self.assertEqual(call.kwargs["model"], "configured-gemini-model")
        self.assertIn("Description: Build APIs", call.kwargs["contents"])
        self.assertEqual(
            call.kwargs["config"].values["response_mime_type"],
            "application/json",
        )
        schema = call.kwargs["config"].values["response_schema"]
        for field_name in ("category", "seniority", "employment_type", "summary"):
            self.assertEqual(schema["properties"][field_name]["type"], "string")
        self.assertIs(call.kwargs["config"].values["response_schema"], GEMINI_ENRICHMENT_RESPONSE_SCHEMA)
        save.assert_called_once()

    def test_empty_scalar_strings_become_none(self):
        payload = self.valid_payload()
        payload.update(
            {"category": "", "seniority": "", "employment_type": "", "summary": ""}
        )
        self.generate_content.return_value = SimpleNamespace(text=json.dumps(payload))
        with fake_genai_types(), patch(
            "jobpulse.ai.enrichment.save_job_ai_enrichment"
        ):
            result = generate_and_save_job_enrichment(self.job, self.client)

        self.assertIsNone(result.category)
        self.assertEqual(result.seniority, "Unknown")
        self.assertEqual(result.employment_type, "Unknown")
        self.assertIsNone(result.summary)

    def test_seniority_and_experience_are_normalized(self):
        payload = self.valid_payload()
        payload.update({"seniority": "4+ years", "experience_years": None})
        self.job.description = "Requires 4+ years of backend experience."
        self.generate_content.return_value = SimpleNamespace(text=json.dumps(payload))
        with fake_genai_types(), patch(
            "jobpulse.ai.enrichment.save_job_ai_enrichment"
        ):
            result = generate_and_save_job_enrichment(self.job, self.client)

        self.assertEqual(result.seniority, "Unknown")
        self.assertEqual(result.experience_years, 4)

    def test_unknown_employment_type_is_not_inferred(self):
        payload = self.valid_payload()
        payload["employment_type"] = "Back end, Database"
        self.generate_content.return_value = SimpleNamespace(text=json.dumps(payload))
        with fake_genai_types(), patch(
            "jobpulse.ai.enrichment.save_job_ai_enrichment"
        ):
            result = generate_and_save_job_enrichment(self.job, self.client)

        self.assertEqual(result.employment_type, "Unknown")

    def test_invalid_structured_output_is_rejected(self):
        payload = self.valid_payload()
        payload["skills"] = "Python"
        self.generate_content.return_value = SimpleNamespace(text=json.dumps(payload))
        with fake_genai_types(), patch(
            "jobpulse.ai.enrichment.save_job_ai_enrichment"
        ) as save:
            with self.assertRaises(EnrichmentGenerationError):
                generate_and_save_job_enrichment(self.job, self.client)

        save.assert_not_called()

    def test_api_failure_becomes_application_error(self):
        self.generate_content.side_effect = RuntimeError("provider failure")
        with fake_genai_types():
            with self.assertRaises(EnrichmentGenerationError):
                generate_and_save_job_enrichment(self.job, self.client)

    def test_persistence_records_model_and_completed_status(self):
        self.generate_content.return_value = SimpleNamespace(
            text=json.dumps(self.valid_payload())
        )
        with fake_genai_types(), patch(
            "jobpulse.ai.enrichment.save_job_ai_enrichment"
        ) as save:
            generate_and_save_job_enrichment(self.job, self.client)

        save.assert_called_once()
        args, kwargs = save.call_args
        self.assertEqual(args[0], 1)
        self.assertIsInstance(args[1], EnrichmentResult)
        self.assertEqual(kwargs["model"], "configured-gemini-model")
        self.assertEqual(kwargs["status"], "completed")
        self.assertIsNotNone(kwargs["enriched_at"])


if __name__ == "__main__":
    unittest.main()
