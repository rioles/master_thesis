from typing import Dict, Any
from services.helper_conset import create_erase_structure, filter_user_consent
from services.return_object import ReturnObject, my_dict
from models.permission_identity import PermissionIdentity
from models.consent_attribut import ConsentAttribute
from models.data_purpose import DataPurpose
from models.data_processor import DataProcessor
from models.data_controller import DataController
from models.data_provider import DataProvider
from datetime import datetime
import json
from models import nosql_storage

from models import storage
from message_queu.rabbitmq import RabbitMQ, appli
my_task = RabbitMQ(appli)

class ConsentRegistration:
    def __init__(self, request_data, return_object):
        self.request_data = request_data
        self.return_object = return_object

    def register_consent(self):
        consent_attributs_arr = self.return_object.consent_attribut_array()
        print("this is consent array", consent_attributs_arr)
        consent_attribut = self.return_object.create_consent_attribut_object()[0]
        print(consent_attribut)
        
        data_controler_object = self.return_object.create_data_controller()
        data_controller_from_db = storage.find_by(DataController, **{"data_controller_name":data_controler_object.data_controller_name})
        data_controller_obj = data_controller_from_db if data_controller_from_db is not None else data_controler_object
        
        data_processor = self.return_object.create_data_processor()
        data_processor_from_db = storage.find_by(DataProcessor, **{"data_process_name":data_processor.data_process_name})
        data_processor_obj = data_processor_from_db if data_processor_from_db is not None else data_processor
        
        data_provider = self.return_object.create_data_provider()
        data_proviver_from_db = storage.find_by(DataProvider, **{"provider_name":data_provider.provider_name})
        data_provider_obj = data_proviver_from_db if data_proviver_from_db is not None else data_provider
        meta_data_id_data_controller = {"data_controller_id":data_controller_obj.id}
        meta_data_id_data_controller = {"data_controller_ids":data_controller_obj.data_controller_id} 
        

        # data_controler_object.save()
        # data_processor.save()
        # data_provider.save()

        all_object_permission_objects = []
        all_object_to_insert_set = set()
        all_object_to_insert_golabl = []
        all_object_data_controller = []
        all_object_data_provider = []
        all_object_data_processor = []
        all_object_data_purpos = []
        all_object_consent_attr = []
        all_objects_dict = {}
        i = 0
        for element in consent_attribut:
            
            all_object_to_insert = []
            
            element_from_storage = storage.find_by(ConsentAttribute, **{"data_attribute":element.data_attribute})
            print("does this is None", element_from_storage) 
            element = element if element_from_storage is None else element_from_storage
            print("dataattributname", element.data_attribute)	
            permission_dict = {}
            permission_dict["id_data_subject"] = self.request_data["user_anip"]
            permission_dict["expiration_date"] = self.request_data["expiration_date"]
            permission_dict["beginning_date"] = self.request_data.get("beginning_date", datetime.now())  # Using get method for optional key
            permission_dict["data_provider_id"] = data_provider_obj.id
            permission_dict["data_controller_id"] = data_controller_obj.id
            permission_dict["consent_attribute_id"] = element.id
            permission_dict["erase"] = False
            permission_dict["consent_date"] = datetime.now()

            permission_object = PermissionIdentity(**permission_dict)
            purpose_objs = return_purpose_object(element, self.request_data)
            print("this is purpose", purpose_objs)
            if data_controller_from_db is None:
                all_object_data_controller.append(data_controller_obj)
            if data_processor_from_db is None:
                all_object_data_processor.append(data_processor_obj)
            if data_proviver_from_db is None:    
                all_object_data_provider.append(data_provider_obj)
            print("this is purpose objss", purpose_objs)				
            if element_from_storage is None:
                all_object_consent_attr.append(element)
            # permission_object.save()
            #all_object_to_insert.append(permission_object)
            if purpose_objs is not None:
                all_object_data_purpos.extend(purpose_objs)
            
            all_object_permission_objects.append(permission_object)
            all_object_to_insert_golabl.extend(all_object_to_insert)
            
            print(f"all object to insert {i}: {all_object_to_insert}")
            
            
            #
            
            
            print("all object", all_object_to_insert)
            i = i+1
        all_object_data_controller = set(all_object_data_controller)
        all_object_data_controller_no_duplicate = list(all_object_data_controller)
        meta_data_id_data_controller["data_controller"] = all_object_data_controller_no_duplicate
        
        all_object_data_provider_set = set(all_object_data_provider)
        all_object_data_provider_no_duplicate = list(all_object_data_provider_set)
        meta_data_id_data_controller["data_provider"] = all_object_data_provider_no_duplicate
        print("all_object_data_provider_no_duplicate",all_object_data_provider_no_duplicate)
        
        all_object_data_processor_set = set(all_object_data_processor)
        all_object_data_processor_no_duplicate = list(all_object_data_processor_set)
        meta_data_id_data_controller["data_processor"] = all_object_data_processor_no_duplicate
        print("all_object_data_processor_no_duplicate",all_object_data_processor_no_duplicate)
        
        all_object_data_purpos_set = set(all_object_data_purpos)
        all_object_data_purpos_no_duplicate = list(all_object_data_purpos_set)
        meta_data_id_data_controller["data_purpos"] = all_object_data_purpos_no_duplicate
        print("all_object_data_purpos_no_duplicate",all_object_data_purpos_no_duplicate)
        
        all_object_permission_objects_set = set(all_object_permission_objects)
        all_object_permission_objects_no_duplicate = list(all_object_permission_objects_set)
        meta_data_id_data_controller["object_permission"] = all_object_permission_objects_no_duplicate
        print("all_object_permission_objects_no_duplicate",all_object_permission_objects_no_duplicate)
        
        all_object_consent_attr_set = set(all_object_consent_attr)
        all_object_consent_attr_no_dup = list(all_object_consent_attr_set)
        meta_data_id_data_controller["consent_attr"] = all_object_consent_attr_no_dup
        print("all_object_consent_attr_no_dup",all_object_consent_attr_no_dup)
             
        #storage.bulk_transaction(
            #[(storage.bulk_save, all_object_data_controller_no_duplicate if all_object_data_controller_no_duplicate else []),
            #(storage.bulk_save, all_object_data_processor_no_duplicate if all_object_data_processor_no_duplicate else []),
            #(storage.bulk_save, all_object_data_provider_no_duplicate if all_object_data_provider_no_duplicate else []),
            #(storage.bulk_save, all_object_consent_attr_no_dup),
            #(storage.bulk_save, all_object_data_purpos_no_duplicate),
            #(storage.bulk_save, all_object_permission_objects_no_duplicate)]
            
            
        #)
        #meta_data_id_data_controller["metadata"] = all_object_no_duplicate
        meta_data_id_data_controller["id_data_controller"] = data_controler_object.id    
        print("all_object_data_controller_no_duplicate",all_object_data_controller_no_duplicate)    
        return meta_data_id_data_controller

    def process_matadata_registration(self):
        data_controler_object_id = self.register_consent()["data_controller_id"]
        print("id_datacontroller", data_controler_object_id)
        data_controler_objects = self.register_consent()
        print("all data objects",data_controler_objects)
        consent_needed_data = self.return_object.data_to_get_from_provider()
        consent_attributs = consent_needed_data["consent_attributs"]
        user_id = self.request_data["user_anip"]
        id = concatenate_strings(user_id, self.register_consent()["data_controller_ids"])
        print("id_datacontroller", data_controler_object_id)
        print("this is id",id)
        print("this is consent_need",consent_needed_data)
        if nosql_storage.get(id) is None:
            erase_structure = create_erase_structure(consent_attributs)
            #erase_structure["id_data_controller"] = 
            print("this is erase_structure", erase_structure)
            nosql_storage.set(id, json.dumps(erase_structure))
            #storage.bulk_transaction(
            #[(storage.bulk_save, data_controler_objects["data_controller"] if data_controler_objects["data_controller"] else []),
            #(storage.bulk_save, data_controler_objects["data_processor"] if data_controler_objects["data_processor"] else []),
            #(storage.bulk_save, data_controler_objects["data_provider"] if data_controler_objects["data_provider"] else []),
            #(storage.bulk_save, data_controler_objects["consent_attr"]),
            #(storage.bulk_save, data_controler_objects["data_purpos"]),
            #(storage.bulk_save, data_controler_objects["object_permission"])]
            
            
        #)
            #self.register_consent()
            #send_consent_metadata(consent_needed_data)
        else:
            
            consent_filter = filter_user_consent(consent_attributs, json.loads(nosql_storage.get(id)))
            consent_needed_data["consent_attributs"] = consent_filter
            print("this is consent_need",consent_needed_data["consent_attributs"])
            #storage.bulk_transaction(
            #[(storage.bulk_save, data_controler_objects["data_controller"] if data_controler_objects["data_controller"] else []),
            #(storage.bulk_save, data_controler_objects["data_processor"] if data_controler_objects["data_processor"] else []),
            #(storage.bulk_save, data_controler_objects["data_provider"] if data_controler_objects["data_provider"] else []),
            #(storage.bulk_save, data_controler_objects["consent_attr"]),
            #(storage.bulk_save, data_controler_objects["data_purpos"]),
            #(storage.bulk_save, data_controler_objects["object_permission"])]   
        #)
            #self.register_consent()
            #send_consent_metadata(self.consent_needed_data)


def send_consent_metadata(meta_data):
    avroschema_dict = generate_schema_from_dict(meta_data)
    schema_url = os.getenv('schema_url')
    topic_name = os.getenv('topic_name_1')
    subject_name = os.getenv('subject_name')
    bootstrap_server = os.getenv('bootstrap_server')
    client = SchemaClient(schema_url, subject_name, avroschema_dict, "AVRO")
    client.register_schema()
    client.set_compatibility("FORWARD")
    schema = client.get_schema_str()
    producer = AvroProducerClass(bootstrap_server, topic_name, client.schema_client, schema)
    producer.send_message(data, data["client"]["client_id"])


def concatenate_strings(string1, string2):
    """
    Concatenate two strings with an underscore as a separator.

    :param string1: The first string.
    :param string2: The second string.
    :return: The concatenated result of string1 and string2 separated by an underscore.
    """
    return f"{string1}_{string2}"

def send_data_to_topic(data):
    try:
        schema_file = os.getenv('schema_file')
        schema_url = os.getenv('schema_url')
        topic_name = os.getenv('topic_name')
        subject_name = os.getenv('subject_name')
        bootstrap_server = os.getenv('bootstrap_server')

        schema_dict = load_avro_schema(schema_file)
        client = SchemaClient(schema_url, subject_name, schema_dict, "AVRO")
        client.set_compatibility("FORWARD")
        schema = client.get_schema_str()

        producer = AvroProducerClass(bootstrap_server, topic_name, client.schema_client, schema)
        producer.send_message(data, data["client"]["client_id"])
    except Exception as e:
        logger.error(f"Error in send_data_to_topic: {e}")
        raise

def return_purpose_object(obj:ConsentAttribute, req:Dict[str, Any]):
    purpose_data = []
    for element in req["consent"][obj.data_attribute]:
        purpose_dict = {"purpose_basic_specification": element, "consent_attribute_id": obj.id}
        purpose_obj = DataPurpose(**purpose_dict)
        purpose_data.append(purpose_obj)
    return purpose_data
    

# Example usage
result = concatenate_strings("Hello", "world")
print(result)  # Output: Hello_world

print(my_dict)
b = ReturnObject(my_dict)
a = ConsentRegistration(my_dict, b)

print(a.process_matadata_registration())

