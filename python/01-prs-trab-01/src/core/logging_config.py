import logging
from src.config.settings import settings

def setup_logging():
    logging.basicConfig(
        filename=settings.logging.file_path,
        level=getattr(logging, settings.logging.level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def log_event(level: str, operation: str, details: str):
    logger = logging.getLogger("science_vault")
    message = f"{operation} {details}"
    
    if level.upper() == "INFO":
        logger.info(message)
    elif level.upper() == "WARNING":
        logger.warning(message)
    elif level.upper() == "ERROR":
        logger.error(message)
