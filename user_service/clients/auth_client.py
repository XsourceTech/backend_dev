import requests
from fastapi import FastAPI, HTTPException
from database_sharing_service.app.config import settings
from database_sharing_service.app.logging_config import get_logger

logger = get_logger("AuthClient")


class AuthClient:
    def __init__(self, base_url: str = settings.AUTH_SERVICE_URL):
        self.base_url = base_url

    def authenticate_user(self, email: str, password: str):
        """
        Call the generate-token endpoint of the Auth Service to generate a JWT token.

        - **email**: The email address for which to generate the token.
        - **password**: The password for the given email.

        Returns the generated JWT token generate by endpoint of the Auth Service.
        """
        url = f"{self.base_url}/generate-token"
        try:
            response = requests.post(url, json={"email": email, "password": password})

            response.raise_for_status()

            token = response.json().get("access_token")
            if not token:
                raise HTTPException(status_code=400, detail="Token generation failed")
            return token
        except requests.exceptions.HTTPError as http_err:
            try:
                error_detail = response.json().get("detail", "Unknown error")
            except ValueError:
                error_detail = "Unknown error"
            raise HTTPException(status_code=response.status_code, detail=error_detail)
        except Exception as err:
            raise HTTPException(status_code=500, detail=f"An error occurred: {err}")

    def validate_token(self, token: str):
        """
        Call the validate-token endpoint of the Auth Service to validate a JWT token.

        - **token**: The JWT token to validate.

        Returns the extracted user information if the token is valid by validate-token endpoint.
        """
        url = f"{self.base_url}/validate-token"
        try:
            response = requests.post(url, params={"token": token})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err} - Status Code: {http_err.response.status_code}")
            return None
        except requests.exceptions.RequestException as err:
            logger.error(f"Request error occurred: {err}")
            return None
