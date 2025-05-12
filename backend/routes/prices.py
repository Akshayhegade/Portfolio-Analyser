from flask import Blueprint, jsonify, request
from backend.services.price_service import PriceService

price_routes = Blueprint('prices', __name__)
price_service = PriceService()

@price_routes.route('/api/prices', methods=['POST'])
def get_prices():
    """
    Get current prices for a list of assets
    Expected request body: { "assets": [{"symbol": "AAPL", "asset_type": "US Stock"}, ...] }
    Returns: { "AAPL": 150.25, "MSFT": 300.50, ... }
    """
    assets = request.json.get('assets', [])
    if not assets:
        return jsonify({"error": "No assets provided"}), 400
        
    prices = price_service.get_prices_for_assets(assets)
    return jsonify(prices)

@price_routes.route('/api/prices/<symbol>', methods=['GET'])
def get_price(symbol):
    """
    Get current price for a single asset
    URL params: ?type=US Stock|Indian Stock|Crypto
    Returns: {"symbol": "AAPL", "price": 150.25}
    """
    if not symbol:
        return jsonify({"error": "No symbol provided"}), 400
        
    asset_type = request.args.get('type', 'US Stock')  # Default to US Stock
    
    # Create a mock asset object for the price service
    asset = {"symbol": symbol, "asset_type": asset_type}
    price = price_service.get_price_for_asset(asset)
        
    if price is None:
        return jsonify({'error': f'Unable to fetch price for {symbol}'}), 404
        
    return jsonify({'symbol': symbol, 'price': price})

@price_routes.route('/api/prices/refresh', methods=['POST'])
def refresh_prices():
    """
    Force refresh the price cache
    Returns: {"status": "success", "message": "Price cache cleared"}
    """
    price_service.clear_cache()
    return jsonify({
        "status": "success",
        "message": "Price cache cleared"
    })
