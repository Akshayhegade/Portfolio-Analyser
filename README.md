# Portfolio Analyser

A full-stack web application designed to track and analyze various asset classes including Indian stocks, US stocks, and cryptocurrencies. The application provides a clean, intuitive interface for managing your investment portfolio.

## Features

- **Asset Management**:
  - Add assets with detailed information (symbol, type, purchase price, quantity, date)
  - Inline editing of asset details
  - Delete individual or multiple assets
  - View categorized assets (Indian Stocks, US Stocks, Cryptocurrencies)

- **Portfolio Overview**:
  - View total investment by asset class
  - Calculate overall portfolio value
  - Track performance of individual assets
  - Live price updates for all assets
  - Real-time profit/loss calculations

- **Symbol Management**:
  - Indian and US stock symbols stored in JSON files for easy maintenance
  - Cryptocurrency symbols fetched from CoinGecko API
  - Symbols loaded into memory at startup for fast access

- **Live Price Tracking**:
  - Real-time price fetching for stocks via Yahoo Finance API
  - Live cryptocurrency prices from CoinGecko API
  - Smart caching system to reduce API calls
  - Rate-limiting awareness to handle API restrictions

## Tech Stack

- **Backend:** 
  - Python (Flask) RESTful API
  - In-memory data storage (PostgreSQL integration planned)
  - JSON-based configuration for symbols
  
- **Frontend:** 
  - React 19 with Material UI components
  - Responsive design for desktop and mobile views
  - Environment variable configuration for API endpoints

- **Deployment:** 
  - Docker containerization for both frontend and backend
  - Docker Compose for orchestration
  - Development and production configurations

- **APIs:** 
  - CoinGecko API for cryptocurrency data and prices
  - Yahoo Finance API for real-time stock prices
  - Rate-limited caching for optimal API usage

## Project Structure

```
Portfolio Analyser/
├── docker-compose.yml      # Docker Compose configuration
│
├── backend/                # Python Flask backend
│   ├── Dockerfile         # Backend container configuration
│   ├── requirements.txt   # Python dependencies
│   ├── app.py             # Main Flask application
│   ├── data/              # JSON files for symbol data
│   │   ├── indian_stocks.json
│   │   └── us_stocks.json
│   ├── models/            # Data models
│   ├── services/          # Business logic services
│   │   ├── symbol_service.py  # Symbol loading and caching
│   │   └── price_service.py   # Live price fetching
│   └── config/            # Application configuration
│
├── frontend/              # React frontend
│   ├── Dockerfile         # Frontend container configuration
│   ├── package.json       # Node.js dependencies
│   ├── public/            # Static files
│   └── src/               # React source code
│       ├── components/    # React components
│       │   ├── AssetList.js       # Asset list with inline editing
│       │   ├── AddAssetForm.js    # Form for adding new assets
│       │   └── LivePriceInfo.js   # Live price display component
│       ├── App.js         # Main React application
│       └── config.js      # Frontend configuration
│
└── README.md             # Project documentation
```

## Getting Started

### Prerequisites

- Docker and Docker Compose installed on your system
- Git for version control

### Running with Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Portfolio\ Analyser
   ```

2. Start the application using Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001

### Development Setup

#### Backend (Flask)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the Flask server:
   ```bash
   python app.py
   ```

#### Frontend (React)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```

## API Endpoints

### Assets
- `GET /assets/` - Get all assets
- `POST /assets/` - Add a new asset
- `GET /assets/:id` - Get a specific asset
- `PUT /assets/:id` - Update a specific asset
- `DELETE /assets/:id` - Delete a specific asset

### Symbols
- `GET /api/symbols/indian_stocks` - Get all Indian stock symbols
- `GET /api/symbols/us_stocks` - Get all US stock symbols
- `GET /api/symbols/crypto` - Get all cryptocurrency symbols

### Prices
- `POST /api/prices` - Get prices for multiple assets
- `GET /api/prices/<symbol>?type=<asset_type>` - Get price for a specific asset
- `POST /api/prices/refresh` - Force refresh the price cache

## Future Enhancements

- User authentication and user-specific portfolios
- Historical performance tracking and visualization
- Advanced charting and technical analysis
- Database integration for persistent storage
- Mobile application
- API key management for higher rate limits

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
