from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
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
    registration_time = Column(DateTime, default=datetime.datetime.utcnow)

    articles = relationship('Article', back_populates='author')


class Article(Base):
    __tablename__ = 'articles'

    article_id = Column(Integer, primary_key=True, index=True)
    article_title = Column(String, nullable=False)
    article_major = Column(String, nullable=True)
    article_topic = Column(String, nullable=True)
    article_field = Column(String, nullable=True)
    article_update_time = Column(DateTime, default=datetime.datetime.utcnow)

    id = Column(Integer, ForeignKey('users.id'))

    author = relationship('User', back_populates='articles')

class FileMetadata(Base):
    __tablename__ = "file_metadata"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    content_type = Column(String)
    blob_url = Column(String)