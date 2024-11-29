"""Config client logger"""

import sys
import os
import logging
from soc_settings.config import LOGGING_LEVEL
sys.path.append('../')

# создаём formatter:
c_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

# Опеределяем имя файла для последующего логирования
path = os.path.dirname(os.path.abspath(__file__))
# Cоединяет пути с учётом особенностей операционной системы
path = os.path.join(path, 'client.log')

# создаём потоки вывода логов
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(c_formatter)
stream_handler.setLevel(logging.INFO)
log_file = logging.FileHandler(path, encoding='utf8')
log_file.setFormatter(c_formatter)

# создаём регистратор и настраиваем его
logger = logging.getLogger('client')
logger.addHandler(stream_handler)
logger.addHandler(log_file)
logger.setLevel(LOGGING_LEVEL)

# отладка
if __name__ == '__main__':
    logger.critical('Критическая ошибка')
    logger.error('Ошибка')
    logger.debug('Отладочная информация')
    logger.info('Информационное сообщение')
