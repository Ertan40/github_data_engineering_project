from src.common.logger import get_logger

logger = get_logger(__name__)

logger.debug("Debug message")
logger.info("ETL started")
logger.warning("API returned incomplete results")
logger.error("Database operation failed")