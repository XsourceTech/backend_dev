from datetime import timedelta, datetime

from jose import jwt
from sqlalchemy.orm import Session

from . import models
from .config import settings
from .models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user_create):
    hashed_password = pwd_context.hash(user_create.password)
    db_user = User(email=user_create.email, full_name=user_create.full_name, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def generate_auth_token(email: str, expiration: int) -> str:
    access_token_expires = timedelta(minutes=expiration)
    expire = datetime.utcnow() + access_token_expires
    to_encode = {"email": email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
