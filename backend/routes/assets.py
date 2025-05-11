from flask import Blueprint, request, jsonify
from typing import Dict, Any, List

from backend.models import portfolio
from backend.utils.logging import logger
from backend.config.settings import ASSET_TYPE_INDIAN_STOCK, ASSET_TYPE_US_STOCK, ASSET_TYPE_CRYPTO

# Create a Blueprint for asset routes
assets_bp = Blueprint('assets', __name__)


@assets_bp.route('/', methods=['GET'])
def get_assets():
    """
    Get all assets in the portfolio
    """
    return jsonify(portfolio.get_all_assets())


@assets_bp.route('/', methods=['POST'])
def add_asset():
    """
    Add a new asset to the portfolio
    """
    data = request.get_json()
    required_fields = ["symbol", "asset_type", "purchase_price", "quantity", "purchase_date"]
    
    # Validate request data
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Validate asset_type
    if data['asset_type'] not in [ASSET_TYPE_INDIAN_STOCK, ASSET_TYPE_US_STOCK, ASSET_TYPE_CRYPTO]:
        return jsonify({"error": f"Invalid asset_type: {data['asset_type']}. Expected one of: {ASSET_TYPE_INDIAN_STOCK}, {ASSET_TYPE_US_STOCK}, {ASSET_TYPE_CRYPTO}"}), 400

    # Validate numeric fields
    try:
        purchase_price = float(data["purchase_price"])
        quantity = float(data["quantity"])
        if purchase_price <= 0 or quantity <= 0:
            return jsonify({"error": "Purchase price and quantity must be positive numbers"}), 400
    except ValueError:
        return jsonify({"error": "Purchase price and quantity must be valid numbers"}), 400
    
    # TODO: Add validation for purchase_date format (e.g., YYYY-MM-DD from date picker)

    # Add the asset
    new_asset = portfolio.add_asset(data)
    return jsonify(new_asset), 201


@assets_bp.route('/<string:asset_id>', methods=['GET'])
def get_asset(asset_id: str):
    """
    Get a specific asset by ID
    """
    asset = portfolio.get_asset_by_id(asset_id)
    if not asset:
        return jsonify({"error": "Asset not found"}), 404
    return jsonify(asset)


@assets_bp.route('/<string:asset_id>', methods=['PUT'])
def update_asset(asset_id: str):
    """
    Update an existing asset
    """
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

    updated_asset = portfolio.update_asset(asset_id, data)
    if not updated_asset:
        return jsonify({"error": "Asset not found"}), 404

    return jsonify(updated_asset)


@assets_bp.route('/<string:asset_id>', methods=['DELETE'])
def delete_asset(asset_id: str):
    """
    Delete an asset from the portfolio
    """
    success = portfolio.delete_asset(asset_id)
    if not success:
        return jsonify({"error": "Asset not found"}), 404

    return jsonify({"message": "Asset deleted successfully"})


@assets_bp.route('/', methods=['DELETE'])
def bulk_delete_assets():
    """
    Delete multiple assets from the portfolio
    """
    data = request.get_json()
    if not data or "ids" not in data or not isinstance(data["ids"], list):
        return jsonify({"error": "Invalid request body. Expected {'ids': ['id1', 'id2', ...]}"}), 400

    ids_to_delete = data["ids"]
    if not ids_to_delete:
        return jsonify({"message": "No asset IDs provided for deletion"}), 200

    deleted_count = portfolio.bulk_delete_assets(ids_to_delete)
    
    return jsonify({"message": f"{deleted_count} assets deleted successfully"}), 200
