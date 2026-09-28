import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from jobpulse.ai.embeddings import (
    EmbeddingGenerationError,
    build_job_embedding_text,
    create_embedding,
    generate_and_save_job_embedding,
)
from jobpulse.ingestion.models import Job


class EmbeddingTests(unittest.TestCase):
    def setUp(self):
        self.provider = Mock()
        self.client = SimpleNamespace(
            provider_client=SimpleNamespace(models=self.provider),
            embedding_model="gemini-embedding-001",
        )

    def test_successful_embedding_generation_uses_configured_model(self):
        self.provider.embed_content.return_value = SimpleNamespace(
            embeddings=[SimpleNamespace(values=[0.1, 0.2, 0.3])]
        )

        embedding, dimensions = create_embedding("Python backend role", self.client)

        self.assertEqual(embedding, [0.1, 0.2, 0.3])
        self.assertEqual(dimensions, 3)
        self.provider.embed_content.assert_called_once_with(
            model="gemini-embedding-001",
            contents="Python backend role",
        )

    def test_blank_input_is_rejected(self):
        for value in ("", "   "):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    create_embedding(value, self.client)
        self.provider.embed_content.assert_not_called()

    def test_api_failure_becomes_application_error(self):
        self.provider.embed_content.side_effect = RuntimeError("provider failure")

        with self.assertRaises(EmbeddingGenerationError):
            create_embedding("Python backend role", self.client)

    def test_job_embedding_text_excludes_empty_fields(self):
        job = Job(
            "Backend Engineer",
            "JobPulse",
            "Remote",
            None,
            "https://example.test/job/1",
            description="Build APIs",
            employment_type="Full-time",
            salary=None,
        )

        text = build_job_embedding_text(job)

        self.assertEqual(
            text,
            "\n".join(
                [
                    "Title: Backend Engineer",
                    "Company: JobPulse",
                    "Location: Remote",
                    "Description: Build APIs",
                    "Employment type: Full-time",
                ]
            ),
        )
        self.assertNotIn("Salary:", text)

    def test_job_embedding_is_persisted_with_model(self):
        self.provider.embed_content.return_value = SimpleNamespace(
            embeddings=[SimpleNamespace(values=[0.4, 0.5])]
        )
        job = Job(
            "Backend Engineer",
            "JobPulse",
            "Remote",
            None,
            "https://example.test/job/1",
        )

        with patch("jobpulse.ai.embeddings.save_job_embedding") as save:
            result = generate_and_save_job_embedding(job, job_id=42, client=self.client)

        self.assertEqual(result, ([0.4, 0.5], 2))
        save.assert_called_once_with(
            42,
            [0.4, 0.5],
            embedding_model="gemini-embedding-001",
        )


if __name__ == "__main__":
    unittest.main()
