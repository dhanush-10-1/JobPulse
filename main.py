from jobpulse.ingestion.fetch import fetch_html
from jobpulse.ingestion.parser import parse_html,extract_jobs
from jobpulse.ingestion.models import Job
from jobpulse.storage.exporter import export_jobs
from jobpulse.utils.logger import logger
from config import URL,OUTPUT_FILE
from jobpulse.database.repository import insert_jobs





def main():
    print("main started")
    try:
        html = fetch_html(URL)
        soup=parse_html(html)
        job_listings=extract_jobs(soup)
        insert_jobs(job_listings)
        export_jobs(job_listings,OUTPUT_FILE) 
    except Exception as e:
        logger.exception("jobpulse pipeline has failed")
        raise
    print("main excuted")


if __name__ == "__main__":
    main()