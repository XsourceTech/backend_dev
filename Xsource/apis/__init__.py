from fastapi import FastAPI
from apis.endpoints import *
from tortoise import Tortoise
from apis.db_config import init
from fastapi.middleware.cors import CORSMiddleware


async def lifespan(app: FastAPI):
    await init()
    yield
    await Tortoise.close_connections()


app = FastAPI(
    lifespan=lifespan,
    title="Xsource",
    description="Xsource API",
    version="1.0.0",
)

"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""

app.include_router(user_account_mgmt, tags=["User account management api(账号管理接口)"])
app.include_router(user_info_mgmt, tags=["User info management api(用户信息管理接口)"])
