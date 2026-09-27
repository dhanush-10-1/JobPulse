from .connections import connect_db, psycopg2
from jobpulse.utils.logger import logger
from jobpulse.ingestion.models import Job


JOB_COLUMNS = """
    title, company, location, posted_date, url,
    source, first_seen_at, last_seen_at, is_active
"""


def ensure_job_freshness_schema():
    conn = None
    cursor = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'jobs'
            """
        )
        existing = {row[0] for row in cursor.fetchall()}
        additions = {
            "source": "VARCHAR(100)",
            "first_seen_at": "TIMESTAMP",
            "last_seen_at": "TIMESTAMP",
            "is_active": "BOOLEAN",
        }
        added = set()
        for column, definition in additions.items():
            if column not in existing:
                cursor.execute(f"ALTER TABLE jobs ADD COLUMN {column} {definition}")
                added.add(column)

        if "source" in added:
            cursor.execute("UPDATE jobs SET source = 'python.org' WHERE source IS NULL")
        if "first_seen_at" in added:
            cursor.execute(
                "UPDATE jobs SET first_seen_at = COALESCE(created_timestamp, CURRENT_TIMESTAMP)"
            )
        if "last_seen_at" in added:
            cursor.execute(
                "UPDATE jobs SET last_seen_at = COALESCE(created_timestamp, CURRENT_TIMESTAMP)"
            )
        if "is_active" in added:
            cursor.execute("UPDATE jobs SET is_active = TRUE WHERE is_active IS NULL")

        cursor.execute("ALTER TABLE jobs ALTER COLUMN source SET DEFAULT 'python.org'")
        cursor.execute("ALTER TABLE jobs ALTER COLUMN source SET NOT NULL")
        cursor.execute("ALTER TABLE jobs ALTER COLUMN first_seen_at SET DEFAULT CURRENT_TIMESTAMP")
        cursor.execute("ALTER TABLE jobs ALTER COLUMN first_seen_at SET NOT NULL")
        cursor.execute("ALTER TABLE jobs ALTER COLUMN last_seen_at SET DEFAULT CURRENT_TIMESTAMP")
        cursor.execute("ALTER TABLE jobs ALTER COLUMN last_seen_at SET NOT NULL")
        cursor.execute("ALTER TABLE jobs ALTER COLUMN is_active SET DEFAULT TRUE")
        cursor.execute("ALTER TABLE jobs ALTER COLUMN is_active SET NOT NULL")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS jobs_active_source_idx ON jobs (source, is_active)"
        )
        conn.commit()
    except psycopg2.Error:
        if conn:
            conn.rollback()
        logger.exception("failed to initialize jobs freshness schema")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_jobs(jobs, source="python.org", complete_run=False, stale_after_days=7):
    if not jobs:
        logger.warning("skipping empty ingestion run")
        return {"inserted": 0, "updated": 0, "stale": 0}

    ensure_job_freshness_schema()
    conn = None
    cursor = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        urls = list(dict.fromkeys(job.url for job in jobs))
        cursor.execute("SELECT url FROM jobs WHERE url = ANY(%s)", (urls,))
        existing_urls = {row[0] for row in cursor.fetchall()}
        for job in jobs:
            cursor.execute(
                f"""
                INSERT INTO jobs ({JOB_COLUMNS})
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP, TRUE)
                ON CONFLICT (url)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    company = EXCLUDED.company,
                    location = EXCLUDED.location,
                    posted_date = EXCLUDED.posted_date,
                    source = EXCLUDED.source,
                    last_seen_at = CURRENT_TIMESTAMP,
                    is_active = TRUE
                """,
                (
                    job.title,
                    job.company,
                    job.location,
                    job.posted_date,
                    job.url,
                    source,
                ),
            )

        inactive_count = 0
        if complete_run:
            cursor.execute(
                """
                UPDATE jobs
                SET is_active = FALSE
                WHERE source = %s
                  AND is_active = TRUE
                  AND last_seen_at < CURRENT_TIMESTAMP - (%s * INTERVAL '1 day')
                """,
                (source, stale_after_days),
            )
            inactive_count = cursor.rowcount

        conn.commit()
        logger.info(
            "upserted %d jobs from %s; marked %d stale jobs inactive",
            len(jobs),
            source,
            inactive_count,
        )
        return {
            "inserted": len(set(urls) - existing_urls),
            "updated": len(set(urls) & existing_urls),
            "stale": inactive_count,
        }
    except psycopg2.Error:
        if conn:
            conn.rollback()
        logger.exception("failed to upsert jobs")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def _fetch_jobs(query, params=()):
    conn = None
    cursor = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [Job.from_row(row) for row in cursor.fetchall()]
    except psycopg2.Error:
        logger.exception("failed to fetch jobs")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_all_jobs():
    return _fetch_jobs(
        f"SELECT {JOB_COLUMNS} FROM jobs WHERE is_active = TRUE ORDER BY posted_date DESC"
    )


def get_jobs_by_url(url):
    jobs = _fetch_jobs(
        f"SELECT {JOB_COLUMNS} FROM jobs WHERE url = %s AND is_active = TRUE",
        (url,),
    )
    return jobs[0] if jobs else None


def get_jobs_by_company(company):
    return _fetch_jobs(
        f"""SELECT {JOB_COLUMNS} FROM jobs
            WHERE company ILIKE %s AND is_active = TRUE
            ORDER BY posted_date DESC""",
        (f"%{company}%",),
    )


def get_jobs_by_location(location):
    return _fetch_jobs(
        f"""SELECT {JOB_COLUMNS} FROM jobs
            WHERE location ILIKE %s AND is_active = TRUE
            ORDER BY posted_date DESC""",
        (f"%{location}%",),
    )


def get_recent_jobs(days):
    return _fetch_jobs(
        f"""SELECT {JOB_COLUMNS} FROM jobs
            WHERE posted_date >= CURRENT_DATE - (%s * INTERVAL '1 day')
              AND is_active = TRUE
            ORDER BY posted_date DESC""",
        (days,),
    )


def get_job_by_id(job_id):
    jobs = _fetch_jobs(
        f"SELECT {JOB_COLUMNS} FROM jobs WHERE id = %s AND is_active = TRUE",
        (job_id,),
    )
    return jobs[0] if jobs else None


def get_jobs_by_filter(job_location=None, company=None):
    if job_location and company:
        return _fetch_jobs(
            f"""SELECT {JOB_COLUMNS} FROM jobs
                WHERE location ILIKE %s AND company ILIKE %s
                  AND is_active = TRUE
                ORDER BY posted_date DESC""",
            (f"%{job_location}%", f"%{company}%"),
        )
    if job_location:
        return get_jobs_by_location(job_location)
    if company:
        return get_jobs_by_company(company)
    return get_all_jobs()
