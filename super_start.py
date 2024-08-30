import multiprocessing
import os


def start_user_service():
    os.system("python user_service/app/main.py")


def start_auth_service():
    os.system("python auth_service/app/main.py")


def start_email_service():
    os.system("python email_service/app/main.py")


if __name__ == "__main__":
    processes = []

    auth_service_process = multiprocessing.Process(target=start_auth_service)
    processes.append(auth_service_process)

    email_service_process = multiprocessing.Process(target=start_email_service)
    processes.append(email_service_process)

    user_service_process = multiprocessing.Process(target=start_user_service)
    processes.append(user_service_process)

    for process in processes:
        process.start()

    for process in processes:
        process.join()
