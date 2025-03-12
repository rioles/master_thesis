from typing import Any, Dict, TypeVar, List
from bcrypt import hashpw, gensalt, checkpw
from models import storage
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError
import secrets
import string
import uuid
import re
import json

T = TypeVar('T')

class EnterpriseService:
    def add_object(
        self,
        current_class: T,
        **object_meta_data: Dict[str, str]
    ) -> T:
        """
        Registers an object in the database.

        Args:
            current_class: The class of the user to register.
            object_meta_data: A dictionary of properties of the user to register.

        Returns:
            The user object, if the user was registered successfully.

        Raises:
            Exception: If the object_meta_data dictionary is empty or if registration fails.
        """
        if not object_meta_data:
            raise Exception("object_meta_data cannot be empty.")

        try:
            client_secret = generate_client_secret()
            client_id = generate_client_id(object_meta_data["enterprise_name"])
            object_meta_data["client_secret"] = _hash_password(client_secret).decode('utf-8')
            object_meta_data["client_id"] = client_id 

            # Create an instance of the current class with the metadata
            enterprise = current_class(**object_meta_data)  # Use ** to unpack the dictionary
            enterprise.save()  # Save the enterprise object to the database

            # Generate the JSON file and return its name
            file_name = generate_client_json(client_id, client_secret, object_meta_data["enterprise_name"])
            return file_name, enterprise  # Return the file name and the enterprise object
        except Exception as e:
            raise Exception(f"An error occurred while registering the enterprise: {e}")
    
    def get_user_log(
        self,
        current_class: T,
        **object_meta_data: Dict[str, str]
    ) -> T:
        enterprise = storage.find_by(current_class, **{"client_id": object_meta_data["client_id"]})
        print("user", enterprise)
        if enterprise is not None and valid_login(enterprise, object_meta_data["client_secret"]):
            return enterprise.to_dict()
        else:
            return None
            
    def find_user_by_id(
        self,
        current_class: T,
        **object_meta_data: Dict[str, str]
    ) -> T:
        enterprise = storage.find_by(current_class, **{"client_id": object_meta_data["client_id"]})
        print("user", enterprise)
        if enterprise is not None:
            return enterprise.to_dict()
        else:
            return None

def generate_client_secret(length=32):
    characters = string.ascii_letters + string.digits
    client_secret = ''.join(secrets.choice(characters) for _ in range(length))
    return client_secret

def generate_client_id(client_name):
    sanitized_client_name = re.sub(r'[^a-zA-Z0-9]+', '-', client_name).strip('-')
    sanitized_client_name = sanitized_client_name.rstrip('-')
    unique_id = str(uuid.uuid4()).replace('-', '') 
    client_id = f"{sanitized_client_name}-{unique_id}"
    return client_id

def generate_client_json(client_id, client_secret, enterprise_name):
    client_email = f"{enterprise_name}@consent.com"
    type = "service_account"
    
    # Create the dictionary with the provided information
    client_info = {
        "client_secret": client_secret,
        "client_id": client_id,
        "client_email": client_email,
        "type": type,
    }

    # Define the JSON file name
    json_file_name = f"{client_id}.json"

    # Write the dictionary to a JSON file
    with open(json_file_name, 'w') as json_file:
        json.dump(client_info, json_file, indent=4)

    return json_file_name

def _hash_password(password: str) -> bytes:
    """ Hash password """
    return hashpw(password.encode(), gensalt())

def valid_login(enterprise, password: str) -> bool:
    """ Login validation """
    try:
        hashed_password = enterprise.client_secret
        return checkpw(password.encode(), hashed_password.encode('utf-8'))
    except (NoResultFound, InvalidRequestError):
        return False

