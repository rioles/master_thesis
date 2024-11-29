from dateutil import parser
from datetime import datetime

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"

class CheckConsentValidity:
    def __init__(self, data):
        self.data = data

    def set_defaults_for_time(self, date):
        """
        Sets hour, minute, and second to 00 if they are not specified in the datetime object.
        :param date: datetime object with potentially missing hour, minute, or second
        :return: A datetime object with hour, minute, and second set to 00 where missing
        """
        # If the date is already a complete datetime object, return it as is
        if hasattr(date, 'hour') and hasattr(date, 'minute') and hasattr(date, 'second'):
            return date
        
        # Set defaults for hour, minute, second if not provided
        return datetime(date.year, date.month, date.day, 
                        getattr(date, 'hour', 0), 
                        getattr(date, 'minute', 0), 
                        getattr(date, 'second', 0))
                    
    def convert_to_datetime(self, date_input):
        """
        Converts a date string to a datetime object.
        If the input is already a datetime object, it returns it with default time values.
        
        :param date_input: Date in string format or a datetime object.
        :return: Corresponding datetime object.
        """
        if isinstance(date_input, str):
            date_input = parser.parse(date_input)
        
        if isinstance(date_input, datetime):
        	
            return self.set_defaults_for_time(date_input)
        
        raise ValueError("Input must be a date string or a datetime object.")

    def check_validity(self, date_from_redis):
        date_from_redis = self.convert_to_datetime(date_from_redis)
        date_now = self.convert_to_datetime(datetime.utcnow())
        return date_now > date_from_redis

    def add_validity(self, date):
        if self.check_validity(date):
            self.data["validity"] = False
        else:
            self.data["validity"] = True
        return self.data

if __name__ == "__main__":
    data = {
        
            "client": {
                "client_id": "ozana-82df06aa132847b8972cc0d83c589411",
                "client_name": "ozana"
            },
            "consent": {
                "age": [
                    "age restrictions",
                    "targeted marketing"
                ],
                "email_address": [
                    "communication",
                    "account creation",
                    "password recovery"
                ],
                "name": [
                    "identification",
                    "personalization"
                ],
                "telephone_number": [
                    "contact",
                    "verification"
                ]
            },
            "consent_grant": {
                "age": True,
                "email_address": True,
                "name": True,
                "telephone_number": True
            },
            "consent_grant_date": "Tue, 12 Nov 2024 14:01:00 GMT",
            "expiration_date": "2025-11-12T13:48:15",
            "user_anip": 789456123
        
    }

    a = CheckConsentValidity(data)
    print(a.convert_to_datetime(data["expiration_date"]))
    print(a.convert_to_datetime(data["consent_grant_date"]))
    print(a.check_validity(data["expiration_date"]))
