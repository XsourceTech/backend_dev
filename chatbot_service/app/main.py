from fastapi import FastAPI, HTTPException, Depends, Query, responses, Path, Form

from chatbot_service.client.article_client import ArticleClient
from database_sharing_service.app import schemas
from database_sharing_service.app.config import settings
from database_sharing_service.app.crud import *
from database_sharing_service.app.database import get_db
from database_sharing_service.app.logging_config import get_logger
from chatbot_service.app.utils import *
from chatbot_service.client.chatbot_client import ChatbotClient
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import uvicorn

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

logger = get_logger("Chatbot_Service")

chatbot_client = ChatbotClient()
article_client = ArticleClient()


@chatbot_app.get("/get-response",
                 response_model=schemas.BotMemoryWithEnd,
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

    Returns the updated bot memory with the next message.
    """
    try:
        payload = jwt.decode(token.access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "auth":
            logger.warning("Token validation failed: Invalid token type for authentication.")
            raise HTTPException(status_code=400, detail="Invalid credentials")
        user_id = payload.get("id")
    except JWTError as e:
        logger.error(f"Token decoding failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid credentials")

    current_level_str = get_current_level(bot_memory, part)

    if current_level_str == 'end':
        logger.warning(f"Chat ended.")
        raise HTTPException(status_code=410, detail="Chat ended.")

    reply = chatbot_client.get_reply(bot_memory, part, schemas.Level(current_level_str))

    if not reply:
        logger.warning(f"Get reply failed.")
        raise HTTPException(status_code=500, detail="Failed to get reply from the chatbot.")

    logger.info(f"Reply successfully.")
    end = get_current_level(bot_memory) == 'end'
    bot_memory_with_end = schemas.BotMemoryWithEnd(bot_memory=bot_memory, end=end)
    return bot_memory_with_end


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

    Returns a summarized message.
    """
    try:
        payload = jwt.decode(token.access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "auth":
            logger.warning("Token validation failed: Invalid token type for authentication.")
            raise HTTPException(status_code=400, detail="Invalid credentials")
        user_id = payload.get("id")
    except JWTError as e:
        logger.error(f"Token decoding failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid credentials")

    summary = chatbot_client.summarize_info(bot_memory, part)
    if not summary:
        logger.warning(f"Get summary failed")
        raise HTTPException(status_code=500, detail="Failed to get summary from the chatbot.")

    #SHOULD BE CHANGED AFTER DISCUSSION WITH MODEL
    article_create = schemas.ArticleCreate(title=summary.title, major=summary.major, field=summary.field,
                                           topic=summary.topic, user_id=user_id)
    article_client.create_article(article_create)
    #SHOULD BE CHANGED AFTER DISCUSSION WITH MODEL

    return {"status": 200, "message": "Article created."}


if __name__ == "__main__":
    uvicorn.run("main:chatbot_app", host="0.0.0.0", port=8004, reload=True)
