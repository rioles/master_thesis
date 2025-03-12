from api.v1.app import jwt
from flask_jwt_extended import decode_token
from flask import abort, jsonify, make_response, request
from flask import current_app


def verify(token: str):
    if not token:
        return jsonify({"msg": "Missing token"}), 400

    try:
        with current_app.app_context():  # Create application context
            # Decode the token
            decoded = decode_token(token)
            return {"msg": "Token is valid", "decoded": decoded}
    except Exception as e:
        return {"msg": str(e)}

# Example usage

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyODQ3NTIzOSwianRpIjoiMmMzMmRiZWYtNjVjOS00ZGFiLWE2MDQtNmVmZWFmZDNjOWRhIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Im96YW5hLTgyZGYwNmFhMTMyODQ3Yjg5NzJjYzBkODNjNTg5NDExIiwibmJmIjoxNzI4NDc1MjM5LCJjc3JmIjoiZWI1ZWE1NzgtYWQxZi00Nzk5LWE3NTItNjcyOTMwNTBjZmVjIiwiZXhwIjoxNzI4NDc4ODM5LCJyb2xlIjoiYWRtaW4ifQ.qAvNVu2CPJpLRHh2QyrIkxUcpD9hJtta74s5WmH2p9o"
#secret_key = "<your_secret_key>"
#decodedss = decode_token(token)
#print("erty", decodedss)
token_data = verify(token)
print("ooo", token_data)
if token_data:
    print(token_data)
    print("Token is valid")
else:
    print("Token is invalid")

