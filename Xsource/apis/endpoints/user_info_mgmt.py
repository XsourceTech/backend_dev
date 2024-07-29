from fastapi import APIRouter, Form
from .utils import *

from models import *

# Create a router object for user information management
user_info_mgmt = APIRouter()


@user_info_mgmt.get("/userinfo/{id}", summary="userinfo(用户信息)")
async def get_user_info(id: str):
    try:
        # Retrieve user information based on the provided user ID
        user = await UserInfo.get(user_info_id=id)
    except Exception:
        return {"status": "404", "msg": "User not found"}

    # Mask the user password before sending the response
    user_dict = mask_user_password(user)
    return {"status": "200", "msg": "OK", "data": user_dict}


# Endpoint to get information of all users
@user_info_mgmt.get("/userinfo", summary="userinfo(所有用户信息)")
async def get_user_infos():
    # Retrieve information of all users
    users = await UserInfo.all()

    # Mask the passwords of all users before sending the response
    users_dict = mask_users_password(users)
    return {"status": "200", "msg": "OK", "data": users_dict}


# Endpoint to modify user information
@user_info_mgmt.post("/userinfo", summary="userinfo(修改用户信息)")
async def modify_user_info(signed_email: str, user_info_name: str = Form(), user_info_gender: str = Form(),
                           user_info_status: str = Form(),
                           user_info_goal: str = Form(), user_info_registration_source: str = Form()):
    # Deserialize the signed email
    deserialized, user_info_email = deserialization(signed_email)
    if not deserialized:
        return {"status": "410", "msg": "Link expired or not exists"}

    # Check if the user account is already activated
    if await user_activated(user_info_email):
        return {"status": "409", "msg": "User already activated"}
    try:
        # Save the modified user information
        user = await save_user_info(user_info_email, user_info_name, user_info_gender, user_info_status, user_info_goal,
                                    user_info_registration_source)

        # Activate the user account after saving the information
        await active_user(user)
    except Exception:
        return {"status": "404", "msg": "User not found"}

    # Mask the user password before sending the response
    user_dict = mask_user_password(user)
    return {"status": "200", "msg": "OK", "data": user_dict}
