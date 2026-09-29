import unittest
from types import SimpleNamespace
from uuid import UUID
from unittest.mock import Mock, patch

from jobpulse.ai.embeddings import EmbeddingGenerationError
from jobpulse.ai.resume import ResumeProfile
from jobpulse.ai.resume_embeddings import (
    build_resume_embedding_text,
    generate_and_save_resume_embedding,
)


class ResumeEmbeddingTests(unittest.TestCase):
    def setUp(self):
        self.resume_id = UUID("11111111-1111-1111-1111-111111111111")
        self.profile = ResumeProfile(
            name="Alex Smith",
            summary="Backend engineer",
            skills=["Python", "SQL"],
            technologies=["PostgreSQL"],
            experience=[{
                "company": "DataWorks",
                "role": "Engineer",
                "duration": "3 years",
                "description": "Built APIs",
            }],
            education=[{
                "institution": "University",
                "degree": "BSc",
                "field": "Computer Science",
                "year": "2020",
            }],
            projects=[{
                "name": "JobPulse",
                "description": "Resume intelligence platform",
                "technologies": ["Python"],
            }],
        )
        self.client = SimpleNamespace(embedding_model="gemini-embedding-001")

    def test_embedding_text_includes_only_non_empty_sections(self):
        profile = self.profile.model_copy(
            update={"summary": " ", "education": [], "projects": []}
        )

        text = build_resume_embedding_text(profile)

        self.assertNotIn("Summary:", text)
        self.assertIn("Skills: Python; SQL", text)
        self.assertIn("Technologies: PostgreSQL", text)
        self.assertIn("Experience:", text)
        self.assertIn("Engineer", text)
        self.assertNotIn("Education:", text)
        self.assertNotIn("Projects:", text)

    @patch("jobpulse.ai.resume_embeddings.save_resume_embedding")
    @patch("jobpulse.ai.resume_embeddings.create_embedding")
    @patch("jobpulse.ai.resume_embeddings.get_resume_profile")
    def test_successful_generation_and_persistence(self, get_profile, create, save):
        get_profile.return_value = self.profile
        create.return_value = ([0.1, 0.2], 2)

        result = generate_and_save_resume_embedding(self.resume_id, self.client)

        self.assertEqual(
            result,
            {
                "resume_id": self.resume_id,
                "embedding_model": "gemini-embedding-001",
                "dimensions": 2,
            },
        )
        create.assert_called_once()
        self.assertIn("Summary: Backend engineer", create.call_args.args[0])
        save.assert_called_once_with(
            self.resume_id,
            [0.1, 0.2],
            embedding_model="gemini-embedding-001",
        )

    @patch("jobpulse.ai.resume_embeddings.get_resume_profile", return_value=None)
    def test_missing_resume_profile_is_rejected(self, get_profile):
        with self.assertRaisesRegex(ValueError, "not found"):
            generate_and_save_resume_embedding(self.resume_id, self.client)

        get_profile.assert_called_once_with(self.resume_id)

    @patch(
        "jobpulse.ai.resume_embeddings.get_resume_profile",
        return_value=ResumeProfile(),
    )
    def test_empty_profile_content_is_rejected(self, get_profile):
        with self.assertRaisesRegex(ValueError, "embeddable content"):
            generate_and_save_resume_embedding(self.resume_id, self.client)

    @patch("jobpulse.ai.resume_embeddings.create_embedding")
    @patch(
        "jobpulse.ai.resume_embeddings.get_resume_profile",
        return_value=ResumeProfile(summary="Backend engineer"),
    )
    def test_provider_failure_is_preserved_as_embedding_error(self, get_profile, create):
        create.side_effect = EmbeddingGenerationError("provider failure")

        with self.assertRaises(EmbeddingGenerationError):
            generate_and_save_resume_embedding(self.resume_id, self.client)

    @patch("jobpulse.ai.resume_embeddings.save_resume_embedding")
    @patch("jobpulse.ai.resume_embeddings.create_embedding", return_value=([0.1], 1))
    @patch(
        "jobpulse.ai.resume_embeddings.get_resume_profile",
        return_value=ResumeProfile(summary="Backend engineer"),
    )
    def test_persistence_failure_is_not_swallowed(self, get_profile, create, save):
        save.side_effect = RuntimeError("database failure")

        with self.assertRaisesRegex(RuntimeError, "database failure"):
            generate_and_save_resume_embedding(self.resume_id, self.client)


if __name__ == "__main__":
    unittest.main()