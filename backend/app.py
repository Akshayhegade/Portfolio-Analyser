import os
import uuid
import logging
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app) # Enable CORS for all routes, fine for development

# --- Global In-Memory Stores ---
portfolio = [
    # 10 Indian Stocks - Total approx 5,000,000 INR
    {"id": str(uuid.uuid4()), "symbol": "RELIANCE.NS", "asset_type": "Indian Stock", "purchase_price": 2800, "quantity": 200, "purchase_date": "2023-01-10"}, # 560,000
    {"id": str(uuid.uuid4()), "symbol": "TCS.NS", "asset_type": "Indian Stock", "purchase_price": 3500, "quantity": 150, "purchase_date": "2023-02-15"},      # 525,000
    {"id": str(uuid.uuid4()), "symbol": "HDFCBANK.NS", "asset_type": "Indian Stock", "purchase_price": 1600, "quantity": 300, "purchase_date": "2023-03-20"}, # 480,000
    {"id": str(uuid.uuid4()), "symbol": "INFY.NS", "asset_type": "Indian Stock", "purchase_price": 1500, "quantity": 350, "purchase_date": "2023-04-05"},     # 525,000
    {"id": str(uuid.uuid4()), "symbol": "ICICIBANK.NS", "asset_type": "Indian Stock", "purchase_price": 900, "quantity": 550, "purchase_date": "2023-05-12"},  # 495,000
    {"id": str(uuid.uuid4()), "symbol": "SBIN.NS", "asset_type": "Indian Stock", "purchase_price": 600, "quantity": 800, "purchase_date": "2023-06-18"},      # 480,000
    {"id": str(uuid.uuid4()), "symbol": "KOTAKBANK.NS", "asset_type": "Indian Stock", "purchase_price": 1800, "quantity": 270, "purchase_date": "2023-07-22"},# 486,000
    {"id": str(uuid.uuid4()), "symbol": "BHARTIARTL.NS", "asset_type": "Indian Stock", "purchase_price": 850, "quantity": 580, "purchase_date": "2023-08-30"},# 493,000
    {"id": str(uuid.uuid4()), "symbol": "LT.NS", "asset_type": "Indian Stock", "purchase_price": 2200, "quantity": 220, "purchase_date": "2023-09-05"},        # 484,000
    {"id": str(uuid.uuid4()), "symbol": "HINDUNILVR.NS", "asset_type": "Indian Stock", "purchase_price": 2500, "quantity": 190, "purchase_date": "2023-10-10"},# 475,000
                                                                                                                                                # Total: 4,903,000

    # 5 US Stocks - Total approx 7,000,000 INR
    # Assuming an arbitrary USD to INR conversion for purchase price, e.g., 1 USD = 80 INR for these examples
    # For AAPL, if price is $170, then 170*80 = 13600 INR
    {"id": str(uuid.uuid4()), "symbol": "AAPL", "asset_type": "US Stock", "purchase_price": 14000, "quantity": 100, "purchase_date": "2023-01-20"}, # 1,400,000
    {"id": str(uuid.uuid4()), "symbol": "MSFT", "asset_type": "US Stock", "purchase_price": 24000, "quantity": 60, "purchase_date": "2023-02-25"},  # 1,440,000
    {"id": str(uuid.uuid4()), "symbol": "GOOGL", "asset_type": "US Stock", "purchase_price": 10000, "quantity": 130, "purchase_date": "2023-03-15"}, # 1,300,000
    {"id": str(uuid.uuid4()), "symbol": "AMZN", "asset_type": "US Stock", "purchase_price": 9000, "quantity": 160, "purchase_date": "2023-04-22"},   # 1,440,000
    {"id": str(uuid.uuid4()), "symbol": "TSLA", "asset_type": "US Stock", "purchase_price": 15000, "quantity": 100, "purchase_date": "2023-05-30"}, # 1,500,000
                                                                                                                                                # Total: 7,080,000

    # 10 Cryptocurrencies - Total approx 2,500,000 INR
    {"id": str(uuid.uuid4()), "symbol": "BTC", "asset_type": "Crypto", "purchase_price": 2200000, "quantity": 0.1, "purchase_date": "2023-01-05"},  # 220,000
    {"id": str(uuid.uuid4()), "symbol": "ETH", "asset_type": "Crypto", "purchase_price": 150000, "quantity": 1.5, "purchase_date": "2023-02-08"},   # 225,000
    {"id": str(uuid.uuid4()), "symbol": "BNB", "asset_type": "Crypto", "purchase_price": 25000, "quantity": 10, "purchase_date": "2023-03-10"},    # 250,000
    {"id": str(uuid.uuid4()), "symbol": "XRP", "asset_type": "Crypto", "purchase_price": 40, "quantity": 6000, "purchase_date": "2023-04-15"},     # 240,000
    {"id": str(uuid.uuid4()), "symbol": "ADA", "asset_type": "Crypto", "purchase_price": 30, "quantity": 8000, "purchase_date": "2023-05-20"},     # 240,000
    {"id": str(uuid.uuid4()), "symbol": "SOL", "asset_type": "Crypto", "purchase_price": 1800, "quantity": 140, "purchase_date": "2023-06-25"},    # 252,000
    {"id": str(uuid.uuid4()), "symbol": "DOGE", "asset_type": "Crypto", "purchase_price": 6, "quantity": 40000, "purchase_date": "2023-07-01"},    # 240,000
    {"id": str(uuid.uuid4()), "symbol": "DOT", "asset_type": "Crypto", "purchase_price": 500, "quantity": 500, "purchase_date": "2023-08-05"},     # 250,000
    {"id": str(uuid.uuid4()), "symbol": "SHIB", "asset_type": "Crypto", "purchase_price": 0.0007, "quantity": 350000000, "purchase_date": "2023-09-10"},#245,000
    {"id": str(uuid.uuid4()), "symbol": "MATIC", "asset_type": "Crypto", "purchase_price": 70, "quantity": 3500, "purchase_date": "2023-10-15"}   # 245,000
                                                                                                                                                # Total: 2,407,000
]
CRYPTO_SYMBOLS = []
INDIAN_STOCK_SYMBOLS = []
US_STOCK_SYMBOLS = []

