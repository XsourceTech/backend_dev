from fastapi import FastAPI, BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

from database_sharing_service.app import schemas
from database_sharing_service.app.config import settings
from database_sharing_service.app.logging_config import logger

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

# Configuring the email connection using FastAPI-Mail
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

@email_app.post("/send-activation-email", tags=["Emails"], summary="Send Activation Email",
          description="Send an account activation email with a token.")
async def send_activation_email(email: EmailStr, token: str, background_tasks: BackgroundTasks):
    """
    Send an account activation email to the specified email address.

    - **email**: The recipient's email address.
    - **token**: The activation token to include in the email.

    Returns a success message if the email is sent.
    """
    logger.info(f"Sending activation email to: {email}")
    # todo: update the activation link when we decided on which URL to use
    activation_link = f"http://example.com/activate?token={token}"
    message = MessageSchema(
        subject="Activate Your Account",
        recipients=[email],
        body=f"Please activate your account by clicking <a href='{activation_link}'>here</a>.",
        subtype="html"
    )
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)
    logger.info(f"Activation email queued for sending to: {email}")
    return {"message": "Activation email sent"}


@email_app.post("/send-password-reset-email", response_model=schemas.Message, tags=["Emails"], summary="Send Password Reset Email",
          description="Send a password reset email with a token.")
async def send_password_reset_email(email: str, token: str, background_tasks: BackgroundTasks):
    """
    Send a password reset email to the specified email address.

    - **email**: The recipient's email address.
    - **token**: The reset token to include in the email.

    Returns a success message if the email is sent.
    """
    logger.info(f"Sending password reset email to: {email}")
    reset_link = f"http://example.com/reset?token={token}"
    message = MessageSchema(
        subject="Reset Your Password",
        recipients=[email],
        body=f"Please reset your password by clicking <a href='{reset_link}'>here</a>.",
        subtype="html"
    )
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)
    logger.info(f"Password reset email queued for sending to: {email}")
    return {"message": "Password reset email sent"}