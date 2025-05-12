/**
 * Application configuration
 * 
 * This file centralizes all configuration settings and environment variables
 * for easier management and deployment across different environments.
 */

// API base URL from environment variable with fallback to localhost
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

// Configuration object
const config = {
  api: {
    baseUrl: API_BASE_URL,
    endpoints: {
      assets: `${API_BASE_URL}/assets`,
      indianStocks: `${API_BASE_URL}/api/symbols/indian_stocks`,
      usStocks: `${API_BASE_URL}/api/symbols/us_stocks`,
      crypto: `${API_BASE_URL}/api/symbols/crypto`,
      prices: `${API_BASE_URL}/api/prices`,
      priceForSymbol: (symbol) => `${API_BASE_URL}/api/prices/${symbol}`,
      refreshPrices: `${API_BASE_URL}/api/prices/refresh`
    }
  }
};

export default config;
