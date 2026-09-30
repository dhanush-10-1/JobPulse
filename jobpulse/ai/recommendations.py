"""Deterministic job recommendations for a stored resume profile."""

from uuid import UUID

from jobpulse.database.repository import (
    get_active_enriched_job_ids,
    get_resume_profile,
)

from .matching import MatchError, MatchResult, match_resume_to_job


def recommend_jobs(resume_id: UUID, top_k: int = 10) -> list[MatchResult]:
    """Return the best eligible job matches for a resume."""
    if not isinstance(top_k, int) or isinstance(top_k, bool) or not 1 <= top_k <= 50:
        raise ValueError("top_k must be between 1 and 50")

    if get_resume_profile(resume_id) is None:
        raise MatchError(f"resume profile not found: {resume_id}")

    results = [
        match_resume_to_job(resume_id, job_id)
        for job_id in get_active_enriched_job_ids()
    ]
    results.sort(key=lambda result: (result.match_score, result.similarity), reverse=True)
    return results[:top_k]