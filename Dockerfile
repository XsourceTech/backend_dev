# Use a smaller base image for production
FROM python:3.9-slim AS integration

# Create and set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY auth_service/requirements.txt .

# Install Python dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
COPY auth_service/ ./auth_service/

# Set working directory for running the application
WORKDIR /usr/src/app/auth_service/app

# Make sure the script is executable
RUN chmod +x main.py

# Define the command to run your application
CMD [ "python", "main.py" ]

# Expose port 8080 for the application
EXPOSE 8080
