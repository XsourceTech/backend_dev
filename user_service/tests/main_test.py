import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from database_sharing_service.app import models
from unittest.mock import MagicMock
from user_service.app.main import user_app
from database_sharing_service.app.crud import *

client = TestClient(user_app)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
mock_password = "123456"
mock_user = models.User(id=0, email="test@example.com", user_name="string",
                        hashed_password=pwd_context.hash(mock_password), is_active=False, source="string",
                        user_identity="string")
auth_token = generate_auth_token(user_id=mock_user.id, email=mock_user.email, expiration=10)
active_token = generate_active_token(email=mock_user.email, expiration=10)
reset_token = generate_reset_token(email=mock_user.email, expiration=10)

def test_signup(mocker):
    mock_get_user_by_email = mocker.patch("user_service.app.main.get_user_by_email", return_value=None)
    mock_create_user = mocker.patch("user_service.app.main.create_user", return_value=mock_user)
    mock_generate_active_token = mocker.patch("user_service.app.main.generate_active_token", return_value=auth_token)
    mock_send_activation_email = mocker.patch("user_service.app.main.email_client.send_activation_email")
    response = client.post(
        "/signup",
        json={"email": mock_user.email, "user_name": mock_user.user_name, "password": mock_user.hashed_password,
              "source": mock_user.source},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "200", "message": "User created"}

    mock_get_user_by_email.assert_called_once_with(mocker.ANY, email=mock_user.email)
    mock_create_user.assert_called_once_with(mocker.ANY, mocker.ANY)
    mock_generate_active_token.assert_called_once_with(mock_user.email, 10)
    mock_send_activation_email.assert_called_once_with(mock_user.email, auth_token)


def test_signup_user_already_exists(mocker):
    mock_get_user_by_email = mocker.patch("user_service.app.main.get_user_by_email", return_value=mock_user)
    response = client.post(
        "/signup",
        json={"email": mock_user.email, "user_name": mock_user.user_name, "password": mock_user.hashed_password,
              "source": mock_user.source},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}

    mock_get_user_by_email.assert_called_once_with(mocker.ANY, email=mock_user.email)


def test_signup_token_generation_failed(mocker):
    mock_get_user_by_email = mocker.patch("user_service.app.main.get_user_by_email", return_value=None)
    mock_generate_active_token = mocker.patch("user_service.app.main.generate_active_token", return_value=None)
    response = client.post(
        "/signup",
        json={"email": mock_user.email, "user_name": mock_user.user_name, "password": mock_user.hashed_password,
              "source": mock_user.source},
    )
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to generate activation token"}

    mock_get_user_by_email.assert_called_once_with(mocker.ANY, email=mock_user.email)
    mock_generate_active_token.assert_called_once_with(mock_user.email, 10)


def test_login_success(mocker):
    mock_token = mocker.patch("user_service.app.main.auth_client.authenticate_user", return_value=auth_token)

    response = client.post(
        "/login",
        json={"email": mock_user.email, "password": mock_user.hashed_password},
    )

    assert response.status_code == 200
    assert response.json() == {"access_token": auth_token, "token_type": "bearer"}

    mock_token.assert_called_once_with(mock_user.email, mock_user.hashed_password)


def test_login_invalid_credentials(mocker):
    mock_token = mocker.patch("user_service.app.main.auth_client.authenticate_user", return_value=None)

    response = client.post(
        "/login",
        json={"email": mock_user.email, "password": mock_user.hashed_password},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}

    mock_token.assert_called_once_with(mock_user.email, mock_user.hashed_password)


def test_activate_user_success(mocker):
    mock_jwt_decode = mocker.patch("user_service.app.main.jwt.decode", return_value={"email": mock_user.email, "type": "active"})
    mock_get_user_by_email = mocker.patch("user_service.app.main.get_user_by_email", return_value=mock_user)
    mock_redirect_response = mocker.patch("user_service.app.main.RedirectResponse",
                                          return_value=MagicMock(status_code=307))
    mock_commit = mocker.patch("sqlalchemy.orm.Session.commit")

    response = client.get("/activate", params={"token": active_token})

    assert response.status_code == 200

    mock_jwt_decode.assert_called_once_with(active_token, mocker.ANY, algorithms=[mocker.ANY])
    mock_get_user_by_email.assert_called_once_with(mocker.ANY, email=mock_user.email)
    mock_commit.assert_called_once()
    mock_redirect_response.assert_called_once_with(url="/activation-success")


def test_activate_user_invalid_token(mocker):
    mock_jwt_decode = mocker.patch("user_service.app.main.jwt.decode", return_value={"email": None, "type": "active"})

    response = client.get("/activate", params={"token": active_token})

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}

    mock_jwt_decode.assert_called_once_with(active_token, mocker.ANY, algorithms=[mocker.ANY])


