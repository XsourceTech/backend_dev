# Overview 
This project consists of multiple microservices including a User Service, Auth Service, and Email Service. Each service is isolated with its own application code, tests, and dependencies. Shared components such as logging and database configurations are placed in a shared directory.

## Directory Descriptions

- **`auth_service/`**: Contains the Auth Service responsible for user authentication and authorization.
  - **`app/`**: The application code for the Auth Service.
  - **`tests/`**: Unit and integration tests for the Auth Service.
  - **`Dockerfile`**: Docker configuration for containerizing the Auth Service.
  - **`requirements.txt`**: Python dependencies for the Auth Service.

- **`email_service/`**: Contains the Email Service responsible for sending emails.
  - **`app/`**: The application code for the Email Service.
  - **`tests/`**: Unit and integration tests for the Email Service.
  - **`Dockerfile`**: Docker configuration for containerizing the Email Service.
  - **`requirements.txt`**: Python dependencies for the Email Service.

- **`user_service/`**: Contains the User Service responsible for managing user accounts.
  - **`app/`**: The application code for the User Service.
  - **`tests/`**: Unit and integration tests for the User Service.
  - **`Dockerfile`**: Docker configuration for containerizing the User Service.
  - **`requirements.txt`**: Python dependencies for the User Service.

- **`database_sharing_service/`**: Contains shared components used by multiple services.
  - **`logging_config.py`**: Centralized logging configuration for all services.
  - **`database.py`**: Database connection and configuration code.
  - **`config.py`**: Centralized configuration handling.
  - **`schemas.py`**: Shared Pydantic models for validation and data management.

- **`.gitignore`**: Specifies files and directories to be ignored by Git.
- **`.env`**: Environment variables used across all services.
- **`docker-compose.yml`**: Docker Compose configuration to manage and run all services together.
- **`README.md`**: Project documentation.
