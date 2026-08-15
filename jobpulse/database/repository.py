from .connections import connect_db,psycopg2
from jobpulse.utils.logger import logger
from jobpulse.ingestion.models import Job

def insert_jobs(jobs):
    conn=None
    cursor=None
    try:
        conn=connect_db()
        cursor=conn.cursor()
        for job in jobs:
            cursor.execute(
                '''
                INSERT INTO jobs(title,company,location,posted_date,url)
                VALUES(%s,%s,%s,%s,%s)
                ON CONFLICT(url)
                DO NOTHING;''',(
                    job.title,
                    job.company,
                    job.location,
                    job.posted_date,
                    job.url
                )
                
            )
        
        logger.info("insert %d jobs successfully",len(jobs))
        conn.commit()
        
    except psycopg2.Error:
        if conn:
            conn.rollback()
        logger.exception("failed to inset jobs")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_all_jobs():
    conn=None
    cursor=None
    try:
        conn=connect_db()
        cursor=conn.cursor()
        cursor.execute(
            '''SELECT title, company, location, posted_date, url
FROM jobs;'''
        )
        rows=cursor.fetchall()
        all_jobs=[Job.from_row(row) for row in rows]
    except psycopg2.Error:
        logger.exception("failed to fetch the jobs")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return all_jobs