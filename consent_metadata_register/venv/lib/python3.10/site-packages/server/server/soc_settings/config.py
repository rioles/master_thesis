"""Константы (TCP)"""

import logging

# Порт поумолчанию для сетевого ваимодействия
DEFAULT_PORT = 7777
# IP адрес по умолчанию для подключения клиента
DEFAULT_IP_ADDRESS = '127.0.0.1'
# Максимальная очередь подключений
MAX_CONNECTIONS = 5
# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 1024
# Кодировка проекта
ENCODING = 'utf-8'
# Устанавливаем уровень логирования
LOGGING_LEVEL = logging.DEBUG
# База данных для хранения данных сервера:
SERVER_CONFIG = 'server.ini'

# Прококол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'
DATA = 'bin'
PUBLIC_KEY = 'pubkey'

# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
EXIT = 'exit'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'
PUBLIC_KEY_REQUEST = 'pubkey_need'

# Словари - ответы:
# 200
RESPONSE_200 = {RESPONSE: 200}
# 202 Код состояния ответа "The HTTP 202 Accepted" указывает,
# что запрос получен, но еще не обработан.
RESPONSE_202 = {RESPONSE: 202,
                LIST_INFO: None
                }
# 400 Код состояния ответа "HTTP 400 Bad Request" указывает, что сервер не смог понять запрос
# из-за недействительного синтаксиса. Клиент не должен повторять этот запрос без изменений.
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}
# 205 Статус ответа "HTTP 205 Reset Content" сообщает клиенту об изменении вида документа, например, для очистки
# содержимого формы, сброса состояния холста или обновления пользовательского интерфейса.
RESPONSE_205 = {
    RESPONSE: 205
}

# 511 The HTTP 511 Network Authentication Required код состояния ответа указывает,
# что клиент должен пройти аутентификацию, чтобы получить доступ к сети.
RESPONSE_511 = {
    RESPONSE: 511,
    DATA: None
}
