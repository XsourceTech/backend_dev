import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from email_service.app.main import email_app
from fastapi_mail import FastMail

client = TestClient(email_app)


def test_send_activation_email_success():
    with patch.object(FastMail, "send_message", return_value=None) as mock_send:
        response = client.post(
            "/send-activation-email",
            params={"email": "test@example.com", "token": "fake_token"}
        )
        print(response.json())  # Add this line to inspect the error details
        assert response.status_code == 200
        assert response.json()["message"] == "Activation email sent"
        mock_send.assert_called_once()


def test_send_activation_email_missing_email():
    response = client.post(
        "/send-activation-email",
        params={"token": "fake_token"}
    )
    assert response.status_code == 422  # Unprocessable Entity


def test_send_activation_email_invalid_email():
    response = client.post(
        "/send-activation-email",
        params={"email": "invalid-email", "token": "fake_token"}
    )
    assert response.status_code == 422  # Unprocessable Entity


def test_send_password_reset_email_success():
    with patch.object(FastMail, "send_message", return_value=None) as mock_send:
        response = client.post(
            "/send-password-reset-email",
            params={"email": "test@example.com", "token": "fake_token"}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Password reset email sent"
        mock_send.assert_called_once()
