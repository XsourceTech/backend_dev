import smtplib
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from itsdangerous import URLSafeTimedSerializer as Serializer
from .utils import *
from models import *
from .secret_key import *
from werkzeug.security import generate_password_hash, check_password_hash


# Function to send an email
def sendmail(receiver_email: str, msg: str):
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = receiver_email
    message["Subject"] = "主题：这是一个测试邮件"

    message.attach(MIMEText(msg, "plain"))
    try:
        smtp_server = "smtp.gmail.com"
        port = 587
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, message.as_string())
        return True
    except Exception:
        return False
    finally:
        server.quit()


# Function to check if an email already exists in the database
async def email_existed(user_info_email: str):
    try:
        await UserInfo.get(user_info_email=user_info_email)
        return True
    except Exception:
        return False


# Function to create a new user account
async def create_user_account(user_info_email: str, user_info_password: str):
    current_utc_time = datetime.now(timezone.utc)
    user_info_id = str(uuid.uuid4())
    hashed_password = generate_password_hash(user_info_password)
    await UserInfo.create(
        user_info_id=user_info_id,
        user_info_email=user_info_email,
        user_info_password=hashed_password,
        user_info_activation=False,
        user_info_registration_date=current_utc_time
    )


# Function to send a verification or reset email
def send_email(user_info_email: str, prefix: str):
    s = Serializer(SECRET_KEY, SALT)
    signed_email = s.dumps({'user_info_email': user_info_email})
    return sendmail(user_info_email, address_website + prefix + signed_email), signed_email


# Function to deserialize a signed email token
def deserialization(signed_email: str):
    serializer = Serializer(SECRET_KEY, SALT)
    try:
        email = serializer.loads(signed_email, max_age=EXPIRATION)
        return True, email['user_info_email']
    except Exception:
        return False, None


# Function to check if a user account is activated
async def user_activated(user_info_email: str):
    user = await UserInfo.get(user_info_email=user_info_email)
    return user.user_info_activation


# Function to activate a user account
async def active_user(user):
    user.user_info_activation = True
    await user.save()


# Function to change the user's password
async def change_user_password(user_info_email: str, user_info_password: str):
    user = await UserInfo.get(user_info_email=user_info_email)
    hashed_password = generate_password_hash(user_info_password)
    user.user_info_password = hashed_password
    await user.save()


# Function to save modified user information
async def save_user_info(user_info_email: str, user_info_name: str, user_info_gender: str, user_info_status: str,
                         user_info_goal: str,
                         user_info_registration_source):
    user = await UserInfo.get(user_info_email=user_info_email)
    user.user_info_name = user_info_name
    user.user_info_gender = user_info_gender
    user.user_info_status = user_info_status
    user.user_info_goal = user_info_goal
    user.user_info_registration_source = user_info_registration_source
    await user.save()
    return user


# Function to mask the user's password before sending the user data
def mask_user_password(user):
    user_dict = user.__dict__.copy()
    user_dict.pop('user_info_password', None)
    return user_dict


# Function to mask the passwords of multiple users before sending the user data
def mask_users_password(users):
    users_list = []
    for user in users:
        users_list.append(mask_user_password(user))
    return users_list
