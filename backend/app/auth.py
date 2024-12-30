from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, db
import boto3
import os
import hmac
import hashlib
import base64
import jwt
from jwt import PyJWKClient, ExpiredSignatureError, InvalidAudienceError, InvalidTokenError
import datetime

auth_bp = Blueprint('auth', __name__)

# AWS Cognito Client
cognito_client = boto3.client('cognito-idp', region_name=os.getenv('AWS_REGION'))

# ✅ Validate Environment Variables
required_env_vars = ['AWS_COGNITO_CLIENT_ID', 'AWS_COGNITO_CLIENT_SECRET', 'AWS_REGION', 'JWT_DECODE_ISSUER']
for var in required_env_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")


# ✅ Calculate SECRET_HASH for AWS Cognito Authentication
def calculate_secret_hash(username, client_id, client_secret):
    message = username + client_id
    dig = hmac.new(
        client_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()


# ✅ User Registration (Local Authentication)
@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"message": "Username and password are required"}), 400

    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({"message": "User already exists"}), 400

    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_password, role='user')
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 201


# ✅ User Login (Local Authentication)
@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"message": "Username and password are required"}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=datetime.timedelta(hours=1)
        )
        return jsonify({"access_token": access_token}), 200
    return jsonify({"message": "Invalid credentials"}), 401


# ✅ AWS Cognito Login
@auth_bp.route('/api/aws-login', methods=['POST'])
def aws_login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"message": "Username and password are required"}), 400

    try:
        secret_hash = calculate_secret_hash(
            data['username'],
            os.getenv('AWS_COGNITO_CLIENT_ID'),
            os.getenv('AWS_COGNITO_CLIENT_SECRET')
        )

        response = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': data['username'],
                'PASSWORD': data['password'],
                'SECRET_HASH': secret_hash
            },
            ClientId=os.getenv('AWS_COGNITO_CLIENT_ID')
        )

        id_token = response['AuthenticationResult']['IdToken']
        access_token = response['AuthenticationResult']['AccessToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']

        return jsonify({
            "id_token": id_token,
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200

    except cognito_client.exceptions.NotAuthorizedException:
        return jsonify({"message": "Invalid AWS Cognito credentials"}), 401
    except cognito_client.exceptions.UserNotFoundException:
        return jsonify({"message": "User not found in AWS Cognito"}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# ✅ AWS Protected Route Example (AWS Cognito)
@auth_bp.route('/api/aws-protected', methods=['GET'])
def aws_protected():
    token = request.headers.get('Authorization')
    if not token or "Bearer " not in token:
        return jsonify({"message": "Missing or malformed Authorization Header"}), 401
    
    token = token.split("Bearer ")[1]
    try:
        jwk_client = PyJWKClient("https://cognito-idp.us-east-1.amazonaws.com/us-east-1_hSlxLW1DX/.well-known/jwks.json")
        signing_key = jwk_client.get_signing_key_from_jwt(token).key

        decoded_token = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=os.getenv('JWT_DECODE_ISSUER'),
            audience=os.getenv('AWS_COGNITO_CLIENT_ID')
        )

        if decoded_token.get("token_use") != "id":
            raise jwt.InvalidTokenError("Token is not an ID Token")

        username = decoded_token.get("cognito:username") or decoded_token.get("username") or "Unknown User"
        return jsonify({"message": f"Hello, AWS Cognito user {username}!"}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidAudienceError:
        return jsonify({"message": "Invalid token audience"}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({"message": f"Invalid token: {str(e)}"}), 401


# ✅ Refresh Token Route (AWS Cognito)
@auth_bp.route('/api/aws-refresh', methods=['POST'])
def aws_refresh():
    data = request.get_json()
    if not data or 'refresh_token' not in data:
        return jsonify({"message": "Refresh token is required"}), 400

    try:
        secret_hash = calculate_secret_hash(
            os.getenv('AWS_COGNITO_CLIENT_ID'),
            os.getenv('AWS_COGNITO_CLIENT_ID'),
            os.getenv('AWS_COGNITO_CLIENT_SECRET')
        )

        response = cognito_client.initiate_auth(
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': data['refresh_token'],
                'SECRET_HASH': secret_hash
            },
            ClientId=os.getenv('AWS_COGNITO_CLIENT_ID')
        )

        new_access_token = response['AuthenticationResult']['AccessToken']
        new_id_token = response['AuthenticationResult']['IdToken']

        return jsonify({
            "access_token": new_access_token,
            "id_token": new_id_token
        }), 200

    except cognito_client.exceptions.NotAuthorizedException:
        return jsonify({"message": "Invalid Refresh Token"}), 401
    except Exception as e:
        return jsonify({"message": str(e)}), 500
