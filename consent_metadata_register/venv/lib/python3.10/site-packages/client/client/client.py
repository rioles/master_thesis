"""Client program"""
from Crypto.PublicKey import RSA
from PyQt5.QtWidgets import QApplication, QMessageBox
import logging
import logs.config_client_log
from soc_settings.config import *
from soc_settings.errors import ServerError
from soc_settings.decorator import log
import sys
import argparse
import os
from client.client_dbase import ClientDBase
from client.transport import ClientTransport
from client.main_window import ClientMainWindow
from client.start_dialog import UserNameDialog




# Инициализируем клиентский логер
logger = logging.getLogger('client')


@log
def arg_parser():
    """
    Создаём парсер аргументов коммандной строки,
    возвращает 3 параметра после чтения
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    parser.add_argument('-p', '--password', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name
    client_passwd = namespace.password

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        logger.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}'
            f'Допустимые адреса с 1024 до 65535. Работа клиента завершается')
        exit(1)

    return server_address, server_port, client_name, client_passwd


# Основная функция клиента
if __name__ == '__main__':
    # Загружаем параметры коммандной строки
    server_address, server_port, client_name, client_passwd = arg_parser()

    # Создаем клиентское приложение
    client_app = QApplication(sys.argv)

    # Если имя пользователя не было указано в коммандной строке, то запросим его
    start_dialog = UserNameDialog()
    if not client_name or not client_passwd:
        client_app.exec_()
        # Если пользователь ввел имя и нажал ОК, то сохраняем введенное и удаляем объект, иначе выходим
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            client_passwd = start_dialog.client_passwd.text()
        else:
            exit(0)

    # Записываем логи
    logger.info(
        f'Запущен клиент с параметрами: адрес сервера: {server_address}, порт: {server_port}, имя пользователя: {client_name}')

    # Загружаем ключи из файла, или же файла нет, то генерируем новую пару
    dir_path = os.path.dirname(os.path.realpath(__file__))
    key_file = os.path.join(dir_path, f'{client_name}.key')
    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())
    keys.publickey().export_key()

    # Создаем объект базы данных
    database = ClientDBase(client_name)

    # создаем объект - транспорт и запускаем транспортный поток
    try:
        transport = ClientTransport(server_port, server_address, database, client_name, client_passwd, keys)
    except ServerError as error:
        message = QMessageBox()
        message.critical(start_dialog, 'Ошибка сервера', error.text)
        exit(1)
    transport.setDaemon(True)
    transport.start()

    # Удалим объект диалога за ненадобностью
    del start_dialog

    # Создаем GUI
    main_window = ClientMainWindow(database, transport, keys)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Чат Программа alpha version release - {client_name}')
    client_app.exec_()

    # Раз графическая оболочка закрылась, то закрываем транспорт
    transport.transport_shutdown()
    transport.join()
