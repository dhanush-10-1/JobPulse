from fastapi import FastAPI,HTTPException,status
from jobpulse.database.repository import ensure_job_freshness_schema,get_job_by_id,get_jobs_by_filter

app = FastAPI()


@app.on_event("startup")
def initialize_database():
    ensure_job_freshness_schema()


@app.get("/jobs")
def get_jobs(company: str | None = None,location:str |None=None):

    jobs=get_jobs_by_filter(location,company)
    if not jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No jobs found"
        )
    return [job.to_dict() for job in jobs]

@app.get("/jobs/{job_id}")
def get_job(job_id:int):
    job=get_job_by_id(job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail="job not found"
        )
    return job.to_dict()
        