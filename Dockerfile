#CONTAINER INTEGRATION
FROM python:3.9 AS integration

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies 
#TOBE MODIFIED
COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "main.py"]

EXPOSE 8080
