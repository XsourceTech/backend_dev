from fastapi import APIRouter
from .utils import *
from models import *
from werkzeug.security import check_password_hash

# Create a router object for user account management
user_account_mgmt = APIRouter()


# Endpoint for user signup
@user_account_mgmt.post("/signup", summary="signup(注册)",
                        description="通过用户发送的邮箱地址和密码进行注册，并且发送验证邮件。")
async def user_signup(user_info_email: str, user_info_password: str):
    if await email_existed(user_info_email):
        return {"status": "409", "msg": "User exists"}

    # Send a verification email to the user's email address
    sent, signed_email = send_email(user_info_email, "verify/")
    if not sent:
        return {"status": "500", "msg": "Internal Server Error"}

    # Create a new user account with the provided email and password
    await create_user_account(user_info_email, user_info_password)
    return {"status": "201", "msg": "Created", "token": signed_email}


"""
    # Endpoint for user email verification (Deprecated)
@user_account_mgmt.get("/verify", summary="verify(邮箱验证)",
                       description="通过用户点击验证邮件中的链接，前端发送请求到后端，后端进行账户激活")
async def user_verify(signed_email: str):
    deserialized, user_info_email = deserialization(signed_email)
    if not deserialized:
        return {"status": "410", "msg": "Link expired or not exists"}
    try:
        if await user_activated(user_info_email):
            return {"status": "409", "msg": "User already activated"}
        await active_user(user_info_email)
        return {"status": "200", "msg": "OK", "email": user_info_email}
    except Exception as e:
        return {"status": "404", "msg": "User not found"}
"""


# Endpoint for user login
@user_account_mgmt.post("/login", summary="login(登录)", description="通过用户发送的邮箱地址和密码进行登录。")
async def user_login(user_info_email: str, user_info_password: str):
    try:
        # Retrieve user information based on the provided email
        user = await UserInfo.get(user_info_email=user_info_email)
    except Exception:
        return {"status": "401", "msg": "Unauthorized"}

    # Check if the provided password matches the stored password hash
    if not check_password_hash(user.user_info_password, user_info_password):
        return {"status": "401", "msg": "Unauthorized"}

    # Check if the user account is activated
    if not user.user_info_activation:
        return {"status": "403", "msg": "User not activated"}

    # Mask the user password before sending the response
    user_dict = mask_user_password(user)
    return {"status": "200", "msg": "OK", "user": user_dict}


# Endpoint for password reset request
@user_account_mgmt.get("/reset", summary="reset(重置账户密码请求)",
                       description="通过用户发送重置密码请求，发送重置密码邮件。")
async def user_reset(user_info_email: str):
    try:
        # Check if the user account is activated
        if not await user_activated(user_info_email):
            return {"status": "403", "message": "User not activated"}
    except Exception:
        return {"status": "404", "msg": "User not found"}

    # Send a password reset email to the user's email address
    sent, signed_email = send_email(user_info_email, "reset/")
    if not sent:
        return {"status": "500", "msg": "Internal Server Error"}
    return {"status": "200", "msg": "OK", "token": f"reset/{signed_email}"}


# Endpoint for resetting the user password
@user_account_mgmt.post("/reset", summary="reset(重置账户密码)",
                        description="通过用户点击重置密码邮件中的链接，转到设置密码界面,前端传回用户已签名的邮箱和新密码，后端进行新密码的设置。")
async def user_reset_password(signed_email: str, user_info_password: str):
    # Deserialize the signed email
    deserialized, user_info_email = deserialization(signed_email)
    if not deserialized:
        return {"status": "410", "msg": "Link expired or not exists"}
    try:
        # Change the user's password in the database
        await change_user_password(user_info_email, user_info_password)
    except Exception:
        return {"status": "404", "msg": "User not found"}
    return {"status": "200", "msg": "OK"}


# Endpoint for resending the verification email
@user_account_mgmt.get("/resend", summary="resend email(重新发送验证邮件)",
                       description="通过用户请求重新验证，重新发送验证邮件。")
async def resend_verify(user_info_email: str):
    # Check if the email exists in the database
    if not await email_existed(user_info_email):
        return {"status": "404", "msg": "User not found"}

    # Check if the user account is already activated
    if await user_activated(user_info_email):
        return {"status": "403", "message": "User already activated"}

    # Resend the verification email to the user's email address
    sent, signed_email = send_email(user_info_email, "verify/")
    if not sent:
        return {"status": "500", "msg": "Internal Server Error"}
    return {"status": "200", "msg": "OK", "token": signed_email}
