from datetime import timedelta, datetime
from flask import Flask, make_response, jsonify, redirect, request
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import NoAuthorizationError, JWTDecodeError
from jwt.exceptions import ExpiredSignatureError
from models import storage
from api.v1.endpoints import app_views
from models.enterprise import Enterprise
import os
import secrets

from os import getenv

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
#app.config['SECRET_KEY'] = secrets.token_hex(16)
#app.config['FLASK_JWT_SECRET_KEY'] = secrets.token_hex(16)
app.config['JWT_SECRET_KEY'] = secrets.token_hex(16)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
#app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=5)

#app.config['JWT_ACCESS_TOKEN_EXPIRES'] = None  # Expires in 24 hour

 
#FLASK_JWT_SECRET_KEY= secrets.token_hex(12)
jwt = JWTManager(app)
cors = CORS(app, resources={r"api/v1/*": {"origins": "*"}})
app.register_blueprint(app_views)


@jwt.additional_claims_loader
def add_claims_to_access_token(identity):
    # identity is the result of identity() function
    # You can add any additional claims based on the identity
    # For example, you might fetch additional user information from a database
    user_info = {'role': 'admin'}  # Additional claim: 'role'
    return user_info

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]  # Assuming the 'sub' claim in the JWT represents the user identity
    # Lookup the user based on the identity
    enterprise = storage.find_by(Enterprise, **{"client_id": identity})
    return enterprise

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "Token has expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    return jsonify({"msg": "Invalid token", "status": 401}), 401

#@jwt.unauthorized_loader
#@cross_origin()
#def unauthorized_callback(callback_error):
    #return jsonify({"msg": "acès non autorisé", "status": 401}), 401

@jwt.unauthorized_loader
@cross_origin()
def unauthorized_callback(callback_error):
    error_message = "Accès non autorisé"
    status_code = 401

    # Check the type of error
    if isinstance(callback_error, ExpiredSignatureError):
        error_message = "Le jeton a expiré, veuillez vous reconnecter."
        status_code = 401  # or any other appropriate status code
    elif isinstance(callback_error, (NoAuthorizationError, JWTDecodeError)):
        error_message = "Le jeton est invalide ou manquant."
        status_code = 401  # or any other appropriate status code

    return jsonify({"msg": error_message, "status": status_code}), status_code

#@jwt.token_in_blocklist_loader
#def check_if_token_revoked(jwt_header, jwt_data):
    #jti = jwt_data["jti"]
    #jwti = storage.find_by(TokenBlockList, **{"jti": jti})
    #return "jwti is not None"



@app.teardown_appcontext
def teardown(self):
    """ Calls storage close"""
    storage.close()


@app.errorhandler(404)
def pageNotFound(error):
    """Error handling for 404"""
    return make_response(jsonify({"error": "Not found"}), 404)


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 5000
    #host = getenv('AUT_API_HOST', default='0.0.0.0')
    #port = getenv('AUT_API_PORT', default=3000)
    app.run(host=host, port=port, threaded=True)
