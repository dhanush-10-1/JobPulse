"""Embedding generation and persistence for resume profiles."""

import json
from collections.abc import Mapping
from uuid import UUID

from jobpulse.database.repository import (
    get_resume_profile,
    save_resume_embedding,
)

from .client import AIClient
from .embeddings import EmbeddingGenerationError, create_embedding


def _section_value(value):
    if isinstance(value, Mapping):
        return json.dumps(value, sort_keys=True)
    return str(value).strip()


def build_resume_embedding_text(profile) -> str:
    """Build deterministic text from populated resume profile sections."""
    parts = []
    if profile.summary and profile.summary.strip():
        parts.append(f"Summary: {profile.summary.strip()}")

    for label, field_name in (
        ("Skills", "skills"),
        ("Technologies", "technologies"),
        ("Experience", "experience"),
        ("Education", "education"),
        ("Projects", "projects"),
    ):
        values = getattr(profile, field_name, [])
        rendered = [
            _section_value(value)
            for value in values
            if value is not None and _section_value(value)
        ]
        if rendered:
            parts.append(f"{label}: {'; '.join(rendered)}")

    return "\n".join(parts)


def generate_and_save_resume_embedding(
    resume_id: UUID,
    client: AIClient | None = None,
):
    """Generate and persist an embedding for a stored resume profile."""
    profile = get_resume_profile(resume_id)
    if profile is None:
        raise ValueError(f"resume profile not found: {resume_id}")

    embedding_text = build_resume_embedding_text(profile)
    if not embedding_text:
        raise ValueError("resume profile does not contain embeddable content")

    ai_client = client or AIClient()
    embedding, dimensions = create_embedding(embedding_text, client=ai_client)
    save_resume_embedding(
        resume_id,
        embedding,
        embedding_model=ai_client.embedding_model,
    )
    return {
        "resume_id": resume_id,
        "embedding_model": ai_client.embedding_model,
        "dimensions": dimensions,
    }