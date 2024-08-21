import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from auth_service.app import auth_app
from database_sharing_service.app import schemas, models
from passlib.context import CryptContext

from database_sharing_service.app.config import settings
from database_sharing_service.app.crud import generate_auth_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
client = TestClient(auth_app)
mock_password = "123456"
mock_user = models.User(id=0, email="test@example.com", user_name="string",
                        hashed_password=pwd_context.hash(mock_password), is_active=False, source="string",
                        user_identity="string")


@patch("auth_service.app.main.get_user_by_email")
def test_generate_token_success(mock_get_user):
    mock_get_user.return_value = mock_user
    response = client.post(
        "/generate-token",
        json={"email": mock_user.email, "password": mock_password}
    )

    assert response.status_code == 200
    token_response = schemas.TokenResponse(**response.json())
    assert token_response.access_token is not None
    assert token_response.token_type == "bearer"


@patch("auth_service.app.main.get_user_by_email")
def test_generate_token_invalid_email(mock_get_user):
    mock_get_user.return_value = None
    response = client.post(
        "/generate-token",
        json={"email": "wrong_email", "password": mock_password}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid email or password"}


@patch("auth_service.app.main.get_user_by_email")
def test_generate_token_invalid_password(mock_get_user):
    mock_get_user.return_value = mock_user
    response = client.post(
        "/generate-token",
        json={"email": mock_user.email, "password": "123456789"}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid email or password"}


def test_validate_token_success():
    mock_token = generate_auth_token(mock_user.email, settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    response = client.post(
        "/validate-token",
        params={"token": mock_token}
    )
    assert response.status_code == 200
    assert response.json() == {"email": mock_user.email}


def test_validate_token_invalid():
    response = client.post(
        "/validate-token",
        params={"token": "invalidtoken"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}

def test_validate_token_expired():
    mock_token = generate_auth_token(mock_user.email, -1)

    response = client.post(
        "/validate-token",
        params={"token": mock_token}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