# --- Asset Type Constants (ensure these match frontend if hardcoded there) ---
# These should match the values used in the frontend's AddAssetForm
ASSET_TYPE_INDIAN_STOCK = "Indian Stock"
ASSET_TYPE_US_STOCK = "US Stock"
ASSET_TYPE_CRYPTO = "Crypto"

# --- Symbol Loading Functions ---
def load_crypto_symbols():
    global CRYPTO_SYMBOLS
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 100, # Top 100
        'page': 1,
        'sparkline': 'false',
        'price_change_percentage': 'false' # Don't need this extra data
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status() # Raise an HTTPError for bad responses (4XX or 5XX)
        data = response.json()
        # Store as a list of dicts: { id (for key), symbol, name }
        CRYPTO_SYMBOLS = [
            {'id': coin['id'], 'symbol': coin['symbol'].upper(), 'name': coin['name']}
            for coin in data
        ]
        logging.info(f"Successfully loaded {len(CRYPTO_SYMBOLS)} crypto symbols from CoinGecko.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching crypto symbols from CoinGecko: {e}")
        CRYPTO_SYMBOLS = [] # Ensure it's an empty list on error
    except Exception as e:
        logging.error(f"An unexpected error occurred while processing crypto symbols: {e}")
        CRYPTO_SYMBOLS = []

