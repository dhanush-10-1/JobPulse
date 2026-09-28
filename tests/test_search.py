import unittest
from unittest.mock import patch

from jobpulse.ai.search import semantic_search


class SemanticSearchTests(unittest.TestCase):
    def test_blank_query_is_rejected(self):
        with patch("jobpulse.ai.search.create_embedding") as create_embedding:
            with self.assertRaises(ValueError):
                semantic_search("   ")
        create_embedding.assert_not_called()

    def test_query_embedding_and_top_k_are_forwarded(self):
        expected = [
            {"job": "closest", "distance": 0.1, "similarity": 0.9},
            {"job": "next", "distance": 0.3, "similarity": 0.7},
        ]
        client = object()
        with patch(
            "jobpulse.ai.search.create_embedding",
            return_value=([0.1, 0.2], 2),
        ) as create_embedding, patch(
            "jobpulse.ai.search.search_jobs_by_embedding",
            return_value=expected,
        ) as search_jobs:
            results = semantic_search("backend platform", top_k=2, client=client)

        create_embedding.assert_called_once_with("backend platform", client=client)
        search_jobs.assert_called_once_with([0.1, 0.2], top_k=2)
        self.assertEqual(results, expected)
        self.assertEqual([item["distance"] for item in results], [0.1, 0.3])


if __name__ == "__main__":
    unittest.main()