import uuid
from typing import List, Dict, Any, Optional
from backend.utils.logging import logger
from backend.config.settings import ASSET_TYPE_INDIAN_STOCK, ASSET_TYPE_US_STOCK, ASSET_TYPE_CRYPTO

# In-memory portfolio storage
_portfolio = [
    # 10 Indian Stocks - Total approx 5,000,000 INR
    {"id": str(uuid.uuid4()), "symbol": "RELIANCE.NS", "asset_type": ASSET_TYPE_INDIAN_STOCK, "purchase_price": 2800, "quantity": 200, "purchase_date": "2023-01-10"}, # 560,000
    {"id": str(uuid.uuid4()), "symbol": "TCS.NS", "asset_type": ASSET_TYPE_INDIAN_STOCK, "purchase_price": 3500, "quantity": 150, "purchase_date": "2023-02-15"},      # 525,000
    {"id": str(uuid.uuid4()), "symbol": "HDFCBANK.NS", "asset_type": ASSET_TYPE_INDIAN_STOCK, "purchase_price": 1600, "quantity": 300, "purchase_date": "2023-03-20"}, # 480,000
    {"id": str(uuid.uuid4()), "symbol": "INFY.NS", "asset_type": ASSET_TYPE_INDIAN_STOCK, "purchase_price": 1500, "quantity": 350, "purchase_date": "2023-04-05"},     # 525,000
    {"id": str(uuid.uuid4()), "symbol": "ICICIBANK.NS", "asset_type": ASSET_TYPE_INDIAN_STOCK, "purchase_price": 900, "quantity": 550, "purchase_date": "2023-05-12"},  # 495,000
    {"id": str(uuid.uuid4()), "symbol": "SBIN.NS", "asset_type": ASSET_TYPE_INDIAN_STOCK, "purchase_price": 600, "quantity": 800, "purchase_date": "2023-06-18"},      # 480,000
    {"id": str(uuid.uuid4()), "symbol": "KOTAKBANK.NS", "asset_type": ASSET_TYPE_INDIAN_STOCK, "purchase_price": 1800, "quantity": 270, "purchase_date": "2023-07-22"},# 486,000
    {"id": str(uuid.uuid4()), "symbol": "BHARTIARTL.NS", "asset_type": ASSET_TYPE_INDIAN_STOCK, "purchase_price": 850, "quantity": 580, "purchase_date": "2023-08-30"},# 493,000
    {"id": str(uuid.uuid4()), "symbol": "LT.NS", "asset_type": ASSET_TYPE_INDIAN_STOCK, "purchase_price": 2200, "quantity": 220, "purchase_date": "2023-09-05"},        # 484,000
    {"id": str(uuid.uuid4()), "symbol": "HINDUNILVR.NS", "asset_type": ASSET_TYPE_INDIAN_STOCK, "purchase_price": 2500, "quantity": 190, "purchase_date": "2023-10-10"},# 475,000
                                                                                                                                                # Total: 4,903,000

    # 5 US Stocks - Total approx 7,000,000 INR
    # Assuming an arbitrary USD to INR conversion for purchase price, e.g., 1 USD = 80 INR for these examples
    # For AAPL, if price is $170, then 170*80 = 13600 INR
    {"id": str(uuid.uuid4()), "symbol": "AAPL", "asset_type": ASSET_TYPE_US_STOCK, "purchase_price": 14000, "quantity": 100, "purchase_date": "2023-01-20"}, # 1,400,000
    {"id": str(uuid.uuid4()), "symbol": "MSFT", "asset_type": ASSET_TYPE_US_STOCK, "purchase_price": 24000, "quantity": 60, "purchase_date": "2023-02-25"},  # 1,440,000
    {"id": str(uuid.uuid4()), "symbol": "GOOGL", "asset_type": ASSET_TYPE_US_STOCK, "purchase_price": 10000, "quantity": 130, "purchase_date": "2023-03-15"}, # 1,300,000
    {"id": str(uuid.uuid4()), "symbol": "AMZN", "asset_type": ASSET_TYPE_US_STOCK, "purchase_price": 9000, "quantity": 160, "purchase_date": "2023-04-22"},   # 1,440,000
    {"id": str(uuid.uuid4()), "symbol": "TSLA", "asset_type": ASSET_TYPE_US_STOCK, "purchase_price": 15000, "quantity": 100, "purchase_date": "2023-05-30"}, # 1,500,000
                                                                                                                                                # Total: 7,080,000

    # 10 Cryptocurrencies - Total approx 2,500,000 INR
    {"id": str(uuid.uuid4()), "symbol": "BTC", "asset_type": ASSET_TYPE_CRYPTO, "purchase_price": 2200000, "quantity": 0.1, "purchase_date": "2023-01-05"},  # 220,000
    {"id": str(uuid.uuid4()), "symbol": "ETH", "asset_type": ASSET_TYPE_CRYPTO, "purchase_price": 150000, "quantity": 1.5, "purchase_date": "2023-02-08"},   # 225,000
    {"id": str(uuid.uuid4()), "symbol": "BNB", "asset_type": ASSET_TYPE_CRYPTO, "purchase_price": 25000, "quantity": 10, "purchase_date": "2023-03-10"},    # 250,000
    {"id": str(uuid.uuid4()), "symbol": "XRP", "asset_type": ASSET_TYPE_CRYPTO, "purchase_price": 40, "quantity": 6000, "purchase_date": "2023-04-15"},     # 240,000
    {"id": str(uuid.uuid4()), "symbol": "ADA", "asset_type": ASSET_TYPE_CRYPTO, "purchase_price": 30, "quantity": 8000, "purchase_date": "2023-05-20"},     # 240,000
    {"id": str(uuid.uuid4()), "symbol": "SOL", "asset_type": ASSET_TYPE_CRYPTO, "purchase_price": 1800, "quantity": 140, "purchase_date": "2023-06-25"},    # 252,000
    {"id": str(uuid.uuid4()), "symbol": "DOGE", "asset_type": ASSET_TYPE_CRYPTO, "purchase_price": 6, "quantity": 40000, "purchase_date": "2023-07-01"},    # 240,000
    {"id": str(uuid.uuid4()), "symbol": "DOT", "asset_type": ASSET_TYPE_CRYPTO, "purchase_price": 500, "quantity": 500, "purchase_date": "2023-08-05"},     # 250,000
    {"id": str(uuid.uuid4()), "symbol": "SHIB", "asset_type": ASSET_TYPE_CRYPTO, "purchase_price": 0.0007, "quantity": 350000000, "purchase_date": "2023-09-10"},#245,000
    {"id": str(uuid.uuid4()), "symbol": "MATIC", "asset_type": ASSET_TYPE_CRYPTO, "purchase_price": 70, "quantity": 3500, "purchase_date": "2023-10-15"}   # 245,000
                                                                                                                                                # Total: 2,407,000
]


