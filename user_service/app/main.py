from fastapi import FastAPI

from database_sharing_service.app import schemas

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


@user_app.post("/signup", response_model=schemas.Message, tags=["Users"], summary="User Registration",
          description="Register a new user with an email, user name, password, source, and user_identity.")
def signup():
    """
    Register a new user in the system.

    - **email**: The email address of the user.
    - **user_name**: The user_name of the account.
    - **password**: The password for the user account.
    - **source**: (Optional)The source for the user account.
    - **user_identity**: (Optional) The user_identity for the user account.

    Returns the newly created user object.
    """
    pass


@user_app.post("/login", response_model=schemas.Token, tags=["Authentication"], summary="User Login",
          description="Authenticate a user and return a JWT token.")
def login(request: schemas.TokenRequest):
    """
    Authenticate a user and return a JWT token.

    - **email**: The email address of the user.
    - **password**: The password for the user account.

    Returns a JWT token if the credentials are valid.
    """
    pass

@user_app.get("/activate", response_model=schemas.Token, tags=["Users"], summary="Activate User Account",
         description="Activate a user account using the token sent to the user's email.")
async def activate_user():
    """
    Activate a user account using the token sent to the user's email.

    - **token**: The activation token sent to the user's email.

    Returns a success message if the account is activated.
    """
    pass


@user_app.get("/users/{user_id}", response_model=schemas.User, tags=["Users"], summary="Get user info")
async def get_user():
    pass