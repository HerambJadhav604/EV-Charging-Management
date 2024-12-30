import hmac
import hashlib
import base64

def calculate_secret_hash(username, client_id, client_secret):
    """
    Calculate the SECRET_HASH for AWS Cognito authentication.
    """
    message = username + client_id
    dig = hmac.new(
        client_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()

# Replace these values with your AWS Cognito details
USERNAME = "awsuser"
CLIENT_ID = "1lb13agkgd3i75q4gru809njuj"
CLIENT_SECRET = "1l7ie7eaevf2pq1k1nus9c860qt9ce601phl84akvd8v2jjqn646"

print("SECRET_HASH:", calculate_secret_hash(USERNAME, CLIENT_ID, CLIENT_SECRET))