def load_indian_stock_symbols():
    global INDIAN_STOCK_SYMBOLS
    # TODO: Implement loading from a reliable source (e.g., a maintained CSV, an API)
    # Structure: {'symbol': 'INFY.NS', 'name': 'Infosys Limited'}
    INDIAN_STOCK_SYMBOLS = [
        {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries Ltd.'},
        {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services Ltd.'},
        {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank Ltd.'},
        {'symbol': 'INFY.NS', 'name': 'Infosys Ltd.'},
        {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank Ltd.'},
        # Add more representative Indian stocks if desired
    ]
    logging.info(f"Loaded {len(INDIAN_STOCK_SYMBOLS)} Indian stock symbols (placeholder).")

def load_us_stock_symbols():
    global US_STOCK_SYMBOLS
    # TODO: Implement loading from a reliable source (e.g., NASDAQ/NYSE listings CSV, an API)
    # Structure: {'symbol': 'MSFT', 'name': 'Microsoft Corporation'}
    US_STOCK_SYMBOLS = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.'},
        {'symbol': 'MSFT', 'name': 'Microsoft Corporation'},
        {'symbol': 'GOOGL', 'name': 'Alphabet Inc. (Class A)'},
        {'symbol': 'AMZN', 'name': 'Amazon.com, Inc.'},
        {'symbol': 'TSLA', 'name': 'Tesla, Inc.'},
        # Add more representative US stocks if desired
    ]
    logging.info(f"Loaded {len(US_STOCK_SYMBOLS)} US stock symbols (placeholder).")

# --- Load all symbols when the application module is loaded by Python ---
# This ensures symbols are loaded when Gunicorn/Flask dev server starts a worker.
load_crypto_symbols()
load_indian_stock_symbols()
load_us_stock_symbols()

# --- API Endpoints ---
@app.route('/')
def hello_world():
    return 'Hello from the Portfolio Analyser Backend!'

@app.route('/assets', methods=['POST'])
def add_asset():
    data = request.get_json()
    required_fields = ["symbol", "asset_type", "purchase_price", "quantity", "purchase_date"]
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Validate asset_type (ensure it matches the constants)
    if data['asset_type'] not in [ASSET_TYPE_INDIAN_STOCK, ASSET_TYPE_US_STOCK, ASSET_TYPE_CRYPTO]:
        return jsonify({"error": f"Invalid asset_type: {data['asset_type']}. Expected one of: {ASSET_TYPE_INDIAN_STOCK}, {ASSET_TYPE_US_STOCK}, {ASSET_TYPE_CRYPTO}"}), 400

    try:
        purchase_price = float(data["purchase_price"])
        quantity = float(data["quantity"])
        if purchase_price <= 0 or quantity <= 0:
            return jsonify({"error": "Purchase price and quantity must be positive numbers"}), 400
    except ValueError:
        return jsonify({"error": "Purchase price and quantity must be valid numbers"}), 400
    
    # TODO: Add validation for purchase_date format (e.g., YYYY-MM-DD from date picker)

    new_asset = {
        "id": str(uuid.uuid4()),
        "symbol": data["symbol"].upper(), # Standardize symbol to uppercase
        "asset_type": data["asset_type"],
        "purchase_price": purchase_price,
        "quantity": quantity,
        "purchase_date": data["purchase_date"]
    }
    portfolio.append(new_asset)
    logging.info(f"Added asset: {new_asset['symbol']}")
    return jsonify(new_asset), 201

@app.route('/assets', methods=['GET'])
def get_assets():
    return jsonify(portfolio)

@app.route('/assets/<string:asset_id>', methods=['PUT'])
def update_asset(asset_id):
    global portfolio
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required_fields = ["symbol", "asset_type", "purchase_price", "quantity", "purchase_date"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    if data['asset_type'] not in [ASSET_TYPE_INDIAN_STOCK, ASSET_TYPE_US_STOCK, ASSET_TYPE_CRYPTO]:
        return jsonify({"error": f"Invalid asset_type: {data['asset_type']}"}), 400

    try:
        purchase_price = float(data["purchase_price"])
        quantity = float(data["quantity"])
        if purchase_price <= 0 or quantity <= 0:
            return jsonify({"error": "Purchase price and quantity must be positive numbers"}), 400
    except ValueError:
        return jsonify({"error": "Purchase price and quantity must be valid numbers"}), 400

    asset_to_update = None
    for asset in portfolio:
        if asset["id"] == asset_id:
            asset_to_update = asset
            break
    
    if not asset_to_update:
        return jsonify({"error": "Asset not found"}), 404

    asset_to_update["symbol"] = data["symbol"].upper()
    asset_to_update["asset_type"] = data["asset_type"]
    asset_to_update["purchase_price"] = purchase_price
    asset_to_update["quantity"] = quantity
    asset_to_update["purchase_date"] = data["purchase_date"]
    
    logging.info(f"Updated asset: {asset_to_update['symbol']} (ID: {asset_id})")
    return jsonify(asset_to_update), 200

@app.route('/assets/<string:asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    global portfolio
    initial_length = len(portfolio)
    portfolio = [asset for asset in portfolio if asset["id"] != asset_id]
    
    if len(portfolio) == initial_length:
        return jsonify({"error": "Asset not found"}), 404
        
    logging.info(f"Deleted asset ID: {asset_id}")
    return jsonify({"message": "Asset deleted successfully"}), 200

@app.route('/assets', methods=['DELETE'])
def bulk_delete_assets():
    global portfolio
    data = request.get_json()
    if not data or "ids" not in data or not isinstance(data["ids"], list):
        return jsonify({"error": "Invalid request body. Expected {'ids': ['id1', 'id2', ...]}"}), 400

    ids_to_delete = set(data["ids"])
    if not ids_to_delete:
        return jsonify({"message": "No asset IDs provided for deletion"}), 200

    initial_length = len(portfolio)
    portfolio = [asset for asset in portfolio if asset["id"] not in ids_to_delete]
    deleted_count = initial_length - len(portfolio)
    
    if deleted_count > 0:
        logging.info(f"Bulk deleted {deleted_count} assets. IDs: {', '.join(list(ids_to_delete))}")
    
    return jsonify({"message": f"{deleted_count} assets deleted successfully"}), 200

# --- Symbol List Endpoints ---
@app.route('/api/symbols/crypto', methods=['GET'])
def get_crypto_symbols():
    return jsonify(CRYPTO_SYMBOLS)

@app.route('/api/symbols/indian_stocks', methods=['GET'])
def get_indian_stock_symbols():
    return jsonify(INDIAN_STOCK_SYMBOLS)

@app.route('/api/symbols/us_stocks', methods=['GET'])
def get_us_stock_symbols():
    return jsonify(US_STOCK_SYMBOLS)

# --- Main guard for running with 'python app.py' for local development ---
if __name__ == '__main__':
    # When running directly, Flask's dev server might reload, re-running module-level code.
    # The symbol loading functions are designed to be safe if called multiple times (they clear and reload lists).
    # For production with Gunicorn, module-level code runs once per worker process initialization.
    flask_port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    logging.info(f"Starting Flask development server on port {flask_port}")
    app.run(debug=True, host='0.0.0.0', port=flask_port)
