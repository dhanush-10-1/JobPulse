from urllib.parse import urlparse

from config import OUTPUT_FILE, URL
from jobpulse.database.repository import insert_jobs
from jobpulse.ingestion.fetch import fetch_html
from jobpulse.ingestion.parser import extract_jobs, parse_html
from jobpulse.storage.exporter import export_jobs
from jobpulse.utils.logger import logger


def _validate_jobs(jobs):
    if not jobs:
        raise ValueError("source returned no job listings")

    seen_urls = set()
    for job in jobs:
        required = (job.title, job.company, job.location, job.posted_date, job.url)
        if any(value is None or value == "" for value in required):
            raise ValueError("source returned a job with missing required fields")
        parsed_url = urlparse(job.url)
        if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
            raise ValueError(f"source returned a non-absolute job URL: {job.url}")
        if job.url in seen_urls:
            raise ValueError(f"source returned duplicate job URL: {job.url}")
        seen_urls.add(job.url)


def run_ingestion():
    logger.info("starting JobPulse ingestion from %s", URL)
    html = fetch_html(URL)
    if not html.strip():
        raise ValueError("source returned an empty response")

    jobs = extract_jobs(parse_html(html), detail_fetcher=fetch_html)
    _validate_jobs(jobs)
    stats = insert_jobs(jobs, source="python.org", complete_run=True)
    export_jobs(jobs, OUTPUT_FILE)
    stats["fetched"] = len(jobs)
    logger.info(
        "JobPulse ingestion succeeded: fetched=%d inserted=%d updated=%d stale=%d",
        stats["fetched"],
        stats["inserted"],
        stats["updated"],
        stats["stale"],
    )
    return stats
