from fastapi import FastAPI

from database_sharing_service.app import schemas

auth_app = FastAPI(
    title="Auth Service API",
    description="API for managing authentication, including JWT token generation and validation.",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Operations related to user authentication, such as token generation and validation.",
        },
    ],
)


@auth_app.post("/generate-token", response_model=schemas.TokenResponse, tags=["Authentication"], summary="Generate JWT Token",
          description="Generate a JWT token for the given email.")
def generate_token(request: schemas.TokenRequest):
    """
    Generate a JWT token for the given email.

    - **email**: The email address for which to generate the token.

    Returns the generated JWT token.
    """
    pass


@auth_app.post("/validate-token", response_model=schemas.TokenData, tags=["Authentication"], summary="Validate JWT Token",
          description="Validate a JWT token and extract the user information.")
def validate_token(token: str):
    """
    Validate a JWT token and extract the user information.

    - **token**: The JWT token to validate.

    Returns the extracted user information if the token is valid.
    """
    pass