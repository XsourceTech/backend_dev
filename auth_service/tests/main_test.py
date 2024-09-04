import pytest
from fastapi.testclient import TestClient
from auth_service.app import auth_app
from database_sharing_service.app import schemas, models
from passlib.context import CryptContext

from database_sharing_service.app.crud import *
from database_sharing_service.app.config import settings
from database_sharing_service.app.crud import generate_auth_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
client = TestClient(auth_app)
mock_password = "123456"
mock_user = models.User(id=1, email="test@example.com", user_name="string",
                        hashed_password=pwd_context.hash(mock_password), is_active=False, source="string",
                        user_identity="string")


def test_generate_token_success(mocker):
    mock_get_user_by_email = mocker.patch("auth_service.app.main.get_user_by_email", return_value=mock_user)
    response = client.post(
        "/generate-token",
        json={"email": mock_user.email, "password": mock_password}
    )

    assert response.status_code == 200
    token_response = schemas.TokenResponse(**response.json())
    assert token_response.access_token is not None
    assert token_response.token_type == "bearer"

    mock_get_user_by_email.assert_called_once_with(mocker.ANY, mock_user.email)


def test_generate_token_invalid_email(mocker):
    mock_get_user_by_email = mocker.patch("auth_service.app.main.get_user_by_email", return_value=None)
    response = client.post(
        "/generate-token",
        json={"email": "wrong_email", "password": mock_password}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid email or password"}

    mock_get_user_by_email.assert_called_once_with(mocker.ANY, "wrong_email")


def test_generate_token_invalid_password(mocker):
    mock_get_user_by_email = mocker.patch("auth_service.app.main.get_user_by_email", return_value=mock_user)
    response = client.post(
        "/generate-token",
        json={"email": mock_user.email, "password": "123456789"}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid email or password"}

    mock_get_user_by_email.assert_called_once_with(mocker.ANY, mock_user.email)


def test_validate_token_success():
    mock_token = generate_auth_token(mock_user.id, mock_user.email, settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    response = client.post(
        "/validate-token",
        params={"token": mock_token}
    )
    assert response.status_code == 200
    assert response.json().get("email") == mock_user.email
    assert response.json().get("id") is not None


def test_validate_token_invalid():
    response = client.post(
        "/validate-token",
        params={"token": "invalidtoken"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


def test_validate_token_expired():
    mock_token = generate_auth_token(mock_user.email, mock_user.id, -1)

    response = client.post(
        "/validate-token",
        params={"token": mock_token}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
