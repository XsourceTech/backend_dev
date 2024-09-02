import os
from dotenv import load_dotenv

current_directory = os.path.dirname(os.path.abspath(__file__))
environment = os.getenv('ENV', 'local')  # 默认使用 'local' 环境
dotenv_path = os.path.join(current_directory, f'../../.env.{environment}')

load_dotenv(dotenv_path)


class Settings:
    DATABASE_URL = os.getenv('DATABASE_URL', default='postgresql')
    SECRET_KEY = os.getenv('SECRET_KEY', default='default_secret_key')
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    SMTP_SERVER = os.getenv('SMTP_SERVER', default='smtp.example.com')
    SMTP_PORT = 587
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', default='your_email@example.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', default='your_password')
    MAIL_FROM = os.getenv('MAIL_FROM', default='your_email@example.com')
    EMAIL_SERVICE_URL = os.getenv('EMAIL_SERVICE_URL', default='http://localhost:8003/')
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', default='http://localhost:8002/')


settings = Settings()
