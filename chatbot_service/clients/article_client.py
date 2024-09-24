import requests

from database_sharing_service.app.models import Article
from database_sharing_service.app.schemas import *
from database_sharing_service.app.config import settings
from database_sharing_service.app.logging_config import get_logger

logger = get_logger("ArticleClient")


class ArticleClient:
    def __init__(self, base_url: str = settings.ARTICLE_SERVICE_URL):
        self.base_url = base_url

    def create_article(self, article_creat: ArticleCreate):
        url = f"{self.base_url}/create-article"
        try:
            response = requests.post(url, json=article_creat.dict())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err} - Status Code: {http_err.response.status_code}")
            return None
        except requests.exceptions.RequestException as err:
            logger.error(f"Request error occurred: {err}")
            return None
