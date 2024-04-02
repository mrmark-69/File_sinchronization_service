from cloud_storage_class import CloudStorage
from config import access_token, watched_directory, interval
from repeat_function import repeat_function_with_delay
from tracking_function import cloud_storage_tracking

if __name__ == '__main__':
    access_token = access_token  # токен доступа к Яндекс Диску. Устанавливается в .env
    folder_path = watched_directory  # Путь к отслеживаемой папке на локальном диске. Устанавливается в .env
    interval = int(interval)  # Время задержки перед повторением кода. Устанавливается в .env

    cloud_storage = CloudStorage(access_token, folder_path)  # Создаю экземпляр класса CloudStorage.
    cloud_storage.make_directory(folder_path)  # Создаю папку в удаленном хранилище для сохранения в ней файлов.
    # Если папка уже существует, то нижеследующий код все-равно отработает.

    repeat_function_with_delay(function=cloud_storage_tracking,
                               interval=interval,
                               folder_path=folder_path,
                               cloud_storage=cloud_storage)
