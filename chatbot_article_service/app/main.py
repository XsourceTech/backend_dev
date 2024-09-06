from fastapi import FastAPI, HTTPException, Depends, Query, responses, Path, Form
from database_sharing_service.app import schemas
from database_sharing_service.app.config import settings
from database_sharing_service.app.crud import *
from database_sharing_service.app.database import get_db
from database_sharing_service.app.logging_config import get_logger
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import uvicorn

chatbot_article_app = FastAPI(
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

logger = get_logger("Chatbot_Article_Service")


@chatbot_article_app.get("/get-response",
                         response_model=schemas.BotMemoryWithEnd,
                         tags=["Chatbot Responses"],
                         summary="Generate next bot message",
                         description="Generate the next bot message based on memory, token, and other parameters.")
def get_response(bot_memory: schemas.BotMemory, token: schemas.Token,
                 db: Session = Depends(get_db)):
    """
    Generate the next bot message.

    - **bot_memory**: The memory of the bot (conversation history).
    - **token**: The session token (authentication information).
    - **end**: A flag indicating whether it's the end of the conversation.

    Returns the updated bot memory with the next message.
    """
    pass


@chatbot_article_app.post("/summarize",
                          response_model=schemas.Message,
                          tags=["Chatbot Responses"],
                          summary="Summarize the conversation",
                          description="Summarize the bot conversation and optionally create new data.")
def summarize(bot_memory: schemas.BotMemory, token: schemas.Token, db: Session = Depends(get_db)):
    """
    Summarize the bot conversation.

    - **bot_memory**: The memory of the bot (conversation history).
    - **token**: The session token (authentication information).

    Returns a summarized message.
    """
    pass


if __name__ == "__main__":
    uvicorn.run("main:chatbot_article_app", host="0.0.0.0", port=8004, reload=True)
