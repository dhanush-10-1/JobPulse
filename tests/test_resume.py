import json
import sys
import types
import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import Mock, patch

from jobpulse.ai.resume import (
    EducationItem,
    ResumeExtractionError,
    ResumeProfile,
    ExperienceItem,
    ProjectItem,
    extract_resume_profile,
)


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


class ResumeExtractionTests(unittest.TestCase):
    def setUp(self):
        self.generate_content = Mock()
        self.client = SimpleNamespace(
            provider_client=SimpleNamespace(
                models=SimpleNamespace(generate_content=self.generate_content)
            ),
            model="configured-resume-model",
        )

    def valid_payload(self):
        return {
            "name": "Alex Smith",
            "summary": "Backend engineer",
            "skills": ["Python"],
            "technologies": ["PostgreSQL"],
            "experience": [{
                "company": "DataWorks",
                "role": "Engineer",
                "duration": "2022-2026",
                "description": "Built APIs",
            }],
            "education": [{
                "institution": "University",
                "degree": "BSc",
                "field": "Computer Science",
                "year": "2020",
            }],
            "projects": [{
                "name": "JobPulse",
                "description": "Resume intelligence platform",
                "technologies": ["Python"],
            }],
        }

    def test_successful_extraction_uses_structured_schema(self):
        self.generate_content.return_value = SimpleNamespace(
            text=json.dumps(self.valid_payload())
        )
        with fake_genai_types(), patch(
            "jobpulse.ai.resume.AIClient", return_value=self.client
        ):
            result = extract_resume_profile("Alex Smith\nBackend engineer")

        self.assertIsInstance(result, ResumeProfile)
        self.assertEqual(result.name, "Alex Smith")
        self.assertEqual(result.skills, ["Python"])
        self.assertIsInstance(result.experience[0], ExperienceItem)
        self.assertIsInstance(result.education[0], EducationItem)
        self.assertIsInstance(result.projects[0], ProjectItem)
        call = self.generate_content.call_args
        self.assertEqual(call.kwargs["model"], "configured-resume-model")
        self.assertEqual(call.kwargs["config"].values["response_mime_type"], "application/json")
        self.assertIs(call.kwargs["config"].values["response_schema"], ResumeProfile)

    def test_blank_input_is_rejected(self):
        with patch("jobpulse.ai.resume.AIClient") as client:
            for value in ("", "   "):
                with self.subTest(value=value):
                    with self.assertRaisesRegex(ValueError, "non-empty"):
                        extract_resume_profile(value)
            client.assert_not_called()

    def test_malformed_provider_response_raises_application_error(self):
        self.generate_content.return_value = SimpleNamespace(text="not-json")
        with fake_genai_types(), patch(
            "jobpulse.ai.resume.AIClient", return_value=self.client
        ):
            with self.assertRaises(ResumeExtractionError):
                extract_resume_profile("Resume text")

    def test_unexpected_provider_shape_raises_application_error(self):
        payload = self.valid_payload()
        payload["skills"] = "Python"
        self.generate_content.return_value = SimpleNamespace(text=json.dumps(payload))
        with fake_genai_types(), patch(
            "jobpulse.ai.resume.AIClient", return_value=self.client
        ):
            with self.assertRaises(ResumeExtractionError):
                extract_resume_profile("Resume text")

    def test_provider_failure_raises_application_error(self):
        self.generate_content.side_effect = RuntimeError("provider failure")
        with fake_genai_types(), patch(
            "jobpulse.ai.resume.AIClient", return_value=self.client
        ):
            with self.assertRaises(ResumeExtractionError):
                extract_resume_profile("Resume text")


if __name__ == "__main__":
    unittest.main()