import requests
from fastapi import FastAPI, HTTPException
from database_sharing_service.app.config import settings


class EmailClient:
    def __init__(self, base_url: str = settings.EMAIL_SERVICE_URL):
        self.base_url = base_url

    def send_activation_email(self, email: str, token: str):
        response = requests.post(
            f"{self.base_url}/send-activation-email",
            params={"email": email, "token": token}
        )
        if response.status_code != 200:
            try:
                error_detail = response.json().get("detail", "Failed to send activation email")
            except ValueError:
                error_detail = "Failed to send activation email"
            raise HTTPException(status_code=response.status_code, detail=error_detail)

        return True

    def send_password_reset_email(self, email: str, token: str):
        response = requests.post(
            f"{self.base_url}/send-password-reset-email",
            params={"email": email, "token": token}
        )
        if response.status_code != 200:
            try:
                error_detail = response.json().get("detail", "Failed to send password reset email")
            except ValueError:
                error_detail = "Failed to send password reset email"
            raise HTTPException(status_code=response.status_code, detail=error_detail)

        return True
