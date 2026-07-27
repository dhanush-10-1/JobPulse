from jobpulse.ingestion.fetch import fetch_html
from jobpulse.ingestion.parser import parse_html,extract_jobs
from jobpulse.ingestion.models import Job



def main():

    html = fetch_html()

    soup=parse_html(html)
    job_listings=extract_jobs(soup)
    for job in job_listings:
        print(job.title)





if __name__ == "__main__":
    main()