"""Run a bounded, sequential batch of AI job enrichments."""

import argparse

from jobpulse.ai.batch_enrichment import enrich_jobs_batch


def main():
    parser = argparse.ArgumentParser(description="Enrich eligible JobPulse jobs")
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="maximum number of jobs to process (default: 10)",
    )
    args = parser.parse_args()
    stats = enrich_jobs_batch(args.limit)
    print(
        "batch enrichment: "
        f"selected={stats.selected} "
        f"succeeded={stats.succeeded} "
        f"failed={stats.failed} "
        f"skipped={stats.skipped}"
    )


if __name__ == "__main__":
    main()