def test_activate_user_user_not_found(mocker):
    mock_jwt_decode = mocker.patch("user_service.app.main.jwt.decode", return_value={"email": mock_user.email,"type": "active"})
    mock_get_user_by_email = mocker.patch("user_service.app.main.get_user_by_email", return_value=None)

    response = client.get("/activate", params={"token": active_token})

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

    mock_jwt_decode.assert_called_once_with(active_token, mocker.ANY, algorithms=[mocker.ANY])
    mock_get_user_by_email.assert_called_once_with(mocker.ANY, email=mock_user.email)


def test_activate_user_invalid_jwt(mocker):
    response = client.get("/activate", params={"token": "not_jwt_format"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}


def test_request_password_reset_success(mocker):
    mock_get_user_by_email = mocker.patch("user_service.app.main.get_user_by_email", return_value=mock_user)
    mock_generate_reset_token = mocker.patch("user_service.app.main.generate_reset_token", return_value=auth_token)
    mock_send_password_reset_email = mocker.patch("user_service.app.main.email_client.send_password_reset_email")
    response = client.post(
        "/password-reset-request",
        data={"email": mock_user.email}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "200", "message": "Email sent"}

    mock_get_user_by_email.assert_called_once_with(mocker.ANY, mock_user.email)
    mock_generate_reset_token.assert_called_once_with(mock_user.email, 10)
    mock_send_password_reset_email.assert_called_once_with(mock_user.email, auth_token)


def test_password_reset_request_user_not_found(mocker):
    mock_get_user_by_email = mocker.patch("user_service.app.main.get_user_by_email", return_value=None)

    response = client.post(
        "/password-reset-request",
        data={"email": mock_user.email}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

    mock_get_user_by_email.assert_called_once_with(mocker.ANY, mock_user.email)


def test_password_reset_request_invalid_token(mocker):
    mock_get_user_by_email = mocker.patch("user_service.app.main.get_user_by_email", return_value=mock_user)
    mock_generate_reset_token = mocker.patch("user_service.app.main.generate_reset_token", return_value=None)

    response = client.post(
        "/password-reset-request",
        data={"email": mock_user.email}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}

    mock_get_user_by_email.assert_called_once_with(mocker.ANY, mock_user.email)
    mock_generate_reset_token.assert_called_once_with(mock_user.email, 10)


def test_password_reset_success(mocker):
    mock_jwt_decode = mocker.patch("user_service.app.main.jwt.decode", return_value={"email": mock_user.email, "type": "reset"})
    mock_get_user_by_email = mocker.patch("user_service.app.main.get_user_by_email", return_value=mock_user)
    mock_commit = mocker.patch("sqlalchemy.orm.Session.commit")
    mock_redirect_response = mocker.patch("user_service.app.main.RedirectResponse", return_value=MagicMock(status_code=307))

    response = client.post(
        "/password-reset",
        data={"token": reset_token, "new_password": "new_password123"}
    )

    assert response.status_code == 200
    mock_jwt_decode.assert_called_once_with(reset_token, mocker.ANY, algorithms=[mocker.ANY])
    mock_get_user_by_email.assert_called_once_with(mocker.ANY, email=mock_user.email)
    mock_commit.assert_called_once()
    mock_redirect_response.assert_called_once_with(url="/password-reset-success")


def test_password_reset_invalid_token():

    response = client.post(
        "/password-reset",
        data={"token": reset_token[:-3], "new_password": "new_password123"}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}


def test_password_reset_user_not_found(mocker):
    mock_jwt_decode = mocker.patch("user_service.app.main.jwt.decode", return_value={"email": mock_user.email, "type": "reset"})
    mock_get_user_by_email = mocker.patch("user_service.app.main.get_user_by_email", return_value=None)

    response = client.post(
        "/password-reset",
        data={"token": reset_token, "new_password": "new_password123"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

    mock_jwt_decode.assert_called_once_with(reset_token, mocker.ANY, algorithms=[mocker.ANY])
    mock_get_user_by_email.assert_called_once_with(mocker.ANY, email=mock_user.email)


def test_password_reset_invalid_jwt():

    response = client.post(
        "/password-reset",
        data={"token": "invalid_jwt", "new_password": "new_password123"}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}


def test_get_user_by_id_success(mocker):
    mock_get_user_by_id = mocker.patch("user_service.app.main.get_user_by_id", return_value=mock_user)
    mock_encrypt_user_id = encrypt_user_id(mock_user.id)
    response = client.get(f"/user/{mock_encrypt_user_id}")

    assert response.status_code == 200
    assert response.json() == {
        "email": mock_user.email,
        "user_name": mock_user.user_name,
        'source': mock_user.source,
        'user_identity': mock_user.user_identity,
        "is_active": mock_user.is_active
    }

    mock_get_user_by_id.assert_called_once_with(mocker.ANY, user_id=decrypt_user_id(mock_encrypt_user_id))


def test_get_user_by_id_user_not_found(mocker):
    mock_get_user_by_id = mocker.patch("user_service.app.main.get_user_by_id", return_value=None)
    mock_encrypt_user_id = encrypt_user_id(mock_user.id)
    response = client.get(f"/user/{mock_encrypt_user_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

    mock_get_user_by_id.assert_called_once_with(mocker.ANY, user_id=decrypt_user_id(mock_encrypt_user_id))
