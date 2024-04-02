import os

from typing import Any
from datetime import date
from loguru import logger

logger.add(f'logfile_{date.today()}.log', format="{time}, {level}, {message}",
           level="DEBUG", rotation="10 KB")

logger.info("Starting the program...")


@logger.catch()
def cloud_storage_tracking(folder_path: str, cloud_storage: Any):
    """ Функция производит загрузку файлов в облачное хранилище и
        удаление файлов которых уже нет в локальном хранилище. """
    try:
        for file in os.listdir(folder_path):
            cloud_storage.upload_file(file)

        for file in cloud_storage.get_remote_files():
            if file not in cloud_storage.get_local_files():
                cloud_storage.delete_file(file)

    except Exception as exc:
        logger.error(f"Error {exc}")

    logger.info("Program finished.")
