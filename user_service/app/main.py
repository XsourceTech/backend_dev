
from fastapi import FastAPI, HTTPException, Depends, Query, responses, Path
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from database_sharing_service.app import schemas, crud
from database_sharing_service.app.config import settings
from database_sharing_service.app.database import get_db
from database_sharing_service.app.logging_config import get_logger
from user_service.clients.auth_client import AuthClient

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
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        logger.warning(f"Signup failed: Email already registered: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = crud.create_user(db, user)
    logger.info(f"User created: {new_user.email}")
    token = (user.email, user.password)
    logger.info(f"Activation email sent to: {new_user.email}")
    return new_user

@user_app.post("/login", response_model=schemas.TokenData, tags=["Authentication"], summary="User Login",
          description="Authenticate a user and return a JWT token.")
def login(user: schemas.TokenRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT token.

    - **email**: The email address of the user.
    - **password**: The password for the user account.

    Returns a JWT token if the credentials are valid.
    """
    logger.info(f"User attempting to log in: {user.email}")
    token = AuthClient.authenticate_user(user.email, user.password)
    if not token:
        logger.warning(f"Login failed for user: {user.email}")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    logger.info(f"User logged in successfully: {user.email}")
    return {"access_token": token, "token_type": "bearer"}


@user_app.get("/activate", tags=["Users"], summary="Activate User Account",
         description="Activate a user account using the token sent to the user's email.")
async def activate_user(token: str = Query(...), db: AsyncSession = Depends(get_db)):
    """
    Activate a user account using the token sent to the user's email.

    - **token**: The activation token sent to the user's email.

    Returns a redirect to a success page if the account is activated.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")

        user = await crud.get_user_by_email(db, email=email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_verified:
            return responses.RedirectResponse(url="/already-verified")  # Redirect if user is already verified

        user.is_verified = True
        await db.commit()

        logger.info(f"User account activated: {email}")
        return RedirectResponse(url="/activation-success")  # Redirect to a success page

    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")


@user_app.get("/user/{user_id}", response_model=schemas.User, tags=["Users"], summary="Get User by ID",
         description="Retrieve user details by their unique user ID.")
async def get_user_by_id(user_id: int = Path(..., description="The ID of the user to retrieve"),
                         db: Session = Depends(get_db)):
    """
    Retrieve user details by their unique user ID.

    - **user_id**: The unique identifier of the user.

    Returns the user's profile information if the user is found.
    """
    logger.info(f"Fetching user with ID: {user_id}")
    user = crud.get_user_by_id(db, user_id=user_id)
    if user is None:
        logger.warning(f"User with ID {user_id} not found.")
        raise HTTPException(status_code=404, detail="User not found")
    return user