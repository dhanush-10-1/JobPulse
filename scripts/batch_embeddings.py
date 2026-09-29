"""Run a bounded, sequential batch of job embeddings."""

import argparse

from jobpulse.ai.batch_embeddings import embed_jobs_batch


def main():
    parser = argparse.ArgumentParser(description="Generate embeddings for JobPulse jobs")
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="maximum number of jobs to process (default: 10)",
    )
    args = parser.parse_args()
    stats = embed_jobs_batch(args.limit)
    print(
        "batch embeddings: "
        f"selected={stats.selected} "
        f"succeeded={stats.succeeded} "
        f"failed={stats.failed} "
        f"skipped={stats.skipped}"
    )


if __name__ == "__main__":
    main()