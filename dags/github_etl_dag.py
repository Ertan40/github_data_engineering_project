from datetime import datetime
from airflow.sdk import dag, task  # type: ignore
from src.main import run_pipeline
import logging

logger = logging.getLogger(__name__)


@dag(
    dag_id="github_repository_etl",
    description="Extract GitHub repositories and load Bronze, Silver and Gold layers",
    start_date=datetime(2026, 11, 22),
    schedule=None,
    catchup=False,
    tags=["github", "etl", "mssql"],
)
def github_repository_etl():
    @task
    def execute_etl():
        logger.info("Starting GitHub ETL through Airflow...")
        run_pipeline()
        logger.info("GitHub ETL task completed successfully.")

    execute_etl()



github_etl = github_repository_etl()
