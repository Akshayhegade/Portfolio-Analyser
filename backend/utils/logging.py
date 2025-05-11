import logging

def setup_logging():
    """
    Configure application logging with a standard format
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

# Create a logger instance that can be imported by other modules
logger = setup_logging()
