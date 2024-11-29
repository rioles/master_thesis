from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Text
from sqlalchemy.orm import mapper, sessionmaker
from soc_settings.config import *
import datetime


# Серверная база данных
class ServerDBase:
    # Класс - отображение таблицы всех пользователей
    # Экземпляр этого класса = запись в таблице AllUsers
    class AllUsers:
        def __init__(self, username, passwd_hash):
            self.name = username
            self.last_login = datetime.datetime.now()
            self.passwd_hash = passwd_hash
            self.pubkey = None
            self.id = None

    # Класс - отображение таблицы активных пользователей:
    # Экземпляр класса = запись в таблице ActiveUsers
    class ActiveUsers:
        def __init__(self, user_id, ip_address, port, login_time):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.id = None

    # Класс - отображение таблицы истории входов
    # Экземпляр этого класса = запись в таблицу LoginHistory
    class LoginHistory:
        def __init__(self, name, date, ip, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip = ip
            self.port = port
    # Класс отображения таблицы контактов пользователей

    class UsersContacts:
        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact

    # Класс отображения таблицы истории действий
    class UsersHistory:
        def __init__(self, user):
            self.id = None
            self.user = user
            self.sent = 0
            self.accepted = 0

    def __init__(self, path):
        # Создаем движок базы данных
        # SERVER_DATABASE - sqlite://server_base.db3
        # echo=False - отключаем ведение логов(вывод sql запросов)
        # pool_recycle - по умолчанию соедниние с БД через 8 часов простоя обрывается
        # Добавляем опцию pool_recycle = 7200 (переустановка соединения)
        self.database_engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200,
                                             connect_args={'check_same_thread': False})

        # создаем объект MetaData
        self.metadata = MetaData()

        # Создаем таблицу пользователей
        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String, unique=True),
                            Column('last_login', DateTime),
                            Column('passwd_hash', String),
                            Column('pubkey', Text)
                            )

        # Создаем таблицу активных пользователей
        active_users_table = Table('Active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('Users.id'), unique=True),
                                   Column('ip_address', String),
                                   Column('port', Integer),
                                   Column('login_time', DateTime)
                                   )

        # Создаем таблицу историй входов
        user_login_history = Table('Login_history', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('name', ForeignKey('Users.id')),
                                   Column('date_time', DateTime),
                                   Column('ip', String),
                                   Column('port', String)
                                   )

        # Создаём таблицу контактов пользователей
        contacts = Table('Contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user', ForeignKey('Users.id')),
                         Column('contact', ForeignKey('Users.id'))
                         )

        # Создаём таблицу истории пользователей
        users_history_table = Table('History', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user', ForeignKey('Users.id')),
                                    Column('sent', Integer),
                                    Column('accepted', Integer)
                                    )

        # Создаем таблицы
        self.metadata.create_all(self.database_engine)

        # Создаем отображения
        # Связываем класс в ORM с таблицей
        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, user_login_history)
        mapper(self.UsersContacts, contacts)
        mapper(self.UsersHistory, users_history_table)

        # Создаем сессию
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()
        # Если в таблице активных пользователей есть записи, то их нужно удалить
        # Когда устанавливаем соединение, очищаем таблицу активных пользователей
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    # Функция выполняющяяся при входе пользователя, записывает в базу факт входа
    # Обновляет открытый ключ пользователя при его изменении
    def user_login(self, username, ip_address, port, key):
        # Запрос в базу на поиск пользователя с таким же именем
        rez = self.session.query(self.AllUsers).filter_by(name=username)

        # Если имя пользователя уже присутствует в таблице, обновляем время последнего входа
        # и проверяем корректность ключа. Если клиент прислал новый ключ, сохраняем его.
        if rez.count():
            user = rez.first()
            user.last_login = datetime.datetime.now()
            if user.pubkey != key:
                user.pubkey = key
        # если нет - создаем нового пользователя
        else:
            raise ValueError('Пользователь не зарегистрирован.')

        # Теперь можно создать запись в таблицу активных пользователей о факте входа
        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)

        # И сохранить в истории входов
        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)

        # Сохраняем изменения
        self.session.commit()

    # Функция регистрации пользователя. Принимает имя и хэш пароля, создает запись в таблице статистики
    def add_user(self, name, passwd_hash):
        user_row = self.AllUsers(name, passwd_hash)
        self.session.add(user_row)
        self.session.commit()
        history_row = self.UsersHistory(user_row.id)
        self.session.add(history_row)
        self.session.commit()

    # Функция удаляющая пользователя из базы
    def remove_user(self, name):
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.query(self.LoginHistory).filter_by(name=user.id).delete()
        self.session.query(self.UsersContacts).filter_by(user=user.id).delete()
        self.session.query(self.UsersContacts).filter_by(contact=user.id).delete()
        self.session.query(self.UsersHistory).filter_by(user=user.id).delete()
        self.session.query(self.AllUsers).filter_by(name=name).delete()
        self.session.commit()

    # Функция возвращает хэш требуемого пользователя
    def get_hash(self, name):
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.passwd_hash

    # Функция возвращает публичный ключ пользователя
    def get_pubkey(self, name):
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.pubkey

    def check_user(self, name):
        if self.session.query(self.AllUsers).filter_by(name=name).count():
            return True
        else:
            return False

    # функция фиксирующая отключение пользоваетля
    def user_logout(self, username):
        # Запрашиваем пользователя, что покидает нас
        # получаем запись из таблицы AllUsers
        user = self.session.query(self.AllUsers).filter_by(name=username).first()

        # Удаляем его из таблицы активных пользователей
        # Удаляем запись из таблицы ActiveUsers
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()

        # Применяем изменения
        self.session.commit()

    # Функция фиксирует передачу сообщения и делает соответствующую запись в БД
    def process_message(self, sender, recipient):
        # Получаем ID отправителя и получателя
        sender = self.session.query(self.AllUsers).filter_by(name=sender).first().id
        recipient = self.session.query(self.AllUsers).filter_by(name=recipient).first().id
        # Запрашиваем строки из истории и инкрементируем счетчики
        sender_row = self.session.query(self.UsersHistory).filter_by(user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(self.UsersHistory).filter_by(user=recipient).first()
        recipient_row.accepted += 1
        self.session.commit()

    # Функция добавляет контакт для пользователя.
    def add_contact(self, user, contact):
        # Получаем ID пользователей
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact).first()

        # Проверяем что не дубль и что контакт может существовать (полю пользователь мы доверяем)
        if not contact or self.session.query(self.UsersContacts).filter_by(user=user.id, contact=contact.id).count():
            return

        # Создаём объект и заносим его в базу
        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    # Функция удаляет контакт из базы данных
    def remove_contact(self, user, contact):
        # Получаем ID пользователей
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact).first()

        # Проверяем что контакт может существовать (полю пользователь мы доверяем)
        if not contact:
            return

        # Удаляем требуемое
        self.session.query(self.UsersContacts).filter(
            self.UsersContacts.user == user.id,
            self.UsersContacts.contact == contact.id
        ).delete()
        self.session.commit()

    # Функция возвращает список известных пользователей со временем последнего входа.
    def users_list(self):
        # Запрос строк таблицы пользователей.
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login
        )
        # возвращаем список кортежей
        return query.all()

    # функция возвращает список активных пользователей
    def active_users_list(self):
        # запрашиваем соединение таблиц и собираем кортежи имя, адрес, порт, время
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        # возвращаем список кортежей
        return query.all()

    # Функция возвращает историю входов по пользователю или всем пользователям
    def login_history(self, username=None):
        # Запрашивает историю входа
        query = self.session.query(self.AllUsers.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port
                                   ).join(self.AllUsers)
        # Если было указано имя пользователя, то фильтруем по нему
        if username:
            query = query.filter(self.AllUsers.name == username)
        # Возвращаем список кортежей
        return query.all()

    # Функкция возвращает список контактов пользователя
    def get_contacts(self, username):
        # Запрашиваем указанного пользователя
        user = self.session.query(self.AllUsers).filter_by(name=username).one()

        # Запрашиваем список его контактов
        query = self.session.query(self.UsersContacts, self.AllUsers.name). \
            filter_by(user=user.id). \
            join(self.AllUsers, self.UsersContacts.contact == self.AllUsers.id)

        # выбираем только имена пользователй и возвращаем их
        return [contact[1] for contact in query.all()]

    # Функция возвращает количество переданных и полученных сообщений
    def message_history(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
            self.UsersHistory.sent,
            self.UsersHistory.accepted
        ).join(self.AllUsers)
        # Возвращаем список кортежей
        return query.all()


# Отладка
if __name__ == '__main__':
    test_db = ServerDBase('server_base.db3')
    # выполним подключение пользователя
    test_db.user_login('client_1', '192.168.1.4', 8888)
    test_db.user_login('client_2', '192.168.1.5', 7777)
    # выводим список всех пользователей
    print(test_db.users_list())
    # # выводим список кортежей - активных пользователей
    # print(test_db.active_users_list())
    # # выполним отключение пользователя
    # test_db.user_logout('client_1')
    # # выводим список активных пользователей
    # print(test_db.active_users_list())
    # # запрашиваем историю входов по пользователю
    # test_db.login_history('client_1')
    # # выводим список известных пользователей
    # print(test_db.users_list())
    test_db.process_message('client_1', 'client_2')
    print(test_db.message_history())