def get_all_assets() -> List[Dict[str, Any]]:
    """
    Get all assets in the portfolio
    """
    return _portfolio


def get_asset_by_id(asset_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific asset by its ID
    """
    for asset in _portfolio:
        if asset["id"] == asset_id:
            return asset
    return None


def add_asset(asset_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add a new asset to the portfolio
    """
    # Create a new asset with a UUID
    new_asset = {
        "id": str(uuid.uuid4()),
        "symbol": asset_data["symbol"].upper(),  # Standardize symbol to uppercase
        "asset_type": asset_data["asset_type"],
        "purchase_price": float(asset_data["purchase_price"]),
        "quantity": float(asset_data["quantity"]),
        "purchase_date": asset_data["purchase_date"]
    }
    
    _portfolio.append(new_asset)
    logger.info(f"Added asset: {new_asset['symbol']}")
    return new_asset


def update_asset(asset_id: str, asset_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update an existing asset in the portfolio
    """
    asset = get_asset_by_id(asset_id)
    if not asset:
        return None
    
    # Update the asset with new data
    asset["symbol"] = asset_data["symbol"].upper()
    asset["asset_type"] = asset_data["asset_type"]
    asset["purchase_price"] = float(asset_data["purchase_price"])
    asset["quantity"] = float(asset_data["quantity"])
    asset["purchase_date"] = asset_data["purchase_date"]
    
    logger.info(f"Updated asset: {asset['symbol']} (ID: {asset_id})")
    return asset


def delete_asset(asset_id: str) -> bool:
    """
    Delete an asset from the portfolio
    """
    global _portfolio
    initial_length = len(_portfolio)
    _portfolio = [asset for asset in _portfolio if asset["id"] != asset_id]
    
    if len(_portfolio) < initial_length:
        logger.info(f"Deleted asset with ID: {asset_id}")
        return True
    return False


def bulk_delete_assets(asset_ids: List[str]) -> int:
    """
    Delete multiple assets from the portfolio
    Returns the number of assets deleted
    """
    global _portfolio
    initial_length = len(_portfolio)
    ids_to_delete = set(asset_ids)
    
    _portfolio = [asset for asset in _portfolio if asset["id"] not in ids_to_delete]
    deleted_count = initial_length - len(_portfolio)
    
    if deleted_count > 0:
        logger.info(f"Bulk deleted {deleted_count} assets. IDs: {', '.join(list(ids_to_delete))}")
    
    return deleted_count
