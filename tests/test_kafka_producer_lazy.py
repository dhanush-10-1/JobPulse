import importlib
from types import SimpleNamespace
from unittest.mock import Mock, patch

import jobpulse.messaging.producer as producer_module


def test_producer_module_imports_without_connecting_to_kafka():
    with patch.object(producer_module, "KafkaProducer") as kafka_producer:
        module = importlib.reload(producer_module)

    kafka_producer.assert_not_called()
    assert module.producer is None


def test_send_job_lazily_uses_configured_producer():
    module = importlib.reload(producer_module)
    fake_producer = Mock()
    fake_producer.send.return_value = Mock(
        get=Mock(
            return_value=SimpleNamespace(
                topic="job-events-2", partition=0, offset=1
            )
        )
    )
    job = SimpleNamespace(
        url="https://example.test/job/1",
        to_dict=Mock(return_value={"id": 1}),
    )

    with patch.object(
        module, "KafkaProducer", return_value=fake_producer
    ) as kafka_producer:
        module.send_job(job)

    kafka_producer.assert_called_once()
    producer_config = kafka_producer.call_args.kwargs
    assert producer_config["bootstrap_servers"] == "localhost:9092"
    assert producer_config["acks"] == "all"
    assert producer_config["enable_idempotence"] is True
    assert producer_config["retries"] == 5
    assert producer_config["delivery_timeout_ms"] == 120000
    assert callable(producer_config["key_serializer"])
    assert callable(producer_config["value_serializer"])
    fake_producer.send.assert_called_once_with(
        "job-events-2",
        key=job.url,
        value={"id": 1},
    )