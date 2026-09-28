import unittest
import sys
import types
from unittest.mock import patch

from jobpulse.ai.embeddings import create_embedding
from jobpulse.ai.enrichment import EnrichmentResult, enrich_job


class AIFoundationTests(unittest.TestCase):
    def test_missing_api_key_is_rejected(self):
        with patch("jobpulse.ai.client.config.GEMINI_API_KEY", None):
            from jobpulse.ai.client import AIClient

            with self.assertRaisesRegex(ValueError, "GEMINI_API_KEY"):
                AIClient()

    def test_gemini_client_uses_configured_key(self):
        fake_genai = types.ModuleType("google.genai")
        fake_genai.Client = unittest.mock.Mock()
        fake_google = types.ModuleType("google")
        fake_google.genai = fake_genai
        with patch.dict(
            sys.modules,
            {"google": fake_google, "google.genai": fake_genai},
        ), patch("jobpulse.ai.client.config.AI_EMBEDDING_MODEL", None):
            from jobpulse.ai.client import AIClient

            client = AIClient(api_key="test-key")

        fake_genai.Client.assert_called_once_with(api_key="test-key")
        self.assertEqual(client.embedding_model, "gemini-embedding-001")

    def test_empty_embedding_input_is_rejected(self):
        for value in ("", "   "):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    create_embedding(value)

    def test_enrichment_result_schema_validation(self):
        result = EnrichmentResult(
            skills=["Python"],
            category="Engineering",
            seniority="Senior",
            employment_type="Full-time",
            responsibilities=["Build services"],
            requirements=["Three years of experience"],
            summary="A backend engineering role.",
        )

        self.assertEqual(result.to_dict()["skills"], ["Python"])
        self.assertEqual(
            enrich_job({"employment_type": "Contract"}).employment_type,
            "Contract",
        )
        with self.assertRaises(TypeError):
            EnrichmentResult(skills="Python")


if __name__ == "__main__":
    unittest.main()
