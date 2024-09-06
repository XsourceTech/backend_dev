import multiprocessing
import sys
import os


def set_pythonpath():
    project_root = os.path.abspath(os.path.dirname(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    os.environ['PYTHONPATH'] = project_root


def start_user_service():
    set_pythonpath()
    os.system("python ./user_service/app/main.py")


def start_auth_service():
    set_pythonpath()
    os.system("python ./auth_service/app/main.py")


def start_email_service():
    set_pythonpath()
    os.system("python ./email_service/app/main.py")


def start_chatbot_article_service():
    set_pythonpath()
    os.system("python ./chatbot_article_service/app/main.py")


def start_article_service():
    set_pythonpath()
    os.system("python ./article_service/app/main.py")


if __name__ == "__main__":
    processes = []

    user_service_process = multiprocessing.Process(target=start_user_service)
    processes.append(user_service_process)

    auth_service_process = multiprocessing.Process(target=start_auth_service)
    processes.append(auth_service_process)

    email_service_process = multiprocessing.Process(target=start_email_service)
    processes.append(email_service_process)

    chatbot_article_service_process = multiprocessing.Process(target=start_chatbot_article_service)
    processes.append(chatbot_article_service_process)

    article_service_process = multiprocessing.Process(target=start_article_service)
    processes.append(article_service_process)

    for process in processes:
        process.start()

    for process in processes:
        process.join()
