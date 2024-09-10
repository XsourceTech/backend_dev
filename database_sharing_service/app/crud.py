from datetime import timedelta, datetime

from fastapi import HTTPException
from jose import jwt
from sqlalchemy.orm import Session

from . import models
from .config import settings
from .models import User, Article
from .schemas import *
from passlib.context import CryptContext
from cryptography.fernet import Fernet

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

cipher_suite = Fernet(settings.FERNET_KEY)


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_article_by_user_id(db: Session, user_id: int):
    return db.query(Article).filter(Article.id == user_id).all()

def get_article_by_article_id(db: Session, article_id: int):
    return db.query(Article).filter(Article.article_id == article_id).first()


def create_user(db: Session, user_create: UserCreate):
    hashed_password = pwd_context.hash(user_create.password)
    db_user = User(email=user_create.email, user_name=user_create.user_name, hashed_password=hashed_password,
                   source=user_create.source, user_identity=user_create.user_identity)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_article(db: Session, article_create: ArticleCreate):
    db_article = Article(article_title=article_create.title, article_major=article_create.major,
                         article_field=article_create.field, article_topic=article_create.topic,
                         id=article_create.user_id)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def delete_article(db: Session, article_id: int):
    db_article = db.query(Article).filter(Article.article_id == article_id).first()
    if db_article is None:
        return False
    try:
        db.delete(db_article)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def generate_auth_token(user_id: int, email: str, expiration: int) -> str:
    access_token_expires = timedelta(minutes=expiration)
    expire = datetime.utcnow() + access_token_expires
    to_encode = {"id": user_id, "email": email, "type": "auth", "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def generate_reset_token(email: str, expiration: int) -> str:
    access_token_expires = timedelta(minutes=expiration)
    expire = datetime.utcnow() + access_token_expires
    to_encode = {"email": email, "type": "reset", "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def generate_active_token(email: str, expiration: int) -> str:
    access_token_expires = timedelta(minutes=expiration)
    expire = datetime.utcnow() + access_token_expires
    to_encode = {"email": email, "type": "active", "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def encrypt_id(user_id: int) -> str:
    encrypted_identity = cipher_suite.encrypt(str(user_id).encode('utf-8'))
    return encrypted_identity.decode('utf-8')


def decrypt_id(encrypted_id: str) -> str:
    decrypted_identity = cipher_suite.decrypt(encrypted_id.encode('utf-8'))
    return decrypted_identity.decode('utf-8')
