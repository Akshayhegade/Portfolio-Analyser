from flask import Flask
from flask_cors import CORS

from backend.config.settings import DEBUG, FLASK_PORT
from backend.utils.logging import logger
from backend.routes.assets import assets_bp
from backend.routes.symbols import symbols_bp
from backend.routes.prices import price_routes
from backend.services import symbol_service


def create_app():
    """
    Create and configure the Flask application
    """
    app = Flask(__name__)
    
    # Enable CORS for all routes (fine for development)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(assets_bp, url_prefix='/assets')
    app.register_blueprint(symbols_bp)
    app.register_blueprint(price_routes)
    
    # Add a simple root route
    @app.route('/')
    def hello_world():
        return 'Hello from the Portfolio Analyser Backend!'
    
    # Load symbol data on startup
    with app.app_context():
        symbol_service.load_crypto_symbols()
        symbol_service.load_indian_stock_symbols()
        symbol_service.load_us_stock_symbols()
    
    return app
