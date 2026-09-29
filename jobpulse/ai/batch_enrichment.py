"""Bounded, sequential batch processing for job AI enrichment."""

from dataclasses import dataclass

import config

from jobpulse.database.repository import (
    get_jobs_for_enrichment_batch,
    save_job_ai_enrichment,
)

from .enrichment import EnrichmentResult, generate_and_save_job_enrichment


@dataclass
class BatchEnrichmentStats:
    selected: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0

    def as_dict(self):
        return {
            "selected": self.selected,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "skipped": self.skipped,
        }


def enrich_jobs_batch(limit, client=None, model=None):
    """Enrich up to ``limit`` eligible jobs without concurrent work or retries."""
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError("limit must be a positive integer")

    configured_model = model or config.AI_MODEL
    records = get_jobs_for_enrichment_batch(limit, model=configured_model)
    stats = BatchEnrichmentStats(selected=len(records))

    for record in records:
        job = record["job"]
        if (
            record.get("status") == "completed"
            and record.get("model") == configured_model
        ):
            stats.skipped += 1
            continue

        try:
            generate_and_save_job_enrichment(job, client=client)
        except Exception:
            stats.failed += 1
            try:
                save_job_ai_enrichment(
                    job.id,
                    EnrichmentResult(),
                    model=configured_model,
                    status="failed",
                )
            except Exception:
                # Preserve the original enrichment failure as the batch result.
                pass
        else:
            stats.succeeded += 1

    return stats