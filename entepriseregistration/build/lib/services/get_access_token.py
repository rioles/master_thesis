import os
import requests
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
from flask_jwt_extended import (
    create_access_token, jwt_required, create_refresh_token, 
    get_jwt_identity, get_jwt, decode_token, verify_jwt_in_request
)
from services.enterprise_service import EnterpriseService
from models.enterprise import Enterprise


class AuthService:
    # Class-level constant for the login URL
    LOGIN_URL = "https://e37e-41-85-163-62.ngrok-free.app/api/v1/login"  
    REDIRECT_URL = "https://e37e-41-85-163-62.ngrok-free.app/api/v1/consent_data"
    CHECK_ENTERPRISE_URL = "https://e37e-41-85-163-62.ngrok-free.app/api/v1/show"

    def __init__(self):
        # Retrieve client ID and client secret from environment variables
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        if not self.client_id or not self.client_secret:
            raise ValueError("Client ID and Client Secret must be set in environment variables")

    def get_access_token(self) -> Optional[str]:
        """
        Obtain an access token using the provided client credentials.
        Returns:
            Optional[str]: The access token if successful, or None if failed.
        """
        try:
            # POST request payload
            payload = {
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }

            # Send POST request to the login URL
            response = requests.post(self.LOGIN_URL, json=payload, headers={'Accept': 'application/json'})

            # If the response is successful (status code 200)
            if response.status_code == 200:
                # Extract the access token from the response
                access_token = response.json().get('access_token')
                return access_token
            else:
                # Print error details if unsuccessful
                print(f"Error response status code: {response.status_code}")
                print(f"Error response content: {response.text}")
                return None
        except Exception as e:
            # Catch and print any exceptions that occur
            print(f"Error occurred while fetching access token: {e}")
            return None

    def send_consent_request(self):
        consent_and_consent_purposes = {
            "name": ["identification", "personalization"],
            "age": ["age restrictions", "targeted marketing"],
            "telephone_number": ["contact", "verification"],
            "email_address": ["communication", "account creation", "password recovery"]
        }

        token = self.get_access_token()
        if not token:
            return {"error": "Unable to retrieve access token"}

        # Add the token to the headers
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        # Send GET request with headers
        response = requests.get(self.CHECK_ENTERPRISE_URL, json={}, headers=headers)
        if response.status_code == 200:
        	decode_token = response.json().get("decode")
        	print(decode_token)
        else:
        	print(f"Error response status code: {response.status_code}")
        	
        
        # Retrieve enterprise data
        enter: EnterpriseService = EnterpriseService()
        enterprise_data = enter.find_user_by_id(Enterprise, **{"client_id": decode_token["sub"]})
        print(enterprise_data)
        enterprise_datas = {"client_name": enterprise_data["enterprise_name"],"client_id":enterprise_data["client_id"]}

        if enterprise_data is not None:
            return {"client": enterprise_datas, "consent_need": consent_and_consent_purposes}
            
        return None


# Example usage
if __name__ == "__main__":
    a = AuthService()

    # Example of accessing environment variables
    print("CLIENT_ID:", os.environ.get('CLIENT_ID'))
    print("Access Token:", a.send_consent_request())

