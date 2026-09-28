"""Semantic job search service."""

from .embeddings import create_embedding
from jobpulse.database.repository import search_jobs_by_embedding


def semantic_search(query_text: str, top_k=10, client=None):
    """Find active jobs nearest to a natural-language embedding query."""
    if not isinstance(query_text, str) or not query_text.strip():
        raise ValueError("search query must be a non-empty string")

    embedding, _ = create_embedding(query_text, client=client)
    return search_jobs_by_embedding(embedding, top_k=top_k)