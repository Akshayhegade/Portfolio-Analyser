import requests
import yfinance as yf
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from backend.utils.logging import logger
from backend.config.settings import COINGECKO_API_URL, REQUEST_TIMEOUT
from backend.services import symbol_service

class PriceService:
    """
    Service for fetching current prices for various asset types
    Supports Indian stocks, US stocks, and cryptocurrencies
    Implements advanced caching to reduce API calls with rate limiting awareness
    """
    def __init__(self):
        # Cache to store prices with a 15-minute expiry for crypto (to reduce API calls)
        # and 5-minute expiry for stocks
        self.price_cache = {}  # Format: {symbol: {price: float, timestamp: datetime}}
        self.stock_cache_duration = timedelta(minutes=5)
        self.crypto_cache_duration = timedelta(minutes=15)
        
        # Rate limiting parameters for CoinGecko
        self.last_coingecko_request = datetime.now() - timedelta(seconds=10)  # Initialize with a past time
        self.coingecko_request_limit = 10  # requests per minute (conservative for free API)
        self.coingecko_min_request_interval = 60 / self.coingecko_request_limit  # seconds between requests
        
        # Flag to indicate if we're experiencing rate limiting
        self.coingecko_rate_limited = False
        self.rate_limit_reset_time = None
    
    def _is_cache_valid(self, symbol: str, is_crypto: bool = False) -> bool:
        """Check if the cached price for a symbol is still valid"""
        if symbol not in self.price_cache:
            return False
        
        cache_time = self.price_cache[symbol]['timestamp']
        duration = self.crypto_cache_duration if is_crypto else self.stock_cache_duration
        
        # If we're rate limited by CoinGecko, extend crypto cache validity
        if is_crypto and self.coingecko_rate_limited:
            # Double the cache duration during rate limiting
            duration = duration * 2
            
        return datetime.now() - cache_time < duration
    
    def get_stock_price(self, symbol: str) -> Optional[float]:
        """
        Get current stock price using Yahoo Finance API
        Works for both US and Indian stocks
        """
        # Check cache first
        if self._is_cache_valid(symbol):
            return self.price_cache[symbol]['price']
        
        try:
            logger.info(f"Fetching stock price for {symbol}")
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            
            if not data.empty:
                # Get most recent closing price
                price = data['Close'].iloc[-1]
                
                # Update cache
                self.price_cache[symbol] = {
                    'price': price,
                    'timestamp': datetime.now()
                }
                
                return price
            
            logger.warning(f"No price data found for stock {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching stock price for {symbol}: {e}")
            return None
    
    def _manage_coingecko_rate_limiting(self) -> Tuple[bool, Optional[str]]:
        """Manage CoinGecko API rate limiting
        Returns a tuple of (can_proceed, error_message)
        """
        now = datetime.now()
        
        # If we know we're rate limited and the reset time hasn't passed yet
        if self.coingecko_rate_limited and self.rate_limit_reset_time and now < self.rate_limit_reset_time:
            time_to_wait = (self.rate_limit_reset_time - now).total_seconds()
            return False, f"Rate limited. Try again in {int(time_to_wait)} seconds."
        
        # Reset rate limited flag if needed
        if self.coingecko_rate_limited and self.rate_limit_reset_time and now >= self.rate_limit_reset_time:
            logger.info("CoinGecko rate limit period has passed, resetting rate limit flag")
            self.coingecko_rate_limited = False
            self.rate_limit_reset_time = None
        
        # Calculate time since last request to enforce minimum interval
        time_since_last_request = (now - self.last_coingecko_request).total_seconds()
        
        # If we need to wait, return False with message
        if time_since_last_request < self.coingecko_min_request_interval:
            wait_time = self.coingecko_min_request_interval - time_since_last_request
            # For short waits (< 1 second), just wait instead of returning error
            if wait_time < 1.0:
                time.sleep(wait_time)
                self.last_coingecko_request = datetime.now()
                return True, None
            return False, f"Too many requests. Try again in {int(wait_time)} seconds."
        
        # Update last request time and allow the request
        self.last_coingecko_request = now
        return True, None
            
    def get_crypto_price(self, symbol_id: str) -> Optional[float]:
        """
        Get current cryptocurrency price using CoinGecko API
        Handles both CoinGecko IDs (e.g., 'bitcoin') and trading pairs (e.g., 'btc-usd')
        """
        # Convert to lowercase for consistency
        symbol_id = symbol_id.lower()
        
        # If the symbol is in format like 'btc-usd', extract the base symbol
        if '-' in symbol_id:
            base_symbol = symbol_id.split('-')[0]
            # Try to find the CoinGecko ID for this symbol
            symbol_id = self._find_crypto_id_by_symbol(base_symbol)
            if not symbol_id:
                logger.error(f"Could not find CoinGecko ID for symbol: {base_symbol}")
                return None
        
        # Check cache first with crypto flag set to true
        if self._is_cache_valid(symbol_id, is_crypto=True):
            logger.info(f"Using cached price for {symbol_id}")
            return self.price_cache[symbol_id]['price']
        
        # Check if we can proceed with the API request (rate limiting)
        can_proceed, error_message = self._manage_coingecko_rate_limiting()
        if not can_proceed:
            logger.warning(f"Skipping CoinGecko request due to rate limiting: {error_message}")
            # Return cached value even if expired rather than nothing
            if symbol_id in self.price_cache:
                logger.info(f"Using expired cache for {symbol_id} due to rate limiting")
                return self.price_cache[symbol_id]['price']
            return None
        
        try:
            logger.info(f"Fetching crypto price for {symbol_id}")
            
            # First try with simple/price endpoint
            params = {'ids': symbol_id, 'vs_currencies': 'usd'}
            
            response = requests.get(
                f"{COINGECKO_API_URL}/simple/price", 
                params=params, 
                timeout=REQUEST_TIMEOUT
            )
            
            # Check if we hit rate limits
            if response.status_code == 429:
                logger.warning("CoinGecko rate limit reached")
                self.coingecko_rate_limited = True
                # Set a reset time 60 seconds from now (typical for CoinGecko)
                self.rate_limit_reset_time = datetime.now() + timedelta(seconds=60)
                
                # Return cached value even if expired
                if symbol_id in self.price_cache:
                    logger.info(f"Using expired cache for {symbol_id} due to rate limiting")
                    return self.price_cache[symbol_id]['price']
                return None
            
            response.raise_for_status()
            
            data = response.json()
            if data and symbol_id in data and 'usd' in data[symbol_id]:
                price = data[symbol_id]['usd']
                
                # Update cache
                if price is not None:
                    self.price_cache[symbol_id] = {
                        'price': price,
                        'timestamp': datetime.now()
                    }
                    
                return price
            
            logger.warning(f"No price data found for crypto {symbol_id}")
            return None
            
        except requests.exceptions.RequestException as e:
            # Handle rate limiting explicitly
            if hasattr(e, 'response') and e.response and e.response.status_code == 429:
                logger.warning("CoinGecko rate limit reached (from exception)")
                self.coingecko_rate_limited = True
                self.rate_limit_reset_time = datetime.now() + timedelta(seconds=60)
                
                # Return cached value even if expired
                if symbol_id in self.price_cache:
                    logger.info(f"Using expired cache for {symbol_id} due to rate limiting")
                    return self.price_cache[symbol_id]['price']
            
            logger.error(f"Error fetching crypto price for {symbol_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching crypto price for {symbol_id}: {e}")
            return None
    
    def _find_crypto_id_by_symbol(self, symbol: str) -> Optional[str]:
        """
        Find the CoinGecko ID for a given crypto symbol.
        Symbol can be either the CoinGecko ID, symbol (e.g., 'btc'), or name (e.g., 'bitcoin')
        """
        logger.info(f"Looking up CoinGecko ID for symbol: {symbol}")
        
        # Get the list of crypto symbols from the symbol service
        crypto_symbols = symbol_service.get_crypto_symbols()
        
        if not crypto_symbols:
            logger.error("No crypto symbols loaded from symbol service!")
            return None
            
        logger.info(f"Loaded {len(crypto_symbols)} crypto symbols from symbol service")
        
        # First try exact match on symbol (case-insensitive)
        for coin in crypto_symbols:
            if 'symbol' not in coin or 'id' not in coin or 'name' not in coin:
                logger.warning(f"Malformed coin data: {coin}")
                continue
                
            if coin['symbol'].lower() == symbol.lower() or \
               coin['id'].lower() == symbol.lower() or \
               coin['name'].lower() == symbol.lower():
                logger.info(f"Found exact match for {symbol}: {coin['id']}")
                return coin['id']
                
        # If no exact match, try partial match on name or symbol
        for coin in crypto_symbols:
            if 'symbol' not in coin or 'id' not in coin or 'name' not in coin:
                continue
                
            if symbol.lower() in coin['symbol'].lower() or \
               symbol.lower() in coin['name'].lower() or \
               symbol.lower() in coin['id'].lower():
                logger.info(f"Found partial match for {symbol}: {coin['id']}")
                return coin['id']
        
        # Log the first few symbols for debugging
        sample_symbols = [f"{c.get('id', '?')} ({c.get('symbol', '?')})" for c in crypto_symbols[:5]]
        logger.warning(f"Could not find CoinGecko ID for symbol: {symbol}")
        logger.warning(f"Sample of available symbols: {', '.join(sample_symbols)}...")
        
        return None
        
        # Normalize the input symbol (uppercase for comparison)
        symbol = symbol.upper()
        
        # Look for an exact match on the symbol
        for crypto in crypto_symbols:
            if crypto['symbol'] == symbol:
                logger.info(f"Found CoinGecko ID for {symbol}: {crypto['id']}")
                return crypto['id']
        
        # If no exact match, try a case-insensitive search
        for crypto in crypto_symbols:
            if crypto['symbol'].upper() == symbol:
                logger.info(f"Found CoinGecko ID for {symbol}: {crypto['id']}")
                return crypto['id']
                
        # If still no match, try common symbol mappings
        symbol_mappings = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'USDT': 'tether',
            'BNB': 'binancecoin',
            'XRP': 'ripple',
            'ADA': 'cardano',
            'SOL': 'solana',
            'DOT': 'polkadot',
            'DOGE': 'dogecoin',
            'AVAX': 'avalanche-2',
            'MATIC': 'matic-network',  # Polygon
            'LINK': 'chainlink',
            'UNI': 'uniswap',
            'SHIB': 'shiba-inu',
            'LTC': 'litecoin'
        }
        
        if symbol in symbol_mappings:
            logger.info(f"Found CoinGecko ID for {symbol} in hardcoded mappings: {symbol_mappings[symbol]}")
            return symbol_mappings[symbol]
        
        logger.warning(f"Could not find CoinGecko ID for crypto symbol: {symbol}")
        return None
    
    def get_price_for_asset(self, asset: Dict[str, Any]) -> Optional[float]:
        """Get current price for a single asset based on its type"""
        symbol = asset.get('symbol')
        asset_type = asset.get('asset_type')
        
        if not symbol or not asset_type:
            logger.error(f"Invalid asset data: missing symbol or asset_type")
            return None
        
        if asset_type == 'Crypto':
            # Find the CoinGecko ID for this crypto symbol
            crypto_id = self._find_crypto_id_by_symbol(symbol)
            if not crypto_id:
                logger.error(f"Could not find CoinGecko ID for symbol: {symbol}")
                return None
                
            return self.get_crypto_price(crypto_id)
        else:  # 'Indian Stock' or 'US Stock'
            return self.get_stock_price(symbol)
    
    def get_prices_for_assets(self, assets: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Get current prices for a list of assets
        Returns a dictionary mapping symbols to prices
        """
        result = {}
        
        for asset in assets:
            symbol = asset.get('symbol')
            if not symbol:
                continue
                
            price = self.get_price_for_asset(asset)
            if price is not None:
                result[symbol] = price
                
        return result
    
    def clear_cache(self) -> None:
        """Clear the price cache completely"""
        self.price_cache = {}
        logger.info("Price cache cleared")
