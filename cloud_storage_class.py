import hashlib
import os

import requests

errors_dict = {
    '400': 'Incorrect data',
    '401': 'Not authorized',
    '403': 'API not available. Your files are taking up more space than you have available. '
           'Delete unnecessary things or increase Disk capacity.',
    '404': 'The requested resource could not be found.',
    '406': 'The resource cannot be provided in the requested format.',
    '409': "Resource already exists.",
    '413': 'File download is not available. The file is too large.',
    '423': 'Engineering works. Now you can only view and download files.',
    '429': 'Too many requests.',
    '503': 'Service is temporarily unavailable.',
    '507': 'Not enough free space'
}


class CloudStorage:
    def __init__(self, access_token: str, folder_path: str) -> None:
        self.access_token = access_token
        self.folder_path = folder_path
        self.headers = {"Authorization": f"OAuth {self.access_token}"}
        self.url = "https://cloud-api.yandex.net/v1/disk/resources"

    def __str__(self) -> str:
        params = {"path": f"{os.path.split(self.folder_path)[-1]}"}

        response = requests.get(url=self.url, headers=self.headers, params=params)
        remote_files = []
        if response.status_code == 200:
            for item in response.json()["_embedded"]["items"]:
                remote_files.append(item['name'])
            return f"Files located in cloud storage: \n{', '.join(sorted(remote_files))}"
        else:
            return errors_dict[str(response.status_code)]

    @classmethod
    def calculate_hash(cls, filename: str) -> str:
        with open(filename, 'rb') as file:
            hasher = hashlib.md5()
            for chunk in iter(lambda: file.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def compare_files(self, local_file: str, remote_file: str) -> None:
        """ Код производит сравнение локального файла и файла в облаке по хэшу.
        Хэш локального файла высчитывается функцией calculate_hash, а код облачного файла получаю из ответа на запрос."""
        params = {'path': remote_file}
        response = requests.get(url=self.url,
                                headers=self.headers,
                                params=params)
        local_hash = self.calculate_hash(local_file)
        remote_hash = response.json()["md5"]

        if local_hash == remote_hash:
            print(f"File '{remote_file}' already exists and is identical to local file")
        else:
            print(f"File '{remote_file}' is different from local file.")
            self.reload_file(
                filename=os.path.split(local_file)[-1])  # Если файлы имеют отличия - заменяю файл на диске.

    def make_directory(self, folder_name: str) -> None:
        """Код создает папку в корневой директории Яндекс Диска"""
        params = {"path": folder_name}
        requests.put(url=self.url,
                     headers=self.headers,
                     params=params)

    def upload_file(self, filename: str) -> None:
        """ Код загружает локальный файл в удаленное хранилище.
        Если файл уже существует, то производится его проверка на идентичность и,
        в случае различий, файл заменяется более свежей версией. """
        params = {"path": f"{os.path.join(os.path.split(self.folder_path)[-1], filename)}"}
        response = requests.get(f"{self.url}/upload?&overwrite=false",
                                headers=self.headers,
                                params=params)

        try:
            href = response.json()["href"]
            with open(os.path.join(self.folder_path, filename),
                      "rb") as file_object:  # Получаю содержимое файла для передачи в put-запрос.
                requests.put(href, files={"file": file_object})
                print(f'File "{filename}" added to cloud storage')
        except KeyError:
            self.compare_files(os.path.join(self.folder_path, filename),
                               os.path.join(os.path.split(self.folder_path)[-1],
                                            filename))  # Проверяю файлы на различие и,
            # если локальный файл отличается, то заменяю файл на диске.

    def reload_file(self, filename: str) -> None:
        """ Код перезаписывает файл в облачном хранилище. """
        headers = self.headers
        params = {"path": f"{os.path.join(os.path.split(self.folder_path)[-1], filename)}"}

        response = requests.get(f"{self.url}/upload?&overwrite=true",
                                headers=headers,
                                params=params)
        href = response.json()["href"]
        with open(os.path.join(self.folder_path, filename),
                  "rb") as file_object:  # Получаю содержимое файла для передачи в put-запрос.
            requests.put(href, files={"file": file_object})
            print(f"file '{params['path']}' was reloaded successfully.")

    def delete_file(self, filename: str) -> None:
        """ Код удаляет файл из облачного хранилища """
        params = {"path": f"{os.path.join(os.path.split(self.folder_path)[-1], filename)}"}

        response = requests.delete(self.url,
                                   headers=self.headers,
                                   params=params)

        if response.status_code == 204:
            print(f"File '{filename}' deleted successfully")
        else:
            print(response.status_code)
            print("Error deleting file")

    def get_remote_files(self) -> list[str]:
        """ Получаю список файлов в облачном хранилище. """
        params = {"path": f"{os.path.split(self.folder_path)[-1]}"}

        response = requests.get(self.url,
                                headers=self.headers,
                                params=params)
        remote_files = []
        if response.status_code == 200:
            for item in response.json()["_embedded"]["items"]:
                remote_files.append(item['name'])
            return sorted(remote_files)
        else:
            print(errors_dict[str(response.status_code)])

    def get_local_files(self) -> list[str]:
        """ Получаю список файлов в локальном хранилище """
        local_files = []
        for file in os.listdir(self.folder_path):
            local_files.append(file)
        return sorted(local_files)
