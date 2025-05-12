from flask import Blueprint, request, jsonify
from datetime import datetime

from backend.models import db, Asset # Updated import
from backend.utils.logging import logger
from backend.config.settings import ASSET_TYPE_INDIAN_STOCK, ASSET_TYPE_US_STOCK, ASSET_TYPE_CRYPTO

# Create a Blueprint for asset routes
assets_bp = Blueprint('assets', __name__)


@assets_bp.route('/', methods=['GET'])
def get_assets():
    """
    Get all assets in the portfolio
    """
    assets = Asset.query.all()
    return jsonify([asset.to_dict() for asset in assets])


@assets_bp.route('/', methods=['POST'])
def add_asset():
    """
    Add a new asset to the portfolio
    """
    data = request.get_json()
    required_fields = ["symbol", "asset_type", "purchase_price", "quantity", "purchase_date"]
    
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    if data['asset_type'] not in [ASSET_TYPE_INDIAN_STOCK, ASSET_TYPE_US_STOCK, ASSET_TYPE_CRYPTO]:
        return jsonify({"error": f"Invalid asset_type: {data['asset_type']}. Expected one of: {ASSET_TYPE_INDIAN_STOCK}, {ASSET_TYPE_US_STOCK}, {ASSET_TYPE_CRYPTO}"}), 400

    try:
        purchase_price = float(data["purchase_price"])
        quantity = float(data["quantity"])
        if purchase_price <= 0 or quantity <= 0:
            return jsonify({"error": "Purchase price and quantity must be positive numbers"}), 400
        # Ensure purchase_date is a string and then parse
        if not isinstance(data.get("purchase_date"), str):
             return jsonify({"error": "purchase_date must be a string in YYYY-MM-DD format"}), 400
        purchase_date = datetime.strptime(data["purchase_date"], '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Purchase price and quantity must be valid numbers, and purchase_date in YYYY-MM-DD format"}), 400
    except TypeError:
        return jsonify({"error": "Invalid type for purchase_date, expected string in YYYY-MM-DD format"}), 400

    new_asset = Asset(
        symbol=data['symbol'],
        asset_type=data['asset_type'],
        purchase_price=purchase_price,
        quantity=quantity,
        purchase_date=purchase_date
    )
    db.session.add(new_asset)
    db.session.commit()
    return jsonify(new_asset.to_dict()), 201


@assets_bp.route('/<int:asset_id>', methods=['GET'])
def get_asset(asset_id: int):
    """
    Get a specific asset by ID
    """
    asset = db.session.get(Asset, asset_id)
    if not asset:
        return jsonify({"error": "Asset not found"}), 404
    return jsonify(asset.to_dict())


@assets_bp.route('/<int:asset_id>', methods=['PUT'])
def update_asset(asset_id: int):
    """
    Update an existing asset
    """
    asset = db.session.get(Asset, asset_id)
    if not asset:
        return jsonify({"error": "Asset not found"}), 404

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
        if not isinstance(data.get("purchase_date"), str):
             return jsonify({"error": "purchase_date must be a string in YYYY-MM-DD format"}), 400
        purchase_date = datetime.strptime(data["purchase_date"], '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Purchase price and quantity must be valid numbers, and purchase_date in YYYY-MM-DD format"}), 400
    except TypeError:
        return jsonify({"error": "Invalid type for purchase_date, expected string in YYYY-MM-DD format"}), 400

    asset.symbol = data['symbol']
    asset.asset_type = data['asset_type']
    asset.purchase_price = purchase_price
    asset.quantity = quantity
    asset.purchase_date = purchase_date
    
    db.session.commit()
    return jsonify(asset.to_dict())


@assets_bp.route('/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id: int):
    """
    Delete an asset from the portfolio
    """
    asset = db.session.get(Asset, asset_id)
    if not asset:
        return jsonify({"error": "Asset not found"}), 404

    db.session.delete(asset)
    db.session.commit()
    return jsonify({"message": "Asset deleted successfully"})


@assets_bp.route('/', methods=['DELETE'])
def bulk_delete_assets():
    """
    Delete multiple assets from the portfolio
    """
    data = request.get_json()
    if not data or "ids" not in data or not isinstance(data["ids"], list):
        return jsonify({"error": "Invalid request body. Expected {'ids': [id1, id2, ...]}"}), 400

    ids_to_delete = data["ids"]
    if not ids_to_delete:
        return jsonify({"message": "No asset IDs provided for deletion"}), 200
    
    # Ensure all ids are integers
    try:
        processed_ids = [int(id_val) for id_val in ids_to_delete]
    except ValueError:
        return jsonify({"error": "All asset IDs must be integers"}), 400

    deleted_count = Asset.query.filter(Asset.id.in_(processed_ids)).delete(synchronize_session=False)
    db.session.commit()
    
    return jsonify({"message": f"{deleted_count} assets deleted successfully"}), 200
