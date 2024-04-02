import time
from typing import Any


def repeat_function_with_delay(function: Any, interval: int, **kwargs: Any) -> None:
    """ Функция повторяет, с заданной периодичностью, вызов другой функции,
    которая передается в нее в качестве одного из аргументов.
    Также функция принимает именованные аргументы для вызываемой функции."""
    while True:
        function(**kwargs)
        time.sleep(interval)
