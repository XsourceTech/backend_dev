import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from aiosmtplib.errors import SMTPRecipientsRefused
from database_sharing_service.app import schemas
from database_sharing_service.app.config import settings
from database_sharing_service.app.logging_config import get_logger

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

logger = get_logger("Email_Service")

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


async def send_email_task(fm: FastMail, message: MessageSchema):
    try:
        await fm.send_message(message)
    except SMTPRecipientsRefused as exc:
        raise HTTPException(status_code=400, detail=f"Failed to send email: {str(exc)}")  # 抛出HTTPException
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unexpected error:" + str(exc))


@email_app.post("/send-activation-email", response_model=schemas.Message, tags=["Emails"],
                summary="Send Activation Email",
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
    activation_link = f"https://frontend-i-xtech.azurewebsites.net/activate/{token}"
    message = MessageSchema(
        subject="Activate Your Account",
        recipients=[email],
        body=f"Please activate your account by clicking <a href='{activation_link}'>here</a>.",
        subtype="html"
    )
    fm = FastMail(conf)

    try:
        await send_email_task(fm, message)
    except SMTPRecipientsRefused as exc:
        logger.error(f"Failed to send activation email to {email}: {exc}")
        raise HTTPException(status_code=400, detail=f"Failed to send email: {str(exc)}")
    except Exception as exc:
        logger.error(f"Unexpected error occurred while sending activation email to {email}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to send activation email")

    logger.info(f"Activation email sent to: {email}")
    return {"status": "200", "message": "Activation email sent"}


@email_app.post("/send-password-reset-email", response_model=schemas.Message, tags=["Emails"],
                summary="Send Password Reset Email",
                description="Send a password reset email with a token.")
async def send_password_reset_email(email: str, token: str, background_tasks: BackgroundTasks):
    """
    Send a password reset email to the specified email address.

    - **email**: The recipient's email address.
    - **token**: The reset token to include in the email.

    Returns a success message if the email is sent.
    """
    logger.info(f"Sending password reset email to: {email}")
    reset_link = f"https://frontend-i-xtech.azurewebsites.net/reset/{token}"
    message = MessageSchema(
        subject="Reset Your Password",
        recipients=[email],
        body=f"Please reset your password by clicking <a href='{reset_link}'>here</a>.",
        subtype="html"
    )
    fm = FastMail(conf)

    try:
        await send_email_task(fm, message)
    except SMTPRecipientsRefused as exc:
        logger.error(f"Failed to send password reset email to {email}: {exc}")
        raise HTTPException(status_code=400, detail=f"Failed to send email: {str(exc)}")
    except Exception as exc:
        logger.error(f"Unexpected error occurred while sending password reset email to {email}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to send password reset email")

    logger.info(f"Password reset email sent to: {email}")
    return {"status": "200", "message": "Password reset email sent"}


if __name__ == "__main__":
    uvicorn.run("main:email_app", host="0.0.0.0", port=8003, reload=True)
