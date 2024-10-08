# Use an official Python 3.12 runtime as a parent image
FROM python:3.12-slim AS integration

# Copy the environment file into the container based on the provided environment argument
ARG ENVIRONMENT
COPY ./.env.${ENVIRONMENT} /app/.env

# Set the working directory in the container
WORKDIR /app



# Copy the shared_requirements.txt from the project root
COPY ./shared_requirements.txt /app/

#
COPY ./super_start.py /app/

# Copy only the necessary application code directories into the container
# Exclude the tests and Dockerfile from being copied
COPY ./user_service/app /app/user_service/app
COPY ./auth_service/app /app/auth_service/app
COPY ./email_service/app /app/email_service/app
COPY ./database_sharing_service/app /app/database_sharing_service/app

#
COPY ./user_service/clients /app/user_service/clients

# Copy the requirements.txt files from each service
COPY ./user_service/requirements.txt /app/user_service/
COPY ./auth_service/requirements.txt /app/auth_service/
COPY ./email_service/requirements.txt /app/email_service/
COPY ./database_sharing_service/requirements.txt /app/database_sharing_service/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r /app/user_service/requirements.txt
RUN pip install -r /app/email_service/requirements.txt
RUN pip install -r /app/auth_service/requirements.txt
RUN pip install -r /app/shared_requirements.txt

# Expose ports needed for the services
EXPOSE 8001 8002 8003

# Run the application
CMD ["python","./super_start.py"]