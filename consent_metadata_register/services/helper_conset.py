#import datetime
from celery import current_app

from celery import Celery
from celery.utils.log import get_task_logger
appli = Celery('update_user_consent', broker='amqp://guest@localhost:5672//', backend='rpc://')

from services.erase_user_data import add_erase_data_to_redis
from datetime import datetime

def get_updated_consent_data(consent_data, consent_delete_attr):
    for element in consent_delete_attr:
        if element in consent_data:
            consent_data[element]["erase"] = True
    return consent_data

def get_updated_consent_data_all(consent_data):
    print("this is element", consent_data)
    for element in consent_data:
        if element not in("id", "erase_all"):
            consent_data[element]["erase"] = True
    return consent_data

def update_dict(dict1, dict2):
    if dict2.get("erase_all", True):
        for key, value in dict1.items():
            if isinstance(value, dict) and "erase" in value:
                dict1[key]["erase"] = True
                dict1[key]["date"] = datetime.now().isoformat()
                
    else:
        for key, value in dict2.items():
            if isinstance(value, dict) and key in dict1:
                if "erase" in value and value["erase"]:
                    dict1[key]["erase"] = True
                    dict1[key]["date"] = datetime.now().isoformat()
        dict1["erase_all"] = True            
    return dict1

#@appli.task(name="delete_consent_task")
#def add_deleted_data_to_mysql():
    
    

@appli.task(name="erase_consent_data_task")
def register_data_redis(data_from_redis, data_from_api,id):
    erase_all = data_from_api["erase_all"]
    #print(data_from_api)
    if erase_all == False:
        consent = data_from_api["attrs"]
        data_dicts = get_updated_consent_data(data_from_redis, consent)
        data_dicts["id"] = id
        add_erase_data_to_redis(data_dicts, id)
        return data_dicts
    else:
        elements = get_updated_consent_data_all(data_from_redis)
        elements["id"] = id
        print("elements",elements)
        add_erase_data_to_redis(elements, id)
        return elements


def filter_user_consent(consentset, consent_filter):
    print("this is consent_filter", consent_filter)
    my_result = set()
    if consent_filter.get("erase_all", False):
        return {}
    else:
        for element in consentset:
            if element in consent_filter and  consent_filter[element].get("erase", False):
                my_result.add(element)
        return my_result

def create_erase_structure(input_set):
    output = {"erase_all": False}
    for element in input_set:
        output[element] = {"erase": False, "date": datetime.utcnow().isoformat()}
    return output
    
    
def update_data(user_data):
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
    personal_data["client_id"] = user_data["data"]["client"]["client_id"]
    return personal_data    
    
    

