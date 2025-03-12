import os
import requests
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
import json
from celery import current_app

from celery import Celery
from celery.utils.log import get_task_logger
from message_queu.rabbitmq import RabbitMQ
appli = Celery('user_personal_data', broker='amqp://guest@localhost:5672//', backend='rpc://')


def get_data(user_data):
    personal_data = {}
    user_datas = {}
    user_anip = user_data["data"]["user_anip"]
    if isinstance(user_anip, int):
        user_anip = str(user_anip)
        
    print("user_anip",type(user_anip))
    consent_grant = user_data["data"]["consent_grant"]
    print("this is user_data",consent_grant)
    data = None
    with open("anip_response.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        
    
    for element in data:
        print(type(element["customer"]["npi"]))
        if element["customer"]["npi"] == user_anip:
            print("another one",element["customer"]["npi"])
            print(f"User found: {element['customer']['npi']}")
            user_datas = element["customer"]
            user_datas["address"] = element["address"]
    
    for element in consent_grant:
        print(element)
        if element in user_datas:
            print(True)
            personal_data[element] = user_datas[element]
    personal_data["user_anip"] = user_anip        
    
    return personal_data

def send_data_to_webhook(data):
    data = get_data(data)
    rabbitmq = RabbitMQ(appli)
    rabbitmq.publish_message("user_data","user_data", **data)            

# Example usage
if __name__ == "__main__":
    my_data = {
  "data": {
    "consent": {
      "name": ["identification", "personalization"],
      "age": ["age restrictions", "targeted marketing"],
      "telephone_number": ["contact", "verification"],
      "email_address": ["communication", "account creation", "password recovery"]
    },
    "client": {
      "client_name": "ozana",
      "client_id": "ozana-82df06aa132847b8972cc0d83c589411"
    },
    "consent_grant": {
      "name": True,
      "age": True,
      "telephone_number": True,
      "email_address": True
    },
    "user_anip": 1245689,
    "expiration_date": "2025-11-12T13:48:15",
    "validity": False
  }
}

    # Example of accessing environment variables
    print("CLIENT_ID:", os.environ.get('CLIENT_ID'))
    print(my_data["data"]["consent_grant"])
    print(get_data(my_data))
    print(send_data_to_webhook(my_data))

