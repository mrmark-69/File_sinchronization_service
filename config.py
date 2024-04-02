import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

access_token = os.getenv('access_token')
watched_directory = os.getenv('watched_directory')
interval = os.getenv('interval')
