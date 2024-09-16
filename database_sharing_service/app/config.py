import os
from dotenv import load_dotenv

current_directory = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_directory, f'../../.env')

load_dotenv(dotenv_path)


class Settings:
    DATABASE_URL = os.getenv('DATABASE_URL',
                             default='postgresql')  #postgresql://postgresadmin@psql-i-xtech:mW%23M%2Ch8ykXNAonOMdDO3Jlbq5GFrqO@psql-i-xtech.postgres.database.azure.com:5432/xsource_db?sslmode=require
    SECRET_KEY = os.getenv('SECRET_KEY', default='default_secret_key')
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 1440
    SMTP_SERVER = os.getenv('SMTP_SERVER', default='smtp.example.com')
    SMTP_PORT = 587
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', default='your_email@example.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', default='your_password')
    MAIL_FROM = os.getenv('MAIL_FROM', default='your_email@example.com')
    EMAIL_SERVICE_URL = os.getenv('EMAIL_SERVICE_URL', default='http://localhost:8003/')
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', default='http://localhost:8002/')
    ARTICLE_SERVICE_URL = os.getenv('ARTICLE_SERVICE_URL', default='http://localhost:8005/')
    CHATBOT_SERVICE_URL = os.getenv('CHATBOT_SERVICE_URL', default='http://localhost:8004/')
    MODEL_CHATBOT_SERVICE_URL = os.getenv('MODEL_CHATBOT_SERVICE_URL', default='http://localhost:8004/')
    FERNET_KEY = os.getenv('FERNET_KEY', default='default_fernet_key')
    AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')
    AZURE_CONTAINER_NAME = os.getenv('AZURE_CONTAINER_NAME')


settings = Settings()
