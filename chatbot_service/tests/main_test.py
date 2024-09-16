import pytest
from fastapi.testclient import TestClient
from chatbot_service.app.main import chatbot_app, chatbot_client, article_client
from database_sharing_service.app import schemas
from unittest.mock import Mock, patch
from jose import jwt, JWTError
from datetime import datetime, timedelta
from database_sharing_service.app.config import settings

client = TestClient(chatbot_app)


@pytest.fixture
def valid_token():
    # 生成用于测试的有效令牌
    to_encode = {"type": "auth", "id": 1}
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return {"access_token": encoded_jwt, "token_type": "bearer"}


def test_get_response_success(mocker, valid_token):
    # 模拟 jwt.decode
    mock_payload = {"type": "auth", "id": 1}
    mocker.patch("chatbot_service.app.main.jwt.decode", return_value=mock_payload)

    # 模拟 get_current_level 返回有效级别
    mocker.patch("chatbot_service.app.main.get_current_level", return_value="topic")

    # 模拟 chatbot_client.get_reply 返回有效回复
    mock_reply = {
        "bot_memory": [
            {"role": "user", "content": "这是用户的消息。"},
            {"role": "assistant", "content": "这是机器人的回复。"}
        ]
    }
    mocker.patch.object(chatbot_client, 'get_reply', return_value=mock_reply)

    # 准备测试数据
    bot_memory = {
        "chat_messages": [
            {"role": "user", "content": "你好"}
        ]
    }
    token = valid_token
    params = {
        "part": "article"
    }

    # 调用 API，将 'token' 放入请求体的 JSON 中
    response = client.post(
        "/get-response",
        json={"bot_memory": bot_memory, "token": token},
        params=params
    )

    # 检查响应
    assert response.status_code == 200
    json_response = response.json()
    assert "bot_memory" in json_response
    assert "is_end" in json_response
    assert isinstance(json_response["bot_memory"]["chat_messages"], list)


def test_get_response_invalid_token(mocker):
    # 模拟 jwt.decode 引发 JWTError
    mocker.patch("chatbot_service.app.main.jwt.decode", side_effect=JWTError())

    # 准备测试数据
    bot_memory = {
        "chat_messages": [
            {"role": "user", "content": "你好"}
        ]
    }
    token = {
        "access_token": "invalid_token",
        "token_type": "bearer"
    }
    params = {
        "part": "article"
    }

    # 调用 API
    response = client.post(
        "/get-response",
        json={"bot_memory": bot_memory, "token": token},
        params=params
    )

    # 检查响应
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}


def test_get_response_invalid_token_type(mocker, valid_token):
    # 模拟 jwt.decode 返回无效类型
    mock_payload = {"type": "other", "id": 1}
    mocker.patch("chatbot_service.app.main.jwt.decode", return_value=mock_payload)

    # 准备测试数据
    bot_memory = {
        "chat_messages": [
            {"role": "user", "content": "你好"}
        ]
    }
    token = valid_token
    params = {
        "part": "article"
    }

    # 调用 API
    response = client.post(
        "/get-response",
        json={"bot_memory": bot_memory, "token": token},
        params=params
    )

    # 检查响应
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}


def test_get_response_empty_bot_memory(mocker, valid_token):
    # 模拟 jwt.decode
    mock_payload = {"type": "auth", "id": 1}
    mocker.patch("chatbot_service.app.main.jwt.decode", return_value=mock_payload)

    # 模拟 get_current_level 返回 None
    mocker.patch("chatbot_service.app.main.get_current_level", return_value=None)

    # 准备测试数据
    bot_memory = {
        "chat_messages": []
    }
    token = valid_token
    params = {
        "part": "article"
    }

    # 调用 API
    response = client.post(
        "/get-response",
        json={"bot_memory": bot_memory, "token": token},
        params=params
    )

    # 检查响应
    assert response.status_code == 400
    assert response.json() == {"detail": "Input empty or role incorrect."}


def test_get_response_chat_ended(mocker, valid_token):
    # 模拟 jwt.decode
    mock_payload = {"type": "auth", "id": 1}
    mocker.patch("chatbot_service.app.main.jwt.decode", return_value=mock_payload)

    # 模拟 get_current_level 返回 'end'
    mocker.patch("chatbot_service.app.main.get_current_level", return_value='end')

    # 准备测试数据
    bot_memory = {
        "chat_messages": [
            {"role": "user", "content": "谢谢，再见"}
        ]
    }
    token = valid_token
    params = {
        "part": "article"
    }

    # 调用 API
    response = client.post(
        "/get-response",
        json={"bot_memory": bot_memory, "token": token},
        params=params
    )

    # 检查响应
    assert response.status_code == 410
    assert response.json() == {"detail": "Chat ended."}


def test_get_response_reply_failed(mocker, valid_token):
    # 模拟 jwt.decode
    mock_payload = {"type": "auth", "id": 1}
    mocker.patch("chatbot_service.app.main.jwt.decode", return_value=mock_payload)

    # 模拟 get_current_level 返回 'topic'
    mocker.patch("chatbot_service.app.main.get_current_level", return_value='topic')

    # 模拟 chatbot_client.get_reply 返回 None
    mocker.patch.object(chatbot_client, 'get_reply', return_value=None)

    # 准备测试数据
    bot_memory = {
        "chat_messages": [
            {"role": "user", "content": "请给我一些建议"}
        ]
    }
    token = valid_token
    params = {
        "part": "article"
    }

    # 调用 API
    response = client.post(
        "/get-response",
        json={"bot_memory": bot_memory, "token": token},
        params=params
    )

    # 检查响应
    assert response.status_code == 503
    assert response.json() == {"detail": "Failed to get reply from the chatbot."}


def test_summarize_success_article(mocker, valid_token):
    # 模拟 jwt.decode
    mock_payload = {"type": "auth", "id": 1}
    mocker.patch("chatbot_service.app.main.jwt.decode", return_value=mock_payload)

    # 模拟 chatbot_client.summarize_info 返回摘要
    summary = {
        "title": "测试标题",
        "major": "测试专业",
        "field": "测试领域",
        "topic": "测试主题"
    }
    mocker.patch.object(chatbot_client, 'summarize_info', return_value=summary)

    # 模拟 article_client.create_article 返回响应
    response_message = {"status": "string", "message": "string"}
    mocker.patch.object(article_client, 'create_article', return_value=response_message)

    # 准备测试数据
    bot_memory = {
        "chat_messages": [
            {"role": "user", "content": "你好"}
        ]
    }
    token = valid_token
    params = {
        "part": "article"
    }

    # 调用 API
    response = client.post(
        "/summarize",
        json={"bot_memory": bot_memory, "token": token},
        params=params
    )

    # 检查响应
    assert response.status_code == 200
    json_response = response.json()
    assert json_response == response_message


def test_summarize_invalid_token(mocker):
    # 模拟 jwt.decode 引发 JWTError
    mocker.patch("chatbot_service.app.main.jwt.decode", side_effect=JWTError())

    # 准备测试数据
    bot_memory = {
        "chat_messages": [
            {"role": "user", "content": "你好"}
        ]
    }
    token = {
        "access_token": "invalid_token",
        "token_type": "bearer"
    }
    params = {
        "part": "article"
    }

    # 调用 API
    response = client.post(
        "/summarize",
        json={"bot_memory": bot_memory, "token": token},
        params=params
    )

    # 检查响应
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}


def test_summarize_summary_failed(mocker, valid_token):
    # 模拟 jwt.decode
    mock_payload = {"type": "auth", "id": 1}
    mocker.patch("chatbot_service.app.main.jwt.decode", return_value=mock_payload)

    # 模拟 chatbot_client.summarize_info 返回 None
    mocker.patch.object(chatbot_client, 'summarize_info', return_value=None)

    # 准备测试数据
    bot_memory = {
        "chat_messages": [
            {"role": "user", "content": "请总结一下"}
        ]
    }
    token = valid_token
    params = {
        "part": "article"
    }

    # 调用 API
    response = client.post(
        "/summarize",
        json={"bot_memory": bot_memory, "token": token},
        params=params
    )

    # 检查响应
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to get summary from the chatbot."}


def test_summarize_create_article_failed(mocker, valid_token):
    # 模拟 jwt.decode
    mock_payload = {"type": "auth", "id": 1}
    mocker.patch("chatbot_service.app.main.jwt.decode", return_value=mock_payload)

    # 模拟 chatbot_client.summarize_info 返回摘要
    summary = {
        "title": "测试标题",
        "major": "测试专业",
        "field": "测试领域",
        "topic": "测试主题"
    }
    mocker.patch.object(chatbot_client, 'summarize_info', return_value=summary)

    # 模拟 article_client.create_article 返回 None
    mocker.patch.object(article_client, 'create_article', return_value=None)

    # 准备测试数据
    bot_memory = {
        "chat_messages": [
            {"role": "user", "content": "请创建文章"}
        ]
    }
    token = valid_token
    params = {
        "part": "article"
    }

    # 调用 API
    response = client.post(
        "/summarize",
        json={"bot_memory": bot_memory, "token": token},
        params=params
    )

    # 检查响应
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to create article."}

