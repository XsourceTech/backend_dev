# Use an official Python 3.12 runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the shared_service directory into the container
COPY ../shared_service /app/shared_service

# Copy the shared_requirements.txt from the project root
COPY ../shared_requirements.txt /app/

# Install shared dependencies
RUN pip install --upgrade pip
RUN pip install -r /app/shared_requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Install service-specific dependencies
RUN pip install -r requirements.txt

# Make port 8002 available to the world outside this container
EXPOSE 8002

# Run the application
CMD ["uvicorn", "auth_service.app.main:app", "--host", "0.0.0.0", "--port", "8002"]