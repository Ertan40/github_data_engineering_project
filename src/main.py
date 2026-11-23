import logging
from src.extract.github_api import extract
from src.transform.clean_data import transform
from src.load.mssql_loader import load_bronze, load_silver, load_gold_snapshot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


def run_pipeline():
    logger.info("Starting GitHub ETL pipeline...")

    try:
        # ED: Extract
        result = extract(max_results=250)

        repositories = result["repositories"]
        raw_pages = result["raw_pages"]
        batch_id = result["batch_id"]
        # ED: Python logging supports deferred formatting. It only formats the message when the message
        # actually needs to be emitted. This is a good practice, particularly when logging frequently.
        # print(f"Batch ID: {batch_id}"
        logger.info("Batch ID: %s", batch_id)
        # print(f"Repositories extracted: {len(repositories)}")
        logger.info("Repositories extracted: %s", len(repositories))
        logger.info("Raw API pages extracted: %s", len(raw_pages))

        # ED: Load Bronze
        bronze_total = load_bronze(raw_pages)
        logger.info("Bronze records loaded: %s", bronze_total)

        # ED: Transform
        cleaned_repositories = transform(repositories)
        logger.info("Repositories after transformation: %s", len(cleaned_repositories))

        # ED: Load Silver
        silver_total = load_silver(cleaned_repositories)
        logger.info("Silver total repositories: %s", silver_total)
        # ED: Load Gold
        gold_total = load_gold_snapshot()
        logger.info("Gold snapshot total: %s", gold_total)
        logger.info("GitHub ETL pipeline completed successfully.")
    except Exception:
        logger.exception("ETL pipeline failed!")
        raise


if __name__ == "__main__":
    run_pipeline()
