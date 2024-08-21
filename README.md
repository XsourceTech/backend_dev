The backend uses a microservice design, which each microservice handles their own functionalities and communicated via APIs, database_sharing_service is used as a shared service
for managing database related things. We are using a centralized logging and database system.

Project Structure
backend_dev/
├── auth_service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_main.py
│   ├── Dockerfile
│   ├── requirements.txt
├── email_service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_main.py
│   ├── Dockerfile
│   ├── requirements.txt
├── user_service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_main.py
│   ├── Dockerfile
│   ├── requirements.txt
├── databbase_sharing_service/
│   ├── __init__.py
│   ├── logging_config.py
│   ├── database.py
│   ├── config.py
│   └── schemas.py
├── .gitignore
├── .env
├── docker-compose.yml
└── README.md
