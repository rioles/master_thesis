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
#from avro_schemas_registry import generate_schema_from_dict
import json
my_task = RabbitMQ(appli)

def add_erase_data_to_redis(erase_structure, id):
    nosql_storage.set(id, json.dumps(erase_structure))
    
def get_data(id):
    nosql_storage.get(id)  
    
    

class ConsentManagerD:
    def __init__(self, request_data):
        self.request_data = request_data
        
    def get_attribut_id(self):
    	id_attrs = []
    	attrs = self.request_data["attrs"]
    	for element in attrs:
    		attr_id = storage.find_by(ConsentAttribute, **{"data_attribute": element})
    		if attr_id is not None:
    			id_attrs.append(attr_id)
    	return id_attrs

    def erase_consent(self):
        perm = []
        
        for element in self.get_attribut_id():
        	new_perm_dict = {}
        	permission_dict = {
                    "id_data_subject": self.request_data["user_anip"],
                    "data_controller_id": self.request_data["id_enterprise"],
                    "consent_attribute_id": element.id,
                    "erase": False,
                }
        	permission_obj = storage.find_by(PermissionIdentity, **permission_dict)
        	
        	if permission_obj is not None:
        	    new_perm_dict["id_data_subject"] = self.request_data["user_anip"]
        	    new_perm_dict["data_controller_id"] = self.request_data["id_enterprise"]
        	    new_perm_dict["consent_attribute_id"] = element.id
        	    new_perm_dict["erase"] = True
        	    new_perm_dict["data_provider_id"] = permission_obj.data_provider_id
        	    new_perm_dict["expiration_date"] = permission_obj.expiration_date
        	    new_perm_dict["beginning_date"] = permission_obj.beginning_date
        	    new_perm_dict["consent_date"] = permission_obj.consent_date
        	  
        	perm_obj = PermissionIdentity(**new_perm_dict)
        	print(perm_obj)
        	perm_obj.save()
        	perm.append(perm_obj.to_dict())
        return perm
              	
    def process_erase_data():
        self.erase_consent()
    
        data_controller_id = self.request_data["data_controller_id"]
        user_id = self.request_data["user_anip"]
        data_controller = storage.find_by(DataController, **{"id": data_controller_id})

        message = {
            "event": "data_erased",
            "status": 204,
            "user": {
                "user_id": user_id
            },
            "client": {
                "id": data_controller.id,
                "name": data_controller.data_controller_name
            },
            "erase_time": {
                "erase_date": nosql_storage.get(id)["erase_date"]
            },
            "data": [],
        }

        my_task.publish_message("send_webhook", "data_erase", **message)
