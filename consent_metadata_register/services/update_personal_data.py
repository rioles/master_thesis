from models.permission_identity import PermissionIdentity
from models.consent_attribut import ConsentAttribute
from models.data_purpose import DataPurpose
from models.data_controller import DataController
from models.data_processor import DataProcessor
from models.data_provider import DataProvider
from datetime import datetime
from models import nosql_storage
from models import storage
from message_queu.rabbitmq import RabbitMQ, appli
from models.permission_identity import PermissionIdentity
from models.data_controller import DataController
from models.data_provider import DataProvider
#from avro_schemas_registry import generate_schema_from_dict
import json
my_task = RabbitMQ(appli)
from celery import current_app

from celery import Celery
from celery.utils.log import get_task_logger
appli = Celery('update_user_consent', broker='amqp://guest@localhost:5672//', backend='rpc://')


def add_erase_data_to_redis(erase_structure, id):
    nosql_storage.set(id, json.dumps(erase_structure))
    
def get_data(id):
    nosql_storage.get(id)  
    
class UpdatePersonalData:
    def __init__(self, request_data):
        self.request_data = request_data
        
    def get_data_controller_id(self):
        id_attrs = []
        provider_name = self.request_data.get("provider")
        if not provider_name:
            raise ValueError("Provider name is missing in request data")
        provider = storage.find_by(DataProvider, **{"provider_name": provider_name})
        filter_dict = {"data_provider_id": provider.id, "id_data_subject": self.request_data["user_anip"]}
        permission_identities = storage.find_all_by(PermissionIdentity, **filter_dict)
        data_controllers_id = set()
        if permission_identities is not None:
            for element in permission_identities:
                data_controllers_id.add(element.data_controller_id)
                # print(data_controllers_id)
        return data_controllers_id
     
    def get_original_data_controller_id(self):
        ids = self.get_data_controller_id()
        original_data_controller_ids = set()
        for element in ids:
            data_controller = storage.find_by(DataController, **{"id": element})
            original_data_controller_ids.add(data_controller.data_controller_id)
        return original_data_controller_ids

    def update_data(self):
        user_anip = self.request_data["user_anip"]
        user_data_from_provider = {}
        attrs = self.request_data["attrs"]
        data = None
        
        with open("anip_response.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        for element in data:
            print(type(element["customer"]["npi"]))
            if element["customer"]["npi"] == user_anip:
                print("another one", element["customer"]["npi"])
                print(f"User found: {element['customer']['npi']}")
                for els in attrs:
                    if els in element["customer"]:
                        element["customer"][els] = self.request_data[els]
        print(data)
        with open("anip_response.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        return self.request_data

@appli.task(name="update_consent_data_task")		
def get_data_update(obj):
    ids = obj.get_original_data_controller_id()
    user_data_updated = obj.request_data
    for element in ids:
        user_data_updated["client_id"] = element
    return user_data_updated
    		

    	
    	

my_dict = {
    "attrs": ["name","age","email"],
    "user_anip":"1245689",
    "id_enterprise":"8ab52fb7-92e4-443f-b4f4-30dd3af72933",
    "provider":"ANIP",
    "name": "GBETOs",
    "email_address": "rioles1992@gmail.com"
}
a = UpdatePersonalData(my_dict)
print(a.get_data_update(a))    	
