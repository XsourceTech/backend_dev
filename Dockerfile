# Use an official Python 3.12 runtime as a parent image
FROM python:3.12-slim AS integration

# Copy the entire application code into the container
ARG ENVIRONMENT
COPY .env.${ENVIRONMENT} .env

# Set the working directory in the container
WORKDIR /app

# Copy the shared_requirements.txt from the project root
COPY ./shared_requirements.txt /app/
COPY ./user_service/requirements.txt /app/
COPY ./email_service/requirements.txt /app/

# Copy the shared_service directory into the container
COPY ./database_sharing_service /app/database_sharing_service

# Install shared dependencies
RUN pip install --upgrade pip
RUN pip install -r /app/shared_requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Install service-specific dependencies
RUN pip install -r /app/requirements.txt

# Make port 8002 available to the world outside this container
EXPOSE 8002

# Run the application
CMD ["uvicorn", "user_service.app.main:user_app", "--host", "0.0.0.0", "--port", "8001"]