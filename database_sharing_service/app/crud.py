from datetime import timedelta, datetime

from jose import jwt
from sqlalchemy.orm import Session

from . import models
from .config import settings
from .models import User
from passlib.context import CryptContext
from cryptography.fernet import Fernet

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

cipher_suite = Fernet(settings.FERNET_KEY)


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user_create):
    #uuid
    hashed_password = pwd_context.hash(user_create.password)
    db_user = User(email=user_create.email, user_name=user_create.user_name, hashed_password=hashed_password,
                   source=user_create.source, user_identity=user_create.user_identity)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


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


def encrypt_user_id(user_id: int) -> str:
    encrypted_identity = cipher_suite.encrypt(str(user_id).encode('utf-8'))
    return encrypted_identity.decode('utf-8')


def decrypt_user_id(encrypted_id: str) -> str:
    decrypted_identity = cipher_suite.decrypt(encrypted_id.encode('utf-8'))
    return decrypted_identity.decode('utf-8')
