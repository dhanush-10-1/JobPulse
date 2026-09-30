"""One-off smoke test for the stored job recommendation pipeline."""

from jobpulse.ai.matching import MatchError
from jobpulse.ai.recommendations import recommend_jobs
from jobpulse.database.connections import connect_db
from jobpulse.database.repository import (
    get_job_by_id,
    get_resume_embedding,
    get_resume_profile,
)


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


def main():
    resume_id = find_resume_id()
    if resume_id is None:
        print("No stored resume profile with a valid embedding was found.")
        return

    try:
        recommendations = recommend_jobs(resume_id, top_k=5)
    except MatchError as error:
        print(f"Recommendations could not run: {error}")
        return

    for rank, recommendation in enumerate(recommendations, start=1):
        job = get_job_by_id(recommendation.job_id)
        job_title = job.title if job else "Unknown"
        company = job.company if job else "Unknown"
        print(f"rank: {rank}")
        print(f"job_id: {recommendation.job_id}")
        print(f"job title: {job_title}")
        print(f"company: {company}")
        print(f"match_score: {recommendation.match_score}")
        print(f"similarity: {recommendation.similarity}")
        print(f"matched_skills: {recommendation.matched_skills}")
        print(f"missing_skills: {recommendation.missing_skills}")
        print(f"experience_match: {recommendation.experience_match}")
        print(f"explanation: {recommendation.explanation}")
        print()

    print(f"total recommendations: {len(recommendations)}")


if __name__ == "__main__":
    main()