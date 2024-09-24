import time
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient
from fastapi import FastAPI, HTTPException, Depends, Query, responses, Path, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from article_service.clients.auth_client import AuthClient
from database_sharing_service.app import schemas, __init__
from database_sharing_service.app.config import settings
from database_sharing_service.app.crud import *
from database_sharing_service.app.database import get_db
from database_sharing_service.app.logging_config import get_logger
from sqlalchemy.orm import Session
from typing import List
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
"""
article_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有Header
)
"""

# Initialize Azure Blob Storage clients
blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER_NAME)

auth_client = AuthClient()

logger = get_logger("Article_Service")


@article_app.get("/get-article",
                 response_model=schemas.Articles,
                 tags=["Articles"],
                 summary="Get user's created articles",
                 description="Retrieve the list of articles created by the user.", )
def get_article_api(token: str = Query(..., description="The authentication token of the user"),
                    db: Session = Depends(get_db)):
    """
    Get a list of articles created by a user.

    - **token**: The authentication token of the user.

    Returns a list of articles created by the user.
    """

    start_time = time.time()  # 开始时间
    logger.info(
        f"Request start - get-article-by-user, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    token_data = auth_client.validate_token(token)
    if not token_data:
        logger.warning("Token validation failed.")
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = token_data.get('id')
    if not user_id:
        logger.warning("No user ID found in token data.")
        raise HTTPException(status_code=400, detail="Invalid token data")

    articles = get_article_by_user_id(db, user_id)

    if articles is None:
        raise HTTPException(status_code=404, detail="No articles found for this user")

    article_infos = [schemas.ArticleInfo(
        id=encrypt_id(article.article_id),
        title=article.article_title,
        major=article.article_major,
        field=article.article_field,
        topic=article.article_topic
    ) for article in articles]

    end_time = time.time()  # 结束时间
    duration = end_time - start_time
    logger.info(
        f"Request end - get-article-by-user, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}, Duration: {duration:.2f} seconds")

    return schemas.Articles(article_infos=article_infos)


@article_app.get("/get-article/{article_encid}",
                 response_model=schemas.ArticleInfo,
                 tags=["Articles"],
                 summary="Get article by ID",
                 description="Retrieve an article by its ID.")
def get_article_by_id_api(article_encid: str = Path(..., description="The ID of the article to retrieve"),
                          db: Session = Depends(get_db)):
    """
    Retrieve an article by its ID.

    - **article_id**: The ID of the article to retrieve.

    Returns the details of the article.
    """
    start_time = time.time()  # 开始时间
    logger.info(
        f"Request start - get-article, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    article_decid = decrypt_id(article_encid)
    article = get_article_by_article_id(db, article_decid)

    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    end_time = time.time()  # 结束时间
    duration = end_time - start_time
    logger.info(
        f"Request end - get-article, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}, Duration: {duration:.2f} seconds")

    return schemas.ArticleInfo(
        id=encrypt_id(article.article_id),
        title=article.article_title,
        major=article.article_major,
        field=article.article_field,
        topic=article.article_topic
    )


@article_app.delete("/delete-article/{article_encid}",
                    response_model=schemas.Message,
                    tags=["Articles"],
                    summary="Delete article",
                    description="Delete an article by its ID.")
def delete_article_api(article_encid: str = Path(..., description="The ID of the article to delete"),
                       db: Session = Depends(get_db)):
    """
    Delete an article by its ID.

    - **article_id**: The ID of the article to delete.

    Returns a message confirming the deletion.
    """

    start_time = time.time()  # 开始时间
    logger.info(
        f"Request start - delete-article, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    article_decid = decrypt_id(article_encid)
    delete = delete_article(db, article_decid)
    if not delete:
        raise HTTPException(status_code=404, detail="Article not found")

    end_time = time.time()  # 结束时间
    duration = end_time - start_time
    logger.info(
        f"Request end - delete-article, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}, Duration: {duration:.2f} seconds")

    return {"status": "200", "message": "Article deleted"}


@article_app.post("/create-article",
                  response_model=schemas.Message,
                  tags=["Articles"],
                  summary="Create article",
                  description="Create a new article with the provided information.")
def create_article_api(article: schemas.ArticleCreate, db: Session = Depends(get_db)):
    """
    Create a new article.

    - **article**: The details of the article to be created (title, major, field, topic, and user_id).

    Returns a message confirming the article creation.
    """

    start_time = time.time()  # 开始时间
    logger.info(
        f"Request start - create-article, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        new_article = create_article(db, article)
        logger.info(f"Article created: {new_article.article_title}")

        end_time = time.time()  # 结束时间
        duration = end_time - start_time
        logger.info(
            f"Request end - create-article, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}, Duration: {duration:.2f} seconds")

        return {"status": "200", "message": "Article created"}
    except Exception as e:
        logger.error(f"Error creating article: {str(e)}")
        raise HTTPException(status_code=500, detail="Fail to create article.")


@article_app.post("/upload/")
async def upload_files(article_encid: str = Query(...), files: List[UploadFile] = File(...),
                       db: Session = Depends(get_db)):
    """
    Upload multiple files to Azure Blob Storage and save their metadata to the PostgreSQL database.
    """
    start_time = time.time()  # 开始时间
    logger.info(
        f"Request start - upload_files, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    uploaded_files_metadata = []
    failed_files = []
    article_id = decrypt_id(article_encid)
    for file in files:
        try:
            # Upload each file to Azure Blob Storage
            blob_name = f"{article_id}/{file.filename}"
            blob_client = container_client.get_blob_client(blob_name)
            try:
                blob_client.upload_blob(file.file, overwrite=False)
            except ResourceExistsError:
                failed_files.append({"filename": file.filename, "error": "File already exists in Azure Blob Storage"})
                continue  # Skip this file and continue with the next one

            # Save file metadata to the PostgreSQL database
            blob_url = blob_client.url
            saved_metadata = save_metadata_to_db(db, article_id=article_id, filename=file.filename,
                                                 content_type=file.content_type, blob_url=blob_name)

            uploaded_files_metadata.append(saved_metadata)

        except Exception as e:
            logger.error(f"Error uploading file '{file.filename}': {str(e)}")
            failed_files.append({"filename": file.filename, "error": str(e)})
            continue  # Skip this file and continue with the next one

    if failed_files:

        end_time = time.time()  # 结束时间
        duration = end_time - start_time
        logger.info(
            f"Request end - upload_files, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}, Duration: {duration:.2f} seconds")

        return {"status": "207", "message": "Some files failed to upload", "uploaded_files": uploaded_files_metadata,
                "failed_files": failed_files}

    end_time = time.time()  # 结束时间
    duration = end_time - start_time
    logger.info(
        f"Request end - upload_files, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}, Duration: {duration:.2f} seconds")

    return {"status": "200", "message": "All files uploaded successfully"}


@article_app.delete("/delete-file/")
async def delete_file(filedelete: schemas.FileDelete, db: Session = Depends(get_db)):
    """
    Delete a file from Azure Blob Storage and remove its metadata from the PostgreSQL database.
    """

    start_time = time.time()  # 开始时间
    logger.info(
        f"Request start - delete-file, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    filedelete.article_id = decrypt_id(filedelete.article_id)
    try:
        # Delete the file from Azure Blob Storage
        blob_name = f"{filedelete.article_id}/{filedelete.filename}"
        blob_client = container_client.get_blob_client(blob_name)

        if blob_client.exists():
            blob_client.delete_blob()
        else:
            raise HTTPException(status_code=404, detail=f"File '{filedelete.filename}' not found in Azure Blob Storage.")

        # Delete file metadata from the PostgreSQL database
        metadata_deleted = delete_metadata_from_db(db, filedelete.article_id, filedelete.filename)

        if not metadata_deleted:
            raise HTTPException(status_code=404, detail=f"Metadata for file '{filedelete.filename}' not found in the database.")

        end_time = time.time()  # 结束时间
        duration = end_time - start_time
        logger.info(
            f"Request end - delete-file, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}, Duration: {duration:.2f} seconds")

        return {"message": f"File '{filedelete.filename}' and its metadata successfully deleted."}

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file")


if __name__ == "__main__":
    uvicorn.run("main:article_app", host="0.0.0.0", port=8005, reload=True)
