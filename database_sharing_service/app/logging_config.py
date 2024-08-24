import logging
import os

from dotenv import load_dotenv

# Load the shared .env file
load_dotenv(dotenv_path="../../.env")

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