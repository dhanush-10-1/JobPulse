from jobpulse.ingestion.fetch import fetch_html
from jobpulse.ingestion.parser import parse_html,extract_jobs
from jobpulse.ingestion.models import Job
from jobpulse.storage.exporter import export_jobs
from jobpulse.utils.logger import logger
from config import URL,OUTPUT_FILE





def main():
    try:
        html = fetch_html(URL)
        soup=parse_html(html)
        job_listings=extract_jobs(soup)
        export_jobs(job_listings,OUTPUT_FILE) 
    except Exception as e:
        logger.exception("jobpulse pipeline has failed")
        raise


if __name__ == "__main__":
    main()