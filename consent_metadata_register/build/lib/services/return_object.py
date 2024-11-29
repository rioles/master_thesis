from typing import Dict, Any
from models.consent_attribut import ConsentAttribute
from models.data_purpose import DataPurpose
from models.data_controller import DataController
from models.data_processor import DataProcessor
from models.data_provider import DataProvider

class ReturnObject:
  def __init__(self, request_data: Dict[str, Any]):
    self.request_data = request_data

  def consent_attribut_array(self):
    consent_array = []
    consent_grant = set()
    for key in self.request_data["consent"]:
      consent_array.append(key)
    for key in self.request_data["consent_grant"]:
      if self.request_data["consent_grant"][key]:
        consent_grant.add(key)
    return consent_grant, consent_array

  def create_consent_attribut_object(self):
    consent_array = self.consent_attribut_array()[1]
    consent_grant = self.consent_attribut_array()[0]
    consent_object_dict = []
    consent_object = []
    for element in consent_array:
      if element in consent_grant:
        object_dict = {}
        attribut_dict = {"contains_personal_data": True, "data_attribute": element}
        consent_attribut_object = ConsentAttribute(**attribut_dict)
        object_dict[element] = consent_attribut_object
        consent_object_dict.append(object_dict)
        consent_object.append(consent_attribut_object)
        # Indentation adjusted for print statement
        print("this is the dict", attribut_dict)

    return consent_object, consent_object_dict
    
  
  def data_to_get_from_provider(self):
  	consent_grant = self.consent_attribut_array()[0]
  	consent_need = {"user_anip": self.request_data["user_anip"]}
  	i = 0
  	for element in consent_grant:
  		consent_need[element] = i
  		i = i+1
  	return consent_need
  	
  def create_purpose_object(self):
    purpose_data = []
    consent_object = self.create_consent_attribut_object()[1]
    for element in consent_object:
      element_key = list(element.keys())[0]  # Simplified list access
      element_value = element[element_key]
      for obj in self.request_data["consent"][element_key]:
        purpose_dict = {"purpose_basic_specification": obj, "consent_attribute_id": element_value.id}
        purpose_obj = DataPurpose(**purpose_dict)  # Assuming DataPurpose class exists
        purpose_data.append(purpose_obj.to_dict())
    return consent_object, purpose_data

  def create_data_controller(self):
    data_controler_dict = {"data_controller_name": self.request_data["client"]["client_name"], "id": self.request_data["client"]["client_id"], "data_controller_type": "private"}
    data_controler_obj = DataController(**data_controler_dict)
    return data_controler_obj

  def create_data_provider(self):
    if "provider" not in self.request_data:
      data_provider_dict = {"provider_name": "ANIP", "type_of_provider": "public"}
      data_provider = DataProvider(**data_provider_dict)
      return data_provider
    else:
      data_provider_dict = {"provider_name": self.request_data["provider"]["provider_name"], "type_of_provider": self.request_data["provider"]["type_of_provider"]}
      data_provider = DataProvider(**data_provider_dict)
      return data_provider

  def create_data_processor(self):
    if "processor" not in self.request_data:
      data_processor_dict = {"data_process_name": self.request_data["client"]["client_name"], "data_process_type": "private", "data_controller_id": self.request_data["client"]["client_id"]}
      data_processor = DataProcessor(**data_processor_dict)
      return data_processor
    else:
      data_processor_dict = {"data_process_name": self.request_data["processor"]["processor_name"], "data_process_type": self.request_data["processor"]["type_of_processor"], "data_controller_id": self.request_data["client"]["client_id"]}
      data_processor = DataProcessor(**data_processor_dict)
      return data_processor     		
    	
my_dict = {
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
        "email_address": False,
        "name": True,
        "telephone_number": True
    },
    "consent_grant_date": "Wed, 27 Nov 2024 11:01:44 GMT",
    "expiration_date": "2025-11-12T13:48:15",
    "user_anip": 1245689
}    	

def consent_give_by_user(consent_give):
    my_consent_set = set()
    for key in consent_give:
        if consent_give[key]:
            my_consent_set.add(key)
    return my_consent_set
	

obj = ReturnObject(my_dict)
print(obj.consent_attribut_array())
print(obj.create_consent_attribut_object())
print(obj.create_purpose_object())
print(obj.create_data_controller())
print(obj.create_data_provider())
print(obj.create_data_processor())
print(obj.data_to_get_from_provider())	
    		
    		
    		
    	
    	
