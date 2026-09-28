"""One-off smoke test for embedding one existing JobPulse job."""

from jobpulse.ai.client import AIClient
from jobpulse.ai.embeddings import generate_and_save_job_embedding
from jobpulse.database.connections import connect_db
from jobpulse.database.repository import JOB_COLUMNS
from jobpulse.ingestion.models import Job


def load_one_job():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"""
            SELECT id, {JOB_COLUMNS}
            FROM jobs
            WHERE is_active = TRUE
            ORDER BY id
            LIMIT 1
            """
        )
        row = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if row is None:
        raise RuntimeError("No active jobs found in the JobPulse database")

    job = Job.from_row(row[1:])
    job.id = row[0]
    return job


def main():
    job = load_one_job()
    client = AIClient()
    _, dimensions = generate_and_save_job_embedding(job, client=client)

    print(f"selected job id: {job.id}")
    print(f"selected job title: {job.title}")
    print(f"embedding model: {client.embedding_model}")
    print(f"embedding dimensions: {dimensions}")
    print("persistence succeeded")


if __name__ == "__main__":
    main()
