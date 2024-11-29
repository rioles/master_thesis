""" Config server logger"""

import sys
import os
import logging
import logging.handlers
import os
from soc_settings.config import LOGGING_LEVEL
sys.path.append('../')

# создаём formatter:
s_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

# Подготовка имени файла для логирования
path = os.path.dirname(os.path.abspath(__file__))
# соединяет пути с учётом особенностей операционной системы
path = os.path.join(path, 'server.log')

# создаём потоки вывода логов
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(s_formatter)
stream_handler.setLevel(logging.INFO)
log_file = logging.handlers.TimedRotatingFileHandler(path, encoding='utf8', interval=1, when='D')
log_file.setFormatter(s_formatter)

# создаём регистратор и настраиваем его
logger = logging.getLogger('server')
logger.addHandler(stream_handler)
logger.addHandler(log_file)
logger.setLevel(LOGGING_LEVEL)

# отладка
if __name__ == '__main__':
    logger.critical('Критическая ошибка')
    logger.error('Ошибка')
    logger.debug('Отладочная информация')
    logger.info('Информационное сообщение')
