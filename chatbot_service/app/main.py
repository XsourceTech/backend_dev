from fastapi import FastAPI, HTTPException, Depends, Query
from chatbot_service.client.article_client import ArticleClient
from database_sharing_service.app.crud import *
from database_sharing_service.app.database import get_db
from database_sharing_service.app.logging_config import get_logger
from chatbot_service.app.utils import *
from chatbot_service.client.model_chatbot_client import ModelChatbotClient
from sqlalchemy.orm import Session
from jose import jwt, JWTError
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

logger = get_logger("Chatbot_Service")

chatbot_client = ModelChatbotClient()
article_client = ArticleClient()


@chatbot_app.post("/get-response",
                  response_model=schemas.BotMemoryWithEndFlag,
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
    try:
        payload = jwt.decode(token.access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "auth":
            logger.warning("Token validation failed: Invalid token type for authentication.")
            raise HTTPException(status_code=400, detail="Invalid credentials")
    except JWTError as e:
        logger.error(f"Token decoding failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid credentials")

    current_level_str = get_current_level(bot_memory, part)
    if current_level_str is None:
        logger.warning(f"User input empty.")
        raise HTTPException(status_code=500, detail="Input empty or role incorrect.")

    if current_level_str == 'end':
        logger.warning(f"Chat ended.")
        raise HTTPException(status_code=410, detail="Chat ended.")

    reply = chatbot_client.get_reply(bot_memory, schemas.Part(part), schemas.Level(current_level_str))

    if reply is None:
        logger.warning(f"Get reply failed.")
        raise HTTPException(status_code=500, detail="Failed to get reply from the chatbot.")

    logger.info(f"Reply successfully.")
    end = get_current_level(bot_memory, part) == 'end'
    bot_memory_reply = BotMemory.parse_obj({"chat_messages": reply.get('bot_memory')})
    bot_memory_with_end_flag = schemas.BotMemoryWithEndFlag(bot_memory=bot_memory_reply, is_end=end)
    return bot_memory_with_end_flag


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
    try:
        payload = jwt.decode(token.access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "auth":
            logger.warning("Token validation failed: Invalid token type for authentication.")
            raise HTTPException(status_code=400, detail="Invalid credentials")
        user_id = payload.get("id")
    except JWTError as e:
        logger.error(f"Token decoding failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid credentials")

    summary = chatbot_client.summarize_info(bot_memory, schemas.Part(part))
    if summary is None:
        logger.warning(f"Get summary failed for user: {user_id}")
        raise HTTPException(status_code=500, detail="Failed to get summary from the chatbot.")

    if part == "article":
        article_create = schemas.ArticleCreate(title=summary.get("title"), major=summary.get("major"),
                                               field=summary.get("field"),
                                               topic=summary.get("topic"), user_id=str(user_id))
        response = article_client.create_article(article_create)
        if response is None:
            logger.warning(f"Article create failed for user: {user_id}")
            raise HTTPException(status_code=500, detail="Failed to create article.")
        return response
    else:
        # generate article part infomation and save, use article_part service
        pass


if __name__ == "__main__":
    uvicorn.run("main:chatbot_app", host="0.0.0.0", port=8004, reload=True)
