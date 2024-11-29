import os
import requests
from api.v1.endpoints import app_views
from flask_cors import cross_origin
from datetime import timedelta, datetime
from flask import abort, jsonify, make_response, request
from models import storage
from services.paginator import Paginator
from flask import send_file
from datetime import datetime
from models.enterprise import Enterprise
from services.enterprise_service import EnterpriseService
from flask_jwt_extended import (
    create_access_token, jwt_required, create_refresh_token, get_jwt_identity, 
    get_jwt, decode_token, verify_jwt_in_request
)
from services.get_access_token import AuthService
from avro_schemas_registry.schema_registry_client import SchemaClient
from avro_schemas_registry.consent_data_producer import AvroProducerClass, load_avro_schema
from avro_schemas_registry.convert_data_to_avro import  generate_schema_from_dict
import fastavro
import json
from dotenv import load_dotenv
load_dotenv()

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
    
    
@app_views.route('/verify', methods=['GET'])
@cross_origin()
def verify_token():
    # Extract the token from the request
    a = AuthService()
    data = request.get_json()
    token = a.get_access_token()
    tokens = data.get('token')
    # print(token)

    if not token:
        return jsonify({"msg": "Missing token"}), 400

    try:
        # Decode the token
        verify_jwt_in_request(optional=False)
        decodedss = get_jwt()
        decoded = decode_token(token)
        print(decoded)
        print("this is decooo", decodedss)
        return jsonify({"msg": "Token is valid", "decoded": decoded}), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 401
        
        
@app_views.route('/show', methods=['GET'])
@jwt_required()
@cross_origin()
def verify_tokenss():
    token = request.headers.get('Authorization').split()[1]
    decoded = decode_token(token)
    return jsonify({"token": token, "decode": decoded}), 200


@app_views.route('/consent_data', methods=['GET'])
@cross_origin()    
def user_consent_data():
    auth_service: AuthService = AuthService()
    consent = auth_service.send_consent_request()
    return jsonify(consent), 200
    

@app_views.route('/consnt_data', methods=['POST'])
@cross_origin()    
def data_get_from_webhook():
    data = request.get_json()
    print(data)
    return jsonify({"data":"received"}), 200


   
@app_views.route('/user_identifier', methods=['POST'])
@cross_origin()    
def user_consent_datas():
    auth_service: AuthService = AuthService()
    consent = auth_service.send_consent_request()
    print(consent)
    data = request.get_json()
    anip_data = data.pop('user_anip')
    #schema_file = os.getenv('schema_file')
    #print("file",schema_file)
    expiration_date = data.pop('expiration_date')
    #schema_dict = load_avro_schema(schema_file)
    schema_url = os.getenv('schema_url')
    topic_name = os.getenv('topic_name')
    subject_name = os.getenv('subject_name')
    bootstrap_server = os.getenv('bootstrap_server')
    all_data = {"consent":consent["consent_need"], "client": consent["client"], "consent_grant":data, "user_anip":anip_data, "consent_grant_date": datetime.utcnow(), "expiration_date":expiration_date}
    schema_dict = generate_schema_from_dict(all_data, "consent_data_value")
    print("this is schema_dict",schema_dict)
    schema_json_str = json.dumps(schema_dict)
    print("this is schema_json",schema_json_str)
    schema_type = "AVRO"
    client = SchemaClient(schema_url, subject_name, schema_dict, schema_type)
    
    #print(client)
    #client.register_schema()
    #client.set_compatibility("FORWARD")
    schema = client.get_schema_str()
    print(schema)
    producer = AvroProducerClass(bootstrap_server, topic_name, client.schema_client, schema)
    producer.send_message(all_data, consent["client"]["client_id"])
    producer.commit()
    return jsonify(all_data), 200

