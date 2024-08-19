import requests


class AuthClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def generate_token(self, email: str, password: str):
        """
        Call the generate-token endpoint of the Auth Service to generate a JWT token.

        - **email**: The email address for which to generate the token.
        - **password**: The password for the given email.

        Returns the generated JWT token generate by endpoint of the Auth Service.
        """
        url = f"{self.base_url}/generate-token"
        response = requests.post(url, json={"email": email, "password": password})
        response.raise_for_status()
        return response.json()

    def validate_token(self, token: str):
        """
        Call the validate-token endpoint of the Auth Service to validate a JWT token.

        - **token**: The JWT token to validate.

        Returns the extracted user information if the token is valid by validate-token endpoint.
        """
        url = f"{self.base_url}/validate-token"
        response = requests.post(url, json={"token": token})
        response.raise_for_status()
        return response.json()
