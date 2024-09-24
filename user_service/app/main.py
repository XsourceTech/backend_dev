from fastapi import FastAPI, HTTPException, Depends, Query, responses, Path, Form
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database_sharing_service.app import schemas
from database_sharing_service.app.config import settings
from database_sharing_service.app.crud import *
from database_sharing_service.app.database import get_db
from database_sharing_service.app.logging_config import get_logger
from user_service.clients.auth_client import AuthClient
from user_service.clients.email_client import EmailClient

import uvicorn

user_app = FastAPI(
    title="User Service API",
    description="API for managing users, including registration, login, and profile management.",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Users",
            "description": "Operations related to users, such as registration, login, and profile management.",
        },
        {
            "name": "Authentication",
            "description": "Operations related to user authentication, such as token generation and validation.",
        },
    ],
)

logger = get_logger("User_Service")

auth_client = AuthClient()
email_client = EmailClient()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@user_app.post("/signup", response_model=schemas.Message, tags=["Users"], summary="User Registration",
               description="Register a new user with an email, user name, password, source, and user_identity.")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user in the system.

    - **email**: The email address of the user.
    - **user_name**: The user_name of the account.
    - **password**: The password for the user account.
    - **source**: (Optional)The source for the user account.
    - **user_identity**: (Optional) The user_identity for the user account.

    Returns the newly created user object.
    """
    logger.info(f"Attempting to sign up user: {user.email}")
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        logger.warning(f"Signup failed: Email already registered: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    token = generate_active_token(user.email, 10)
    if not token:
        raise HTTPException(status_code=500, detail="Failed to generate activation token")
    try:
        email_client.send_activation_email(user.email, token)
    except Exception as e:
        logger.info(f"Fail to send email for user: {user.email}")
        raise HTTPException(status_code=400, detail="Invalid email")
    logger.info(f"Activation email sent to: {user.email}")
    new_user = create_user(db, user)
    logger.info(f"User created: {new_user.email}")
    return {"status": "200", "message": "User created"}


@user_app.post("/login", response_model=schemas.TokenResponse, tags=["Authentication"], summary="User Login",
               description="Authenticate a user and return a JWT token.")
def login(user: schemas.TokenRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT token.

    - **email**: The email address of the user.
    - **password**: The password for the user account.

    Returns a JWT token if the credentials are valid.
    """
    logger.info(f"User attempting to log in: {user.email}")
    try:
        token = auth_client.authenticate_user(user.email, user.password)

        if not token:
            logger.warning(f"Login failed for user: {user.email}")
            raise HTTPException(status_code=400, detail="Invalid credentials")

    except HTTPException as http_exc:
        logger.warning(f"HTTP exception raised during authentication for user: {user.email} - {http_exc.detail}")
        raise http_exc

    except Exception as exc:
        logger.error(f"Unexpected error during login for user: {user.email} - {str(exc)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during authentication")

    logger.info(f"User logged in successfully: {user.email}")
    return {"access_token": token, "token_type": "bearer"}


@user_app.post("/password-reset-request", tags=["Users"], summary="Request Password Reset",
               description="Request a password reset link by providing the user's email address.")
def request_password_reset(email: str = Form(...), db: Session = Depends(get_db)):
    """
    Request a password reset link.

    - **email**: The email address of the user who needs to reset their password.

    Sends a password reset link to the provided email if the user exists.
    """
    logger.info(f"Attempting to reset password for user: {email}")
    user = get_user_by_email(db, email)
    if user is None:
        logger.warning(f"Reset password failed: Email does not exist: {email}")
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = generate_reset_token(email, 10)
    if not reset_token:
        logger.warning(f"Reset failed for user: {user.email}")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    try:
        email_client.send_password_reset_email(user.email, reset_token)
    except Exception as e:
        logger.info(f"Fail to send email for user: {user.email}")
        raise HTTPException(status_code=400, detail="Invalid email")
    logger.info(f"Activation email sent to: {user.email}")

    return {"status": "200", "message": "Email sent"}


@user_app.get("/activate", tags=["Users"], summary="Activate User Account",
              description="Activate a user account using the token sent to the user's email.")
def activate_user(token: str = Query(...), db: Session = Depends(get_db)):
    logger.info(f"User account activating for token: {token}")
    """
    Activate a user account using the token sent to the user's email.

    - **token**: The activation token sent to the user's email.

    Returns a redirect to a success page if the account is activated.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "active":
            logger.warning("Token validation failed: Invalid token type for user activation.")
            raise HTTPException(status_code=400, detail="Invalid token")
        email: str = payload.get("email")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")

        user = get_user_by_email(db, email=email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_active:
            return {"status": "409", "message": "User already verified"}   # Redirect if user is already verified

        user.is_active = True
        db.commit()

        logger.info(f"User account activated: {email}")
        return {"status": "200", "message": "Activation success"}  # Redirect to a success page

    except JWTError as e:
        logger.error(f"Token decoding failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid credentials")


@user_app.post("/password-reset", tags=["Users"], summary="Reset User Password",
               description="Reset the user's password using a valid reset token.")
def reset_password(token: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    """
    Reset the user's password using the reset token.

    - **token**: The reset token received by the user.
    - **new_password**: The new password that the user wants to set.

    Updates the user's password if the token is valid.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "reset":
            logger.warning("Token validation failed: Invalid token type for password reset.")
            raise HTTPException(status_code=400, detail="Invalid token")
        email: str = payload.get("email")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        user = get_user_by_email(db, email=email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user.hashed_password = pwd_context.hash(new_password)
        db.commit()

        logger.info(f"User password reset: {email}")
        return {"status": "200", "message": "Reset success"}  # Redirect to a success page

    except JWTError as e:
        logger.error(f"Token decoding failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid credentials")


@user_app.get("/users/{token}", response_model=schemas.User, tags=["Users"], summary="Get User by Token",
              description="Retrieve user details by their authentication token.")
async def query_user_by_token(token: str = Path(..., description="The authentication token of the user to retrieve"),
                              db: Session = Depends(get_db)):
    """
    Retrieve user details by their authentication token.

    - **token**: The authentication token of the user.

    Returns the user's profile information if the token is valid.
    """
    token_data = auth_client.validate_token(token)
    if not token_data:
        logger.warning("Token validation failed.")
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = token_data.get('id')
    if not user_id:
        logger.warning("No user ID found in token data.")
        raise HTTPException(status_code=400, detail="Invalid token")
    user = get_user_by_id(db, user_id=user_id)
    if user is None:
        logger.warning(f"User with ID {user_id} not found.")
        raise HTTPException(status_code=404, detail="User not found")
    return user


if __name__ == "__main__":
    uvicorn.run("main:user_app", host="0.0.0.0", port=8001, reload=True)
