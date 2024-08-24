import logging
import os

from dotenv import load_dotenv

# Load a specific .env.production file based on the environment
environment = os.getenv('ENV', 'local')  # Default to 'local' if ENV is not set

# Construct the file name
dotenv_path = f'"../../.env.production.{environment}'

# Load the environment variables from the specified file
load_dotenv(dotenv_path)


class ServiceLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return f"[{self.extra['service_name']}] {msg}", kwargs

def get_logger(service_name):
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return ServiceLoggerAdapter(logger, {'service_name': service_name})