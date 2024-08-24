from sqlalchemy import Column, Integer, String, Boolean
from .database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    user_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    source = Column(String, nullable=True)
    user_identity = Column(String, nullable=True)
