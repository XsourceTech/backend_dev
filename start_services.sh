#!/bin/bash

uvicorn user_service.app.main:user_app --host 0.0.0.0 --port 8001 &
uvicorn auth_service.app.main:auth_app --host 0.0.0.0 --port 8002 &
uvicorn email_service.app.main:email_app --host 0.0.0.0 --port 8003 &

wait -n