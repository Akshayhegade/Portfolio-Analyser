from flask import Flask
from flask_cors import CORS
import os

from backend.config.settings import DEBUG, FLASK_PORT
from backend.utils.logging import logger
from backend.routes.assets import assets_bp
from backend.routes.symbols import symbols_bp
from backend.routes.prices import price_routes
from backend.services import symbol_service
from backend.models import db


def create_app(config_override=None):
    """
    Create and configure the Flask application
    """
    app = Flask(__name__)

    # Default configuration
    # Use a file-based SQLite database in the instance folder
    app.instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    os.makedirs(app.instance_path, exist_ok=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(app.instance_path, "portfolio_analyser.db")}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = False # Default to not testing

    # Override with provided config
    if config_override:
        app.config.update(config_override)
    
    # Configure SQLAlchemy
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') # Moved up
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Moved up
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Disable strict slashes to prevent redirects that break CORS preflight
    app.url_map.strict_slashes = False
    
    # Enable CORS for all routes
    CORS(app, 
         origins="*", 
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "Accept"],
         supports_credentials=False,
         automatic_options=True,
         send_wildcard=True)
    
    # Register blueprints
    app.register_blueprint(assets_bp, url_prefix='/assets')
    app.register_blueprint(symbols_bp)
    app.register_blueprint(price_routes)
    
    # Add a simple root route
    @app.route('/')
    def hello_world():
        return 'Hello from the Portfolio Analyser Backend!'
    
    # Load symbol data and initialize database on startup
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Load symbol data
        symbol_service.load_crypto_symbols()
        symbol_service.load_indian_stock_symbols()
        symbol_service.load_us_stock_symbols()
    
    return app
