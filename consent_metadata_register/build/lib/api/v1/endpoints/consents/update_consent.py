import os
import requests
from api.v1.endpoints import app_views
from flask_cors import cross_origin
from datetime import timedelta, datetime
from flask import abort, jsonify, make_response, request
from models import storage
from services.helper_conset import get_updated_consent_data, get_updated_consent_data_all, register_data_redis, appli, create_erase_structure, update_dict
from models.engine.redis_manager import RedisDBManager
from services.erase_user_data import add_erase_data_to_redis, get_data
from services.paginator import Paginator
from flask import send_file
from datetime import datetime
from flask_jwt_extended import (
    create_access_token, jwt_required, create_refresh_token, get_jwt_identity, 
    get_jwt, decode_token, verify_jwt_in_request
)
from datetime import datetime
from services.erase_user_data import ConsentManagerD
import fastavro
import json
from dotenv import load_dotenv
load_dotenv()
from message_queu.rabbitmq import RabbitMQ
from datetime import datetime


# logging.basicConfig(filename='/tmp/userlogin.log', level=logging.DEBUG, 
# format='%(asctime)s - %(levelname)s - %(message)s')

@app_views.route('/enterprise', methods=['POST'], strict_slashes=False)
@cross_origin()
def post_enterprise():
    """Create a new category"""
    if not request.get_json():
        return make_response(jsonify(
            {'status': '401', 'message': 'The request data is empty'}), 400)
    enter: EnterpriseService = EnterpriseService()    
    file_name, enterprise = enter.add_object(Enterprise, **request.get_json())
    response = send_file(file_name, as_attachment=True)
    # response.headers['Enterprise'] = jsonify(enterprise.to_dict())
    # return make_response(jsonify(enterprise.to_dict()), 201)
    return response, 201
    
    
@app_views.route('/delete', methods=['DELETE'],strict_slashes=False)
@cross_origin()
def delete_consent():
    r = RedisDBManager()
    datas = request.get_json()
    erase_all = datas["erase_all"]
    
    print(erase_all)
    #print(consent)
    id1 = datas["user_anip"]
    id2 = datas["id_enterprise"]
    id = concatenate_strings(id1, id2)
    consent_deleter = ConsentManagerD(datas)
    consent_to_delete = consent_deleter.erase_consent()
    print("consent to delete", consent_to_delete)
    data_from_redis = r.get(id)
    consent_element = create_erase_structure(datas["attrs"])
    consent_element["erase_all"] = datas["erase_all"]
    result = {}
    if data_from_redis is not None:
    	data = update_dict(json.loads(data_from_redis), consent_element)
    	result = register_data_redis.apply_async(
    	args=[json.loads(data_from_redis), datas, id])
    	result_without_key = result.get()
    	
    	
    else:	
    	#data_dict = json.loads(data_from_api)
    	result = register_data_redis.apply_async(
    	args=[data_from_api, datas, id])
    	result_without_key = result.get()
    	result_with_key = result_without_key["id"] = id
    	print("this is result",result)
    
    rabbitmq = RabbitMQ(appli)
    rabbitmq.publish_message("delete_ds_data","delete_ds_data", **result.get())

    
           
    #add_erase_data_to_redis(data_dict, id)
    return jsonify(consent_to_delete), 200

@app_views.route('/redis_data', methods=['GET'])
@cross_origin()
def get_consent():
    r = RedisDBManager()
    id =  str(request.get_json()["id"])
    print(type(id))
    data = r.get(id)
    print(data)
    return jsonify(data), 200



   
    
def concatenate_strings(str1, str2):
  """
  Concatenates two strings.

  Args:
    str1: The first string.
    str2: The second string.

  Returns:
    The concatenated string.
  """
  return f"{str1}_{str2}"
