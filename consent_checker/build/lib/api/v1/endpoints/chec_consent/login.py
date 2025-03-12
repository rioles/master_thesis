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
from flask_jwt_extended import create_access_token, jwt_required, create_refresh_token, get_jwt_identity,get_jwt,decode_token
from datetime import timedelta

@app_views.route('/login', methods=['POST'], strict_slashes=False)
@cross_origin()
def login_handler():
    """create a new category"""
    expires = timedelta(hours=1)
    if not request.get_json():
        return make_response(jsonify(
            {'status': '401', 'message': 'The request data is empty'}), 400)
    enter: EnterpriseService = EnterpriseService()    
    enterprise = enter.get_user_log(Enterprise, **request.get_json())
    print("ennte", enterprise)
    if enterprise is not None:
        access_token = create_access_token(identity=enterprise["client_id"], expires_delta=expires)
        refresh_token = create_refresh_token(identity=enterprise["client_id"])
        decoded_token = decode_token(access_token)
        response_data = {'access_token': access_token, 'refresh_token': refresh_token}
        return make_response(jsonify(response_data), 200)
    else:
        return make_response(jsonify({'status': '404', 'message': f'no user with client_id {request.get_json()["email"]} or password  exists'}), 400)
