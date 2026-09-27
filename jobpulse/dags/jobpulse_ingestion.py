import logging
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from jobpulse.ingestion.pipeline import run_ingestion

logger = logging.getLogger(__name__)

DAG_ID = "jobpulse_ingestion"
SCHEDULE = os.getenv("JOBPULSE_AIRFLOW_SCHEDULE", "0 * * * *")
RETRIES = int(os.getenv("JOBPULSE_AIRFLOW_RETRIES", "2"))
RETRY_DELAY_MINUTES = int(os.getenv("JOBPULSE_AIRFLOW_RETRY_DELAY_MINUTES", "5"))


def log_start(**context):
    logger.info("Starting JobPulse ingestion run_id=%s", context["run_id"])


def ingest_jobs(**context):
    stats = run_ingestion()
    context["ti"].xcom_push(key="ingestion_stats", value=stats)
    logger.info("Airflow ingestion task completed: %s", stats)


def log_finish(**context):
    stats = context["ti"].xcom_pull(
        task_ids="ingest_jobs", key="ingestion_stats"
    )
    if not stats:
        raise RuntimeError("ingestion task did not publish statistics")
    logger.info(
        "Finished JobPulse ingestion: fetched=%d inserted=%d updated=%d stale=%d",
        stats["fetched"],
        stats["inserted"],
        stats["updated"],
        stats["stale"],
    )


with DAG(
    dag_id=DAG_ID,
    start_date=datetime(2026, 1, 1),
    schedule=SCHEDULE,
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "jobpulse",
        "retries": RETRIES,
        "retry_delay": timedelta(minutes=RETRY_DELAY_MINUTES),
    },
    tags=["jobpulse", "ingestion", "python-org"],
) as dag:
    start = PythonOperator(
        task_id="start",
        python_callable=log_start,
    )
    ingest = PythonOperator(
        task_id="ingest_jobs",
        python_callable=ingest_jobs,
    )
    finish = PythonOperator(
        task_id="finish",
        python_callable=log_finish,
        trigger_rule="all_success",
    )

    start >> ingest >> finish
