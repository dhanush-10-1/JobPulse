from datetime import date

from jobpulse.ingestion.models import Job
from jobpulse.messaging.producer import send_job


job = Job(
    "Kafka Integration Test",
    "JobPulse Test Company",
    "Bangalore",
    date.today(),
    "https://jobpulse.test/jobs/999"
)

if __name__ == "__main__":
    send_job(job)
