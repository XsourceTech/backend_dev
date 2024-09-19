# Use an official Python 3.12 runtime as a parent image
FROM python:3.12-slim AS integration

# Copy the environment file into the container based on the provided environment argument
ARG ENVIRONMENT
COPY ./.env.${ENVIRONMENT} /app/.env

# Set the working directory in the container
WORKDIR /app

RUN apt-get update && apt-get install -y supervisor

# Copy the shared_requirements.txt from the project root
COPY ./shared_requirements.txt /app/
# Copy the super start file from the project root
COPY ./super_start.py /app/


# Copy only the necessary application code directories into the container
COPY ./user_service/app /app/user_service/app
COPY ./auth_service/app /app/auth_service/app
COPY ./email_service/app /app/email_service/app
COPY ./chatbot_service/app /app/chatbot_service/app
COPY ./article_service/app /app/article_service/app

COPY ./database_sharing_service/app /app/database_sharing_service/app

# Copy the clients files from each service
COPY ./user_service/clients /app/user_service/clients
COPY ./chatbot_service/clients /app/chatbot_service/clients
COPY ./article_service/clients /app/article_service/clients

# Copy the requirements.txt files from each service
COPY ./user_service/requirements.txt /app/user_service/
COPY ./auth_service/requirements.txt /app/auth_service/
COPY ./email_service/requirements.txt /app/email_service/
COPY ./article_service/requirements.txt /app/article_service/
COPY ./chatbot_service/requirements.txt /app/chatbot_service/

COPY ./database_sharing_service/requirements.txt /app/database_sharing_service/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r /app/user_service/requirements.txt
RUN pip install -r /app/email_service/requirements.txt
RUN pip install -r /app/auth_service/requirements.txt
RUN pip install -r /app/shared_requirements.txt

# Nginx 阶段使用 integration 阶段的构建输出
FROM nginx:latest AS final

# 复制Nginx配置文件
COPY ./nginx.conf /etc/nginx/nginx.conf
# 复制 supervisord 配置
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 复制Python应用服务构建输出
COPY --from=integration /app /app

# Expose ports needed for the services
EXPOSE 80 443

# 启动Nginx和应用
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]