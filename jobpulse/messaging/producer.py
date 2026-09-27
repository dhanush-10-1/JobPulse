import json

from kafka import KafkaProducer


producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    acks="all",
    enable_idempotence=True,
    retries=5,
    delivery_timeout_ms=120000,
    key_serializer=lambda key: key.encode("utf-8"),
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)


def send_job(job):
    future = producer.send(
        "job-events-2",
        key=job.url,
        value=job.to_dict()
    )

    record_metadata = future.get(timeout=10)

    print(
        f"Job sent successfully | "
        f"topic={record_metadata.topic} | "
        f"partition={record_metadata.partition} | "
        f"offset={record_metadata.offset}"
    )