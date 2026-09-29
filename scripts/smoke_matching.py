"""One-off smoke test for the stored resume-to-job matching pipeline."""

from jobpulse.ai.matching import MatchError, match_resume_to_job
from jobpulse.database.connections import connect_db
from jobpulse.database.repository import get_resume_embedding, get_resume_profile


def find_resume_id():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT rp.id
            FROM resume_profiles rp
            JOIN resume_embeddings re ON re.resume_id = rp.id
            ORDER BY rp.created_at, rp.id
            """
        )
        for (resume_id,) in cursor.fetchall():
            if get_resume_profile(resume_id) and get_resume_embedding(resume_id):
                return resume_id
    finally:
        cursor.close()
        conn.close()
    return None


def find_job():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT j.id, j.title, j.company
            FROM jobs j
            JOIN job_ai_enrichment ai ON ai.job_id = j.id
            JOIN job_embeddings je ON je.job_id = j.id
            WHERE j.is_active = TRUE
              AND ai.status = 'completed'
            ORDER BY j.id
            LIMIT 1
            """
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def main():
    resume_id = find_resume_id()
    if resume_id is None:
        print("No eligible stored resume profile with a valid embedding was found.")
        return

    job = find_job()
    if job is None:
        print("No eligible active job with completed enrichment and an embedding was found.")
        return

    job_id, job_title, company = job
    try:
        result = match_resume_to_job(resume_id, job_id)
    except MatchError as error:
        print(f"Matching could not run: {error}")
        return

    print(f"resume_id: {result.resume_id}")
    print(f"job_id: {result.job_id}")
    print(f"job title: {job_title}")
    print(f"company: {company}")
    print(f"similarity: {result.similarity}")
    print(f"matched_skills: {result.matched_skills}")
    print(f"missing_skills: {result.missing_skills}")
    print(f"experience_match: {result.experience_match}")
    print(f"match_score: {result.match_score}")
    print(f"explanation: {result.explanation}")


if __name__ == "__main__":
    main()
