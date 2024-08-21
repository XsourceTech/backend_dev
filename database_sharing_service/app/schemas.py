from pydantic import BaseModel, EmailStr


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
    id: int
    is_active: bool

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


# Schema for token requests, such as login or token generation
class TokenRequest(BaseModel):
    email: str
    password: str
