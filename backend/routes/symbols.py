from flask import Blueprint, jsonify
from backend.services import symbol_service
from backend.utils.logging import logger

# Create a Blueprint for symbol routes
symbols_bp = Blueprint('symbols', __name__, url_prefix='/api/symbols')


@symbols_bp.route('/crypto', methods=['GET'])
def get_crypto_symbols():
    """
    Get all cryptocurrency symbols
    """
    return jsonify(symbol_service.get_crypto_symbols())


@symbols_bp.route('/indian_stocks', methods=['GET'])
def get_indian_stock_symbols():
    """
    Get all Indian stock symbols
    """
    return jsonify(symbol_service.get_indian_stock_symbols())


@symbols_bp.route('/us_stocks', methods=['GET'])
def get_us_stock_symbols():
    """
    Get all US stock symbols
    """
    return jsonify(symbol_service.get_us_stock_symbols())
