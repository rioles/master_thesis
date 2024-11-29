"""Декоратор, логирование"""

import sys

sys.path.append('../')
import logs.config_server_log
import logs.config_client_log
import logging
import socket

# метод определения модуля, источника запуска.
# Метод find () возвращает индекс первого вхождения искомой подстроки,
# если он найден в данной строке.
# Если его не найдено, - возвращает -1.
if sys.argv[0].find('client') == -1:
    # сервер
    logger = logging.getLogger('server')
else:
    # иначе клиент
    logger = logging.getLogger('client')


# Функция логирования вызовов других функций
def log(func_to_log):
    """Функция-декоратор"""
    def log_keeper(*args, **kwargs):
        logger.debug(f'Была вызвана функция {func_to_log.__name__} c параметрами {args}, {kwargs}. '
            f'Вызов из модуля {func_to_log.__module__}.')
        ret = func_to_log(*args, **kwargs)
        return ret
    return log_keeper


# Функция проверки, что клиент авторизован на сервере
# Проверяет, что передаваемый объект сокета находится в списке клиентов.
def login_required(func):
    def checker(*args, **kwargs):
        # если первый аргумент - экземпляр MessageProcessor
        # А сокет в остальных аргументах
        # Импорт нужен тут, инаече ошибка рекурсивного импорта
        from server.core import MessageProcessor
        from soc_settings.config import ACTION, PRESENCE
        if isinstance(args[0], MessageProcessor):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    # Проверяем, что сокет есть в списке names класса MessageProcessor
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True

            # Теперь надо проверить, что передаваемые аргументы не presence - сообщение
            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            # Если не авторизован и не сообщение начала авторизации, то вызываем исключение
            if not found:
                raise TypeError

        return func(*args, **kwargs)

    return checker
