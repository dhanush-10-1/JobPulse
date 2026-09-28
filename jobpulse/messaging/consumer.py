import time
from datetime import date
import json

from kafka import KafkaConsumer, KafkaProducer
from jobpulse.ingestion.models import Job
from jobpulse.database.repository import insert_jobs

dlt_producer=KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda value : json.dumps(value).encode("utf-8")
)

def send_to_dlt(data, error):
    future=dlt_producer.send(
        "job-events-2.DLT",
        value={
            "original_event":data,
            "error":str(error)
        }
    )
    future.get(timeout=10)

consumer=KafkaConsumer(
    "job-events-2",
    bootstrap_servers="localhost:9092",
    group_id="jobpulse-db-consumer",
    enable_auto_commit=False,
    auto_offset_reset="earliest",
    value_deserializer=lambda value: json.loads(value.decode("utf-8"))
)

def process_job(data):
    job=Job(
        data["title"],
        data["company"],
        data["location"],
        date.fromisoformat(data["posted_date"]),
        data["url"],
        source=data.get("source", "python.org"),
        source_job_id=data.get("source_job_id"),
        description=data.get("description"),
        employment_type=data.get("employment_type"),
        salary=data.get("salary"),
    )
    insert_jobs([job])

def process_with_retry(data, max_retries=3):

    for i in range(max_retries):

        try:
            print(f"Processing attempt {i + 1}/{max_retries}")
            process_job(data)
            print("Job processed successfully")
            return

        except Exception as e:
            print(f"Processing failed: {e}")

            if i == max_retries - 1:
                print("Maximum retries reached. Sending to DLT...")
                send_to_dlt(data, e)
                print("Successfully sent to DLT")
                return

            time.sleep(2 ** i)


for message in consumer:
    process_with_retry(message.value)
    consumer.commit()
