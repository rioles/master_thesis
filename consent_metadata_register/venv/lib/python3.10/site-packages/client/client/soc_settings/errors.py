"""Errors"""
class ServerError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class NoRequiredFieldInTheAcceptedDictionary(Exception):
    """
    Error - there is no required field in the accepted dictionary
    """
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'В принятом словаре отсутствует обязательное поле {self.missing_field}.'
