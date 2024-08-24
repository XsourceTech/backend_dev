import requests
from database_sharing_service.app.config import settings


class EmailClient:
    def __init__(self, base_url: str = settings.EMAIL_SERVICE_URL):
        self.base_url = base_url

    def send_activation_email(self, email: str, token: str):
        response = requests.post(
            f"{self.base_url}/send-activation-email",
            params={"email": email, "token": token}
        )
        return response.status_code == 200

    def send_password_reset_email(self, email: str, token: str):
        response = requests.post(
            f"{self.base_url}/send-password-reset-email",
            params={"email": email, "token": token}
        )
        return response.status_code == 200
