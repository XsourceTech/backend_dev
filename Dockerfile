#CONTAINER INTEGRATION
FROM python:3.9-slim AS integration

# Create and set the working directory in the container
WORKDIR /usr/src/app

#TOBE MODIFIED
COPY auth_service/requirements.txt .

# Install Python dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application into the container
COPY . .

# Make sure the script is executable
RUN chmod +x main.py

# Define the command to run your application
CMD [ "python", "auth_service/main.py" ]

# Expose port 8080 for the application
EXPOSE 8080

