import logging
import os

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Logs to stderr
        logging.FileHandler("app.log")  # Logs to a file
    ]
)

# Logger for each service to use
logger = logging.getLogger("authentication_service")

# setting up logging level based on environment
if os.getenv("ENV") == "production":
    logger.setLevel(logging.WARNING)
else:
    logger.setLevel(logging.DEBUG)