"""Clients Unit-tests"""

import sys
from soc_settings.config import *
import unittest
from client import create_presence, process_ans
from errors import NoRequiredFieldInTheAcceptedDictionary, ServerError
sys.path.append('../')


class MyTestCaseClient(unittest.TestCase):
    """Базовый класс"""

    def test_def_correct_presence(self):
        """Тест коректного запроса"""
        test = create_presence('Guest')
        # время необходимо приравнять принудительно иначе тест никогда не будет пройден
        test[TIME] = 1.1
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1,
                                USER: {ACCOUNT_NAME: 'Guest'}})

    def test_200_correct_ans(self):
        """Тест корректного разбора ответа 200"""
        self.assertEqual(process_ans({RESPONSE: 200}), '200 : OK')

    # тест корректного разбора 400
    def test_400_ans(self):
        self.assertRaises(ServerError, process_ans, {RESPONSE: 400, ERROR: 'Bad Request'})

    def test_no_response(self):
        """Тест исключения без поля RESPONSE"""
        self.assertRaises(NoRequiredFieldInTheAcceptedDictionary, process_ans, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
