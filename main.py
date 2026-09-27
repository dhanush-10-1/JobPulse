from jobpulse.ingestion.pipeline import run_ingestion
from jobpulse.utils.logger import logger
from jobpulse.database.repository import get_all_jobs,get_jobs_by_url,get_jobs_by_company,get_jobs_by_location,get_recent_jobs





def main():
    print("main started")
    try:
        stats = run_ingestion()
        logger.info("command-line ingestion stats: %s", stats)
        job_listings = get_all_jobs()
        if job_listings:
            get_jobs_by_url(job_listings[0].url)
        if len(job_listings) > 1:
            get_jobs_by_company(job_listings[1].company)
        if len(job_listings) > 2:
            get_jobs_by_location(job_listings[2].location)
        get_recent_jobs(30)
        
        

    except Exception as e:
        logger.exception("jobpulse pipeline has failed")
        raise
    print("main excuted")


if __name__ == "__main__":
    main()