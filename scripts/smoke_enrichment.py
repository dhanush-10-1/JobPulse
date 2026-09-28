"""One-off smoke test for enriching one existing JobPulse job."""

from jobpulse.ai.client import AIClient
from jobpulse.ai.enrichment import generate_and_save_job_enrichment
from jobpulse.database.connections import connect_db
from jobpulse.database.repository import JOB_COLUMNS
from jobpulse.ingestion.models import Job


def load_one_job_with_description():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"""
            SELECT id, {JOB_COLUMNS}
            FROM jobs
            WHERE is_active = TRUE
              AND description IS NOT NULL
              AND BTRIM(description) <> ''
            ORDER BY id
            LIMIT 1
            """
        )
        row = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if row is None:
        raise RuntimeError("No active jobs with descriptions found")

    job = Job.from_row(row[1:])
    job.id = row[0]
    return job


def main():
    job = load_one_job_with_description()
    client = AIClient()
    result = generate_and_save_job_enrichment(job, client=client)

    print(f"job id: {job.id}")
    print(f"job title: {job.title}")
    print(f"model: {client.model}")
    print(f"category: {result.category}")
    print(f"seniority: {result.seniority}")
    print(f"number of extracted skills: {len(result.skills)}")
    print("persistence succeeded")


if __name__ == "__main__":
    main()