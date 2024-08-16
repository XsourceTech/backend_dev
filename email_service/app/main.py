from fastapi import FastAPI

from database_sharing_service.app import schemas

email_app = FastAPI(
    title="Email Service API",
    description="API for sending emails such as account activation and password resets.",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Emails",
            "description": "Operations related to sending emails for account activation and password resets.",
        },
    ],
)


@email_app.post("/send-activation-email", response_model=schemas.Message, tags=["Emails"], summary="Send Activation Email",
          description="Send an account activation email with a token.")
async def send_activation_email():
    """
    Send an account activation email to the specified email address.

    - **email**: The recipient's email address.
    - **token**: The activation token to include in the email.

    Returns a success message if the email is sent.
    """
    pass


@email_app.post("/send-password-reset-email", response_model=schemas.Message, tags=["Emails"], summary="Send Password Reset Email",
          description="Send a password reset email with a token.")
async def send_password_reset_email():
    """
    Send a password reset email to the specified email address.

    - **email**: The recipient's email address.
    - **token**: The reset token to include in the email.

    Returns a success message if the email is sent.
    """
    pass
