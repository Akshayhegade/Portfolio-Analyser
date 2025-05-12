import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Flask settings
FLASK_PORT = int(os.environ.get('FLASK_RUN_PORT', 5000))
DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')

# Asset types
ASSET_TYPE_INDIAN_STOCK = "Indian Stock"
ASSET_TYPE_US_STOCK = "US Stock"
ASSET_TYPE_CRYPTO = "Crypto"

# API endpoints
COINGECKO_API_URL = 'https://api.coingecko.com/api/v3'
YHOO_FINANCE_API_URL = 'https://query1.finance.yahoo.com/v8/finance/chart'
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY', '')

# Cache settings
PRICE_CACHE_DURATION = 300  # seconds (5 minutes)

# Request timeouts
REQUEST_TIMEOUT = 15  # seconds
