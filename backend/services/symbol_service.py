import requests
import json 
import os 
from typing import List, Dict, Any
from backend.utils.logging import logger
from backend.config.settings import COINGECKO_API_URL, REQUEST_TIMEOUT

# Base directory for data files
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# In-memory symbol storage
_crypto_symbols = []
_indian_stock_symbols = []
_us_stock_symbols = []


def load_crypto_symbols() -> List[Dict[str, Any]]:
    """
    Load cryptocurrency symbols from CoinGecko API
    """
    global _crypto_symbols
    if _crypto_symbols:
        logger.info("Crypto symbols already loaded, returning cached version.")
        return _crypto_symbols

    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 100,  
        'page': 1,
        'sparkline': 'false',
        'price_change_percentage': 'false'  
    }
    
    try:
        logger.info(f"Fetching crypto symbols from {COINGECKO_API_URL}/coins/markets...")
        response = requests.get(f"{COINGECKO_API_URL}/coins/markets", params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()  
        data = response.json()
        
        # Store as a list of dicts: { id (for key), symbol, name }
        _crypto_symbols = [
            {'id': coin['id'], 'symbol': coin['symbol'].upper(), 'name': coin['name']}
            for coin in data
        ]
        logger.info(f"Successfully loaded {len(_crypto_symbols)} crypto symbols from CoinGecko.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching crypto symbols from CoinGecko: {e}")
        _crypto_symbols = []  
    except Exception as e:
        logger.error(f"An unexpected error occurred while processing crypto symbols: {e}")
        _crypto_symbols = []
    
    return _crypto_symbols


def load_indian_stock_symbols() -> List[Dict[str, Any]]:
    """
    Load Indian stock symbols from a JSON file.
    """
    global _indian_stock_symbols
    if _indian_stock_symbols: 
        logger.info("Indian stock symbols already loaded, returning cached version.")
        return _indian_stock_symbols

    file_path = os.path.join(_DATA_DIR, 'indian_stocks.json')
    try:
        logger.info(f"Loading Indian stock symbols from {file_path}...")
        with open(file_path, 'r') as f:
            _indian_stock_symbols = json.load(f)
        logger.info(f"Successfully loaded {len(_indian_stock_symbols)} Indian stock symbols from {file_path}.")
    except FileNotFoundError:
        logger.error(f"Indian stock symbols file not found: {file_path}")
        _indian_stock_symbols = []
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {file_path}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading Indian stock symbols: {e}")
        _indian_stock_symbols = []
    return _indian_stock_symbols


def load_us_stock_symbols() -> List[Dict[str, Any]]:
    """
    Load US stock symbols from a JSON file.
    """
    global _us_stock_symbols
    if _us_stock_symbols: 
        logger.info("US stock symbols already loaded, returning cached version.")
        return _us_stock_symbols
        
    file_path = os.path.join(_DATA_DIR, 'us_stocks.json')
    try:
        logger.info(f"Loading US stock symbols from {file_path}...")
        with open(file_path, 'r') as f:
            _us_stock_symbols = json.load(f)
        logger.info(f"Successfully loaded {len(_us_stock_symbols)} US stock symbols from {file_path}.")
    except FileNotFoundError:
        logger.error(f"US stock symbols file not found: {file_path}")
        _us_stock_symbols = []
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {file_path}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading US stock symbols: {e}")
        _us_stock_symbols = []
    return _us_stock_symbols


# --- Getter functions ---

def get_crypto_symbols() -> List[Dict[str, Any]]:
    """
    Get the list of cryptocurrency symbols. Loads if not already present.
    """
    if not _crypto_symbols:
        logger.info("Crypto symbols not found in memory, attempting to load.")
        load_crypto_symbols()
    return _crypto_symbols


def get_indian_stock_symbols() -> List[Dict[str, Any]]:
    """
    Get the list of Indian stock symbols. Loads if not already present.
    """
    if not _indian_stock_symbols:
        logger.info("Indian stock symbols not found in memory, attempting to load.")
        load_indian_stock_symbols()
    return _indian_stock_symbols


def get_us_stock_symbols() -> List[Dict[str, Any]]:
    """
    Get the list of US stock symbols. Loads if not already present.
    """
    if not _us_stock_symbols:
        logger.info("US stock symbols not found in memory, attempting to load.")
        load_us_stock_symbols()
    return _us_stock_symbols

# --- Service Class (recommended structure for Flask app integration) ---

class SymbolService:
    def __init__(self):
        self.crypto_symbols = []
        self.indian_stock_symbols = []
        self.us_stock_symbols = []
        self.load_all_symbols()

    def load_all_symbols(self):
        """
        Loads all types of symbols into the service instance.
        This is typically called once when the service is initialized.
        """
        logger.info("Initializing SymbolService and loading all symbols...")
        # Assign to instance variables, using the module-level functions that cache globally
        self.crypto_symbols = get_crypto_symbols() 
        self.indian_stock_symbols = get_indian_stock_symbols()
        self.us_stock_symbols = get_us_stock_symbols()
        logger.info("SymbolService: All symbols loaded and cached.")

    def get_all_crypto_symbols(self) -> List[Dict[str, Any]]:
        return self.crypto_symbols

    def get_all_indian_stock_symbols(self) -> List[Dict[str, Any]]:
        return self.indian_stock_symbols

    def get_all_us_stock_symbols(self) -> List[Dict[str, Any]]:
        return self.us_stock_symbols

    def get_all_symbols(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Returns all loaded symbols, categorized by type.
        """
        return {
            "crypto": self.crypto_symbols,
            "indian_stocks": self.indian_stock_symbols,
            "us_stocks": self.us_stock_symbols,
        }

# Optional: Eager load symbols when this module is imported by Flask app
# This happens if SymbolService is instantiated at app creation.
# If SymbolService is not instantiated globally but on-demand, then loading is lazy.
# Current setup in __init__.py for create_app() instantiates SymbolService,
# so symbols are loaded at app startup.

# For direct testing of this module:
if __name__ == '__main__':
    # Configure logger for direct script run
    import logging
    logging.basicConfig(level=logging.INFO)
    logger.info("--- Testing Symbol Loading ---")
    
    # Test loading functions directly (they use global caches)
    crypto = load_crypto_symbols()
    indian = load_indian_stock_symbols()
    us = load_us_stock_symbols()

    logger.info(f"Loaded {len(crypto)} crypto symbols via direct call.")
    logger.info(f"Loaded {len(indian)} Indian stock symbols via direct call.")
    logger.info(f"Loaded {len(us)} US stock symbols via direct call.")

    logger.info("--- Testing SymbolService ---")
    service = SymbolService()
    all_symbols = service.get_all_symbols()
    logger.info(f"Crypto from service: {len(all_symbols['crypto'])}")
    logger.info(f"Indian Stocks from service: {len(all_symbols['indian_stocks'])}")
    logger.info(f"US Stocks from service: {len(all_symbols['us_stocks'])}")

    # Verify subsequent calls use cache
    logger.info("--- Verifying Cache ---")
    service_2 = SymbolService() # Should use already loaded global symbols
    assert len(service_2.get_all_crypto_symbols()) == len(crypto)
    logger.info("Cache verification successful.")
