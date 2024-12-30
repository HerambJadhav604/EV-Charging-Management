from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import boto3

# Load environment variables
load_dotenv()

# Initialize database
db = SQLAlchemy()
migrate = Migrate() 

def create_app():
    app = Flask(__name__)
    
    # Load configuration from environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///ev_charging.db')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
    
    # AWS Cognito Configuration
    app.config['AWS_COGNITO_USER_POOL_ID'] = os.getenv('AWS_COGNITO_USER_POOL_ID')
    app.config['AWS_COGNITO_CLIENT_ID'] = os.getenv('AWS_COGNITO_CLIENT_ID')
    app.config['AWS_REGION'] = os.getenv('AWS_REGION')

    # Initialize database and JWT manager
    db.init_app(app)
    JWTManager(app)
    migrate.init_app(app, db) 
    
    # Initialize AWS Cognito Client
    try:
        app.cognito_client = boto3.client(
            'cognito-idp',
            region_name=app.config['AWS_REGION']
        )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize AWS Cognito: {e}")
    
    # Import and register blueprints
    from .auth import auth_bp
    from .routes.ev_owner import ev_owner_bp
    from .routes.energy_provider import energy_provider_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(ev_owner_bp)
    app.register_blueprint(energy_provider_bp)

    # Database initialization
    with app.app_context():
        db.create_all()
    
    return app
