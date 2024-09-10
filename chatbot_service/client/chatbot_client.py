import requests

from database_sharing_service.app.schemas import *
from database_sharing_service.app.config import settings
from database_sharing_service.app.logging_config import get_logger

logger = get_logger("ChatbotClient")


class ChatbotClient:
    def __init__(self, base_url: str = settings.CHATBOT_SERVICE_URL):
        self.base_url = base_url

    def get_reply(self, bot_memory: BotMemory, part: Part, level: Level):
        """
        Call the /reply_msg endpoint to get a reply based on the user's bot memory and level.

        - **bot_memory**: The BotMemory object containing the current memory of the bot.
        - **level**: The Level of the information ('major', 'field', 'topic', 'title').

        Returns the bot's response message.
        """
        url = f"{self.base_url}/reply_msg"
        payload = {
            "bot_memory": bot_memory.dict(),
            "level": level.value,
            "part": part.value
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err} - Status Code: {http_err.response.status_code}")
            return None
        except requests.exceptions.RequestException as err:
            logger.error(f"Request error occurred: {err}")
            return None

    def summarize_info(self, bot_memory: BotMemory, part: Part):
        """
        Call the /summarize_info endpoint to get a summary of the bot memory.

        - **bot_memory**: The BotMemory object containing the current memory of the bot.

        Returns a general summary of the bot memory.
        """
        url = f"{self.base_url}/summarize_info"
        payload = {
            "bot_memory": bot_memory.dict(),
            "part": part.value
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err} - Status Code: {http_err.response.status_code}")
            return None
        except requests.exceptions.RequestException as err:
            logger.error(f"Request error occurred: {err}")
            return None
