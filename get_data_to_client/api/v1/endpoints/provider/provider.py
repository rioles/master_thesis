import os
import requests
from api.v1.endpoints import app_views
from flask_cors import cross_origin
from datetime import timedelta, datetime
from flask import abort, jsonify, make_response, request
from services.paginator import Paginator
from flask import send_file
from datetime import datetime
from flask_jwt_extended import (
    create_access_token, jwt_required, create_refresh_token, get_jwt_identity, 
    get_jwt, decode_token, verify_jwt_in_request
)
import fastavro
import json
from dotenv import load_dotenv
load_dotenv()


# logging.basicConfig(filename='/tmp/userlogin.log', level=logging.DEBUG, 
# format='%(asctime)s - %(levelname)s - %(message)s')

@app_views.route('/provider', methods=['GET'], strict_slashes=False)
@cross_origin()
def get_data():
    """Create a new category"""
    
    return "response", 201
