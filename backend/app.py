import os
from backend import create_app
from backend.config.settings import FLASK_PORT, DEBUG
from backend.utils.logging import logger

# Create the Flask application
app = create_app()
# --- Global In-Memory Stores ---
# Portfolio data is now managed by the Portfolio model in backend/models/portfolio.py
# --- Asset Type Constants (ensure these match frontend if hardcoded there) ---
# These should match the values used in the frontend's AddAssetForm
ASSET_TYPE_INDIAN_STOCK = "Indian Stock"
ASSET_TYPE_US_STOCK = "US Stock"
ASSET_TYPE_CRYPTO = "Crypto"

# Symbol loading is now handled by the SymbolService in backend/services/symbol_service.py

# API endpoints are now defined in backend/routes/

# --- Main guard for running with 'python app.py' for local development ---
if __name__ == '__main__':
    # When running directly, Flask's dev server might reload, re-running module-level code.
    # For production with Gunicorn, module-level code runs once per worker process initialization.
    logger.info(f"Starting Flask development server on port {FLASK_PORT}")
    # Note: Symbol loading is now handled within create_app, specifically by initializing SymbolService.
    app.run(debug=DEBUG, host='0.0.0.0', port=FLASK_PORT)
