from bloom_filter import BloomFilter
from services.check_consent_validity import CheckConsentValidity
from models import storage
import json
import hashlib
import struct

bloom_filter = BloomFilter(size=10000, hash_count=7, redis_key="consent_data")
bloom_filter1 = BloomFilter(size=10000, hash_count=7, redis_key="user_id_enterprise_id")

class ConsentValidityManager:
    def __init__(self, producer):
        self.producer = producer

    def process_message(self, message):
        """
        Define how to process the received message.
        :param message: The message received from Kafka.
        """
        print(f"Consumed message: {message}")
        user_id_client_id = concaten_user_id_and_enteripse(message)
        # user_id_client_id_str = json.dumps(user_id_client_id)
        print(user_id_client_id)
        print(message)
        messages = json.dumps(message)
        string_id = ensure_string(user_id_client_id[1])
        # data = {user_id_client_id[2]: message}
        if not bloom_filter1.check(storage, user_id_client_id[2]):
            bloom_filter.add(storage, message)
            bloom_filter1.add(storage, user_id_client_id[2])
            storage.set(user_id_client_id[2], messages)
            message["validity"] = True
            self.producer.send_message(message, string_id)
            return
        else:
            if bloom_filter.check(storage, message):
                data = storage.get(user_id_client_id[2])
                
                date = extract_expiration_date(data)
                print("data is not None", data)
                print("type of data",type( data))
                
                if data is not None:
                    consent_checker = CheckConsentValidity(message)
                    data = consent_checker.add_validity(date)
                    print("flag", data)
                    print("type of data", type(data))
                    self.producer.send_message(data, string_id)
            else:
                message["validity"] = True
                bloom_filter.add(storage, message)
                bloom_filter1.add(storage, user_id_client_id)
                storage.set(user_id_client_id[2], messages)
                self.producer.send_message(message, string_id)

def concaten_user_id_and_enteripse(data):
    client_id = data["client"]["client_id"]
    user_id = data["user_anip"]
    return client_id, user_id, f"{user_id}_{client_id}"


def extract_expiration_date(data):
  """
  Extracts the expiration date from the given data, handling both string and dictionary formats.

  Args:
      data: The data to extract the expiration date from. It can be a JSON string or a dictionary.

  Returns:
      The expiration date as a datetime.date object if found and valid, otherwise None.
  """

  if isinstance(data, str):
    try:
      python_dict = json.loads(data)
      return python_dict["expiration_date"]
    except ValueError:
      return None
  else:
    return data["expiration_date"]


def ensure_string(data):
    """
    Check if data is an int and convert to string if necessary.

    :param data: The data to check and possibly convert.
    :return: The data as a string.
    """
    if isinstance(data, int):
        return str(data)
    return data


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
        "consent_grant_date": "Tue, 12 Nov 2024 17:51:38 GMT",
        "expiration_date": "2025-11-12T13:48:15",
        "user_anip": 1245689
    }
    print(concaten_user_id_and_enteripse(data))
