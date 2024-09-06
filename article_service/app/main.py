from fastapi import FastAPI, HTTPException, Depends, Query, responses, Path, Form
from database_sharing_service.app import schemas
from database_sharing_service.app.config import settings
from database_sharing_service.app.crud import *
from database_sharing_service.app.database import get_db
from database_sharing_service.app.logging_config import get_logger
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import uvicorn

article_app = FastAPI(
    title="Article Service",
    description="Service for managing articles, including creation, deletion, and retrieval.",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Articles",
            "description": "Operations related to articles such as retrieval, creation, and deletion.",
        },
    ],
)

logger = get_logger("Article_Service")


@article_app.get("/get-article",
                 response_model=schemas.Articles,
                 tags=["Articles"],
                 summary="Get user's created articles",
                 description="Retrieve the list of articles created by the user.")
def get_article(user_id: str = Query(..., description="The ID of the user whose articles are being requested"),
                db: Session = Depends(get_db)):
    """
    Get a list of articles created by a user.

    - **user_id**: The ID of the user whose articles are being requested.

    Returns a list of articles created by the user.
    """
    pass


@article_app.delete("/delete-article/{article_id}",
                    response_model=schemas.Message,
                    tags=["Articles"],
                    summary="Delete article",
                    description="Delete an article by its ID.")
def delete_article(article_id: str = Path(..., description="The ID of the article to delete"),
                   db: Session = Depends(get_db)):
    """
    Delete an article by its ID.

    - **article_id**: The ID of the article to delete.

    Returns a message confirming the deletion.
    """
    pass


@article_app.post("/create-article",
                  response_model=schemas.Message,
                  tags=["Articles"],
                  summary="Create article",
                  description="Create a new article with the provided information.")
def create_article(article: schemas.ArticleCreate, db: Session = Depends(get_db)):
    """
    Create a new article.

    - **article**: The details of the article to be created (title, major, field, topic, and user_id).

    Returns a message confirming the article creation.
    """
    pass


if __name__ == "__main__":
    uvicorn.run("main:article_app", host="0.0.0.0", port=8005, reload=True)
