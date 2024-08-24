@echo off
pip install -r shared_requiements.txt
pip install -r auth_service\requirements.txt
pip install -r database_sharing_service\requirements.txt
pip install -r email_service\requirements.txt
pip install -r user_service\requirements.txt
pause