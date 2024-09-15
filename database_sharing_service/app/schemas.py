from pydantic import BaseModel, EmailStr
from typing import List
from enum import Enum


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


class BotMemoryWithEndFlag(BaseModel):
    bot_memory: BotMemory
    is_end: bool


# Schema for Token
class Token(BaseModel):
    access_token: str
    token_type: str


# Schema for ArticleCreate
class ArticleCreate(BaseModel):
    user_id: str
    title: str
    major: str | None = None
    field: str | None = None
    topic: str | None = None


# Schema for ArticleInfo
class ArticleInfo(BaseModel):
    id: str
    title: str
    major: str | None = None
    field: str | None = None
    topic: str | None = None


# Schema for Articles
class Articles(BaseModel):
    article_infos: List[ArticleInfo]


class Level(str, Enum):
    MAJOR = 'major'
    FIELD = 'field'
    TOPIC = 'topic'
    TITLE = 'title'


class Part(str, Enum):
    ARTICLE = 'article'
    ABSTRACT = 'abstract'
    INTRODUCTION = 'introduction'
    LITERATURE_REVIEW = 'literature_review'
    METHODOLOGY = 'methodology'
    RESULTS = 'results'
    CONCLUSION = 'conclusion'
    REFERENCES = 'references'


class FileMetadataResponse(BaseModel):
    id: int
    filename: str
    content_type: str
    blob_url: str

    class Config:
        from_attributes = True
