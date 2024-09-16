import pytest
from fastapi.testclient import TestClient
from article_service.app.main import article_app
from database_sharing_service.app import schemas, models
from article_service.app import main
from unittest.mock import MagicMock
from passlib.context import CryptContext

client = TestClient(article_app)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Mock data
mock_user_id = 1
mock_token = "validtoken"
mock_invalid_token = "invalidtoken"
mock_encrypted_id = "encrypted_id"
mock_decrypted_id = 1

# Mock article data
mock_article = models.Article(
    article_id=1,
    article_title="Test Article",
    article_major="Computer Science",
    article_field="AI",
    article_topic="Machine Learning",
    id=mock_user_id
)


def test_get_article_success(mocker):
    # Mock the auth_client.validate_token to return a valid token_data
    mock_token_data = {'id': mock_user_id}
    mocker.patch.object(main.auth_client, 'validate_token', return_value=mock_token_data)

    # Mock the get_article_by_user_id to return a list of articles
    mocker.patch('article_service.app.main.get_article_by_user_id', return_value=[mock_article])

    # Mock the encrypt_id function
    mocker.patch('article_service.app.main.encrypt_id', return_value=mock_encrypted_id)

    # Send the request
    response = client.get("/get-article", params={"token": mock_token})

    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert "article_infos" in data
    assert len(data["article_infos"]) == 1
    assert data["article_infos"][0]["id"] == mock_encrypted_id
    assert data["article_infos"][0]["title"] == "Test Article"
    assert data["article_infos"][0]["major"] == "Computer Science"
    assert data["article_infos"][0]["field"] == "AI"
    assert data["article_infos"][0]["topic"] == "Machine Learning"


def test_get_article_invalid_token(mocker):
    # Mock the auth_client.validate_token to return None
    mocker.patch.object(main.auth_client, 'validate_token', return_value=None)

    # Send the request with invalid token
    response = client.get("/get-article", params={"token": mock_invalid_token})

    # Check the response
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_get_article_no_user_id_in_token(mocker):
    # Mock the auth_client.validate_token to return token_data without 'id'
    mock_token_data = {"None": None}
    mocker.patch.object(main.auth_client, 'validate_token', return_value=mock_token_data)

    # Send the request
    response = client.get("/get-article", params={"token": mock_token})

    # Check the response
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid token data"}


def test_get_article_no_articles_found(mocker):
    # Mock the auth_client.validate_token to return a valid token_data
    mock_token_data = {'id': mock_user_id}
    mocker.patch.object(main.auth_client, 'validate_token', return_value=mock_token_data)

    # Mock the get_article_by_user_id to return None
    mocker.patch('article_service.app.main.get_article_by_user_id', return_value=None)

    # Send the request
    response = client.get("/get-article", params={"token": mock_token})

    # Check the response
    assert response.status_code == 404
    assert response.json() == {"detail": "No articles found for this user"}


def test_get_article_by_id_success(mocker):
    # Mock the decrypt_id function
    mocker.patch('article_service.app.main.decrypt_id', return_value=mock_decrypted_id)

    # Mock the get_article_by_article_id to return an article
    mocker.patch('article_service.app.main.get_article_by_article_id', return_value=mock_article)

    # Mock the encrypt_id function
    mocker.patch('article_service.app.main.encrypt_id', return_value=mock_encrypted_id)

    # Send the request
    response = client.get(f"/get-article/{mock_encrypted_id}")

    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == mock_encrypted_id
    assert data["title"] == "Test Article"
    assert data["major"] == "Computer Science"
    assert data["field"] == "AI"
    assert data["topic"] == "Machine Learning"

def test_get_article_by_id_not_found(mocker):
    # Mock the decrypt_id function
    mocker.patch('article_service.app.main.decrypt_id', return_value=mock_decrypted_id)

    # Mock the get_article_by_article_id to return None
    mocker.patch('article_service.app.main.get_article_by_article_id', return_value=None)

    # Send the request
    response = client.get(f"/get-article/{mock_encrypted_id}")

    # Check the response
    assert response.status_code == 404
    assert response.json() == {"detail": "Article not found"}

def test_delete_article_success(mocker):
    # Mock the decrypt_id function
    mocker.patch('article_service.app.main.decrypt_id', return_value=mock_decrypted_id)

    # Mock the delete_article function to return True
    mocker.patch('article_service.app.main.delete_article', return_value=True)

    # Send the request
    response = client.delete(f"/delete-article/{mock_encrypted_id}")

    # Check the response
    assert response.status_code == 200
    assert response.json() == {"status": "200", "message": "Article deleted"}

def test_delete_article_not_found(mocker):
    # Mock the decrypt_id function
    mocker.patch('article_service.app.main.decrypt_id', return_value=mock_decrypted_id)

    # Mock the delete_article function to return False
    mocker.patch('article_service.app.main.delete_article', return_value=False)

    # Send the request
    response = client.delete(f"/delete-article/{mock_encrypted_id}")

    # Check the response
    assert response.status_code == 404
    assert response.json() == {"detail": "Article not found"}

def test_create_article_success(mocker):
    # Mock the create_article function
    mocker.patch('article_service.app.main.create_article', return_value=mock_article)

    # Send the request
    article_data = {
        "user_id": str(mock_user_id),
        "title": "Test Article",
        "major": "Computer Science",
        "field": "AI",
        "topic": "Machine Learning"
    }
    response = client.post("/create-article", json=article_data)

    # Check the response
    assert response.status_code == 200
    assert response.json() == {"status": "200", "message": "Article created"}

def test_create_article_exception(mocker):
    # Mock the create_article function to raise an exception
    mocker.patch('article_service.app.main.create_article', side_effect=Exception("Database Error"))

    # Send the request
    article_data = {
        "user_id": str(mock_user_id),
        "title": "Test Article",
        "major": "Computer Science",
        "field": "AI",
        "topic": "Machine Learning"
    }
    response = client.post("/create-article", json=article_data)

    # Check the response
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
