from pydantic import BaseModel, EmailStr
from typing import List


# Base schema for user data, used for sharing common attributes
class UserBase(BaseModel):
    email: EmailStr
    user_name: str


# Schema for creating a new user
class UserCreate(UserBase):
    password: str
    source: str | None = None
    user_identity: str | None = None


# Schema representing the User model with additional attributes
class User(UserBase):
    is_active: bool
    source: str | None = None
    user_identity: str | None = None

    class Config:
        from_attributes = True


# Schema for a message
class Message(BaseModel):
    status: str
    message: str


# Schema for JWT token response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# Schema for the data embedded in the JWT token
class TokenData(BaseModel):
    email: str | None = None
    id: str | None = None


# Schema for token requests, such as login or token generation
class TokenRequest(BaseModel):
    email: str
    password: str


# Schema for ChatMessage
class ChatMessage(BaseModel):
    role: str
    content: str


# Schema for BotMemory
class BotMemory(BaseModel):
    chat_messages: List[ChatMessage]


class BotMemoryWithEnd(BaseModel):
    bot_memory: BotMemory
    end: bool


# Schema for Token
class Token(BaseModel):
    access_token: str
    token_type: str


# Schema for ArticleCreate
class ArticleCreate(BaseModel):
    title: str
    major: str
    filed: str
    topic: str
    user_id: str


# Schema for ArticleInfo
class ArticleInfo(BaseModel):
    title: str
    major: str
    filed: str
    topic: str


# Schema for Articles
class Articles(BaseModel):
    article_infos: List[ArticleInfo]
