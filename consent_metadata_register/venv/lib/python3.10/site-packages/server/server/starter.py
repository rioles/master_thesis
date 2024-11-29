"""Starter"""

import subprocess

proc = []

while True:
    action = input('Нажмите: q для выхода s - запустить сервер, k - запустить клиентов '
                   'x - чтобы закрыть все окна: ')
    if action == 'q':
        break
    elif action == 'x':
        while proc:
            proc.pop().kill()
    elif action == 's':
        # запускаем сервер
        proc.append(subprocess.Popen('python server.py',
                                     creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif action == 'k':
        print('Убедитесь, что на сервере зарегистрировано необходимо количество клиентов с паролем 123.')
        print('Первый запуск может быть достаточно долгим из-за генерации ключей!')
        client_count = int(input('Введите количество тестовых клиентов для запуска: '))
        # Запускаем клиентов
        for i in range(client_count):
            proc.append(subprocess.Popen(f'python client.py -n test{i + 1} -p 123', creationflags=subprocess.CREATE_NEW_CONSOLE))



