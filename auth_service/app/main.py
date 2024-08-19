import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from datetime import datetime, timedelta
from database_sharing_service.app import schemas, models
from database_sharing_service.app.config import settings
from database_sharing_service.app.crud import verify_password
from database_sharing_service.app.database import get_db
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from logging_config import logger

auth_app = FastAPI(
    title="Auth Service API",
    description="API for managing authentication, including JWT token generation and validation.",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Operations related to user authentication, such as token generation and validation.",
        },
    ],
)


@auth_app.post("/generate-token", response_model=schemas.TokenResponse, tags=["Authentication"],
               summary="Generate JWT Token",
               description="Generate a JWT token for the given email.")
def generate_token(request: schemas.TokenRequest, db: Session = Depends(get_db)):
    """
    Generate a JWT token for the given email.

    - **email**: The email address for which to generate the token.
    - **password**: The password for the given email.

    Returns the generated JWT token.
    """

    # Query the database for a user with the provided email.
    user = db.query(models.User).filter(models.User.email == request.email).first()

    # Verify the user's email address and password.
    if not user:
        logger.warning(f"Failed login attempt with non-existent email: {request.email}")
        raise HTTPException(status_code=400, detail="Invalid email or password")
    if not verify_password(request.password, user.hashed_password):
        logger.warning(f"Failed login attempt for email: {request.email} with incorrect password")
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Generate token.
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + access_token_expires
    to_encode = {"email": request.email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    logger.info(f"Token generated for email: {request.email}")
    return schemas.TokenResponse(access_token=encoded_jwt, token_type="bearer")


@auth_app.post("/validate-token", response_model=schemas.TokenData, tags=["Authentication"],
               summary="Validate JWT Token",
               description="Validate a JWT token and extract the user information.")
def validate_token(token: str):
    """
    Validate a JWT token and extract the user information.

    - **token**: The JWT token to validate.

    Returns the extracted user information if the token is valid.
    """

    # Define an HTTP exception to be raised if the token validation fails
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode the JWT token using the secret key and algorithm
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            logger.warning("Token validation failed: missing email in payload.")
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError as e:
        logger.error(f"Token validation failed: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    logger.info(f"Token validated successfully for email: {email}")
    return token_data


if __name__ == '__main__':
    uvicorn.run("main:auth_app", port=8080, reload=True)
