from fastapi import requests
from database_sharing_service.app.config import settings


def send_activation_email(email: str, token: str):
    response = requests.post(
        f"{settings.EMAIL_SERVICE_URL}/send-activation-email",
        json={"email": email, "token": token}
    )
    return response.status_code == 200

def send_password_reset_email(email: str, token: str):
    response = requests.post(
        f"{settings.EMAIL_SERVICE_URL}/send-password-reset-email",
        json={"email": email, "token": token}
    )
    return response.status_code == 200