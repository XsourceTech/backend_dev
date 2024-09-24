from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from chatbot_service.clients.article_client import ArticleClient
from database_sharing_service.app.crud import *
from database_sharing_service.app.database import get_db
from database_sharing_service.app.logging_config import get_logger
from chatbot_service.app.utils import *
from chatbot_service.clients.model_chatbot_client import ModelChatbotClient
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import time
import uvicorn

from database_sharing_service.app.schemas import BotMemory

chatbot_app = FastAPI(
    title="ChatbotArticle Service",
    description="Service for generating and summarizing chatbot responses.",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Chatbot Responses",
            "description": "Operations related to chatbot responses generation and summarization.",
        },
    ],
)
"""
chatbot_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有Header
)
"""

logger = get_logger("Chatbot_Service")

chatbot_client = ModelChatbotClient()
article_client = ArticleClient()


@chatbot_app.post("/get-response",
                  response_model=schemas.BotMemoryWithFlag,
                  tags=["Chatbot Responses"],
                  summary="Generate next bot message",
                  description="Generate the next bot message based on memory, token, and other parameters.")
def get_response(bot_memory: schemas.BotMemory, token: schemas.Token,
                 part: str = Query(..., description="Part name of chatbot like article, abstract etc"),
                 db: Session = Depends(get_db)):
    """
    Generate the next bot message.

    - **bot_memory**: The memory of the bot (conversation history).
    - **token**: The session token (authentication information).
    - **end**: A flag indicating whether it's the end of the conversation.
    - **part**: The part name of chatbot like article, abstract etc.

    Returns the updated bot memory with the next message.
    """

    start_time = time.time()  # 开始时间
    logger.info(
        f"Request start - get-response, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        payload = jwt.decode(token.access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "auth":
            logger.warning("Token validation failed: Invalid token type for authentication.")
            raise HTTPException(status_code=400, detail="Invalid credentials")
    except JWTError as e:
        logger.error(f"Token decoding failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid credentials")

    old_level_str = get_current_level(bot_memory, part)
    if old_level_str is None:
        logger.warning(f"User input empty.")
        raise HTTPException(status_code=400, detail="Input empty or role incorrect.")

    if old_level_str == 'end':
        logger.warning(f"Chat ended.")
        raise HTTPException(status_code=410, detail="Chat ended.")

    chatbot_start_time = time.time()  # 开始时间
    logger.info(
        f"Request start - chatbot-get-response, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    reply = chatbot_client.get_reply(bot_memory, schemas.Part(part), schemas.Level(old_level_str))
    if reply is None:
        logger.warning(f"Get reply failed.")
        raise HTTPException(status_code=503, detail="Failed to get reply from the chatbot.")
    logger.info(f"Reply successfully.")

    chatbot_end_time = time.time()  # 结束时间
    chatbot_duration = chatbot_end_time - chatbot_start_time
    logger.info(
        f"Request end - chatbot-get-response, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}, Duration: {chatbot_duration:.2f} seconds")

    bot_memory_reply = BotMemory.parse_obj({"chat_messages": reply.get('bot_memory')})
    new_level_str = get_current_level(bot_memory_reply, part)
    end = get_current_level(bot_memory_reply, part) == 'end'
    if new_level_str != old_level_str and new_level_str != 'end':
        bot_memory_reply.chat_messages[-1].content += f"接下来我想和你聊聊{translate[new_level_str]}。"
    bot_memory_with_flag = schemas.BotMemoryWithFlag(bot_memory=bot_memory_reply, is_end=end)

    end_time = time.time()  # 结束时间
    duration = end_time - start_time
    logger.info(
        f"Request end - get-response, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}, Duration: {duration:.2f} seconds")

    return bot_memory_with_flag


@chatbot_app.post("/summarize",
                  response_model=schemas.Message,
                  tags=["Chatbot Responses"],
                  summary="Summarize the conversation",
                  description="Summarize the bot conversation and optionally create new data.")
def summarize(bot_memory: schemas.BotMemory, token: schemas.Token,
              part: str = Query(..., description="Part name of chatbot like article, abstract etc"),
              db: Session = Depends(get_db)):
    """
    Summarize the bot conversation.

    - **bot_memory**: The memory of the bot (conversation history).
    - **token**: The session token (authentication information).
    - **part**: The part name of chatbot like article, abstract etc.

    Returns a summarized message.
    """

    start_time = time.time()  # 开始时间
    logger.info(
        f"Request start - summarize, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        payload = jwt.decode(token.access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "auth":
            logger.warning("Token validation failed: Invalid token type for authentication.")
            raise HTTPException(status_code=400, detail="Invalid credentials")
        user_id = payload.get("id")
    except JWTError as e:
        logger.error(f"Token decoding failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid credentials")

    chatbot_start_time = time.time()  # 开始时间
    logger.info(
        f"Request start - chatbot-get-summary, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    summary = chatbot_client.summarize_info(bot_memory, schemas.Part(part))
    if summary is None:
        logger.warning(f"Get summary failed for user: {user_id}")
        raise HTTPException(status_code=500, detail="Failed to get summary from the chatbot.")

    chatbot_end_time = time.time()  # 结束时间
    chatbot_duration = chatbot_end_time - chatbot_start_time
    logger.info(
        f"Request end - chatbot-get-summary, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}, Duration: {chatbot_duration:.2f} seconds")

    if part == "article":
        if summary.get("title") is None or (summary.get("major") is None and summary.get("field") is None and summary.get("topic") is None):
            raise HTTPException(status_code=400, detail="Insufficient information to summarize the conversation.")
        article_create = schemas.ArticleCreate(title=summary.get("title"), major=summary.get("major"),
                                               field=summary.get("field"),
                                               topic=summary.get("topic"), user_id=str(user_id))
        response = article_client.create_article(article_create)
        if response is None:
            logger.warning(f"Article create failed for user: {user_id}")
            raise HTTPException(status_code=500, detail="Failed to create article.")

        end_time = time.time()  # 结束时间
        duration = end_time - start_time
        logger.info(
            f"Request end - summarize, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}, Duration: {duration:.2f} seconds")

        return response
    else:
        # generate article part infomation and save, use article_part service
        pass


if __name__ == "__main__":
    uvicorn.run("main:chatbot_app", host="0.0.0.0", port=8004, reload=True)
