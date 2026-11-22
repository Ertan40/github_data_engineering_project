from src.common.logger import get_logger
from src.extract.github_api import extract
from src.transform.clean_data import transform
from src.load.mssql_loader import load_bronze, load_silver, load_gold_snapshot

logger = get_logger(__name__)


def run_pipeline():
    # print("Starting GitHub ETL pipeline...") ED: replaced them with logger.info:
    logger.info("Starting GitHub ETL pipeline...")

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
    # print(f"Raw API pages extracted: {len(raw_pages)}")
    logger.info("Raw API pages extracted: %s", len(raw_pages))

    # ED: Load Bronze
    bronze_total = load_bronze(raw_pages)
    # print(f"Bronze records loaded: {bronze_total}")
    logger.info("Bronze records loaded: %s", bronze_total)

    # ED: Transform
    cleaned_repositories = transform(repositories)
    # print(f"Repositories after transformation: {len(cleaned_repositories)}")
    logger.info("Repositories after transformation: %s", len(cleaned_repositories))

    # ED: Load Silver
    silver_total = load_silver(cleaned_repositories)
    # print(f"Silver total repositories: {silver_total}")
    logger.info("Silver total repositories: %s", silver_total)
    # ED: Load Gold
    gold_total = load_gold_snapshot()
    # print(f"Gold snapshot total: {gold_total}")
    logger.info("Gold snapshot total: %s", gold_total)

    logger.info("GitHub ETL pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()
