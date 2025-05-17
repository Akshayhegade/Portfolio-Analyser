# Portfolio Analyser

A full-stack web application designed to track and analyze various asset classes including Indian stocks, US stocks, and cryptocurrencies. The application provides a clean, intuitive interface for managing your investment portfolio with real-time price updates and performance tracking.

> **Latest Update (May 2024)**: Switched to SQLite database, improved Docker setup, and enhanced error handling for cryptocurrency price fetching.

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
  - Interactive data visualizations and charts

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
  - SQLite for persistent data storage (file-based for development)
  - SQLAlchemy ORM for database operations
  - JSON-based configuration for symbols
  - Rate-limited API integrations with Yahoo Finance and CoinGecko
  
- **Frontend:** 
  - React 19 with Material UI components
  - Responsive design for desktop and mobile views
  - Custom theming and elegant UI styling
  - Data visualization using Recharts library
  - Environment variable configuration for API endpoints

- **Deployment:** 
  - Docker containerization for both frontend and backend
  - Docker Compose for orchestration
  - Development and production configurations
  - Automatic database seeding on container startup
  - Volume mounting for persistent data storage

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
│   ├── alembic.ini        # Alembic configuration
│   ├── app.py             # Main Flask application
│   ├── data/              # JSON files for symbol data
│   │   ├── indian_stocks.json
│   │   └── us_stocks.json
│   ├── migrations/        # Alembic database migrations
│   │   ├── versions/      # Migration scripts
│   │   └── env.py         # Alembic environment setup
│   ├── models/            # Data models (SQLAlchemy)
│   │   ├── base.py        # Base model for common fields
│   │   ├── asset.py       # Asset model
│   │   └── price_history.py # PriceHistory model
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
│       │   ├── LivePriceInfo.js   # Live price display component
│       │   └── PortfolioCharts.js # Data visualization components
│       ├── App.js         # Main React application
│       ├── theme.js       # Custom Material UI theme
│       └── config.js      # Frontend configuration
│
└── README.md             # Project documentation
```

## Getting Started

### Prerequisites

- Docker and Docker Compose installed on your system
- Git for version control
- A running PostgreSQL server instance (Docker Compose will set one up for you, or you can use an existing one by configuring `DATABASE_URL` in a `.env` file in the `backend` directory).

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/portfolio-analyzer.git
   cd portfolio-analyzer
   ```

2. Start the application:
   ```bash
   docker-compose up --build
   ```
   This will:
   - Build and start both frontend and backend containers
   - Set up the SQLite database
   - Seed the database with initial data
   - Start the development servers

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001

4. For development, you can also run the services separately:
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   flask run --port=5001

   # Frontend (in a new terminal)
   cd frontend
   npm install
   npm start
   ```

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

3. Set up the `DATABASE_URL` environment variable. You can do this by creating a `.env` file in the `backend` directory with the following content:
   ```env
   DATABASE_URL="postgresql://your_db_user:your_db_password@your_db_host:your_db_port/your_db_name"
   ```
   Replace the placeholders with your actual PostgreSQL connection details. If you used the `docker-compose.yml` to start a PostgreSQL instance, the default URL would be `DATABASE_URL="postgresql://user:password@localhost:5432/portfolio_db"` (assuming the service is named `db` and exposed on `localhost:5432`, and you've configured these credentials in `docker-compose.yml`).

4. Apply database migrations (ensure you are in the `backend` directory and your virtual environment is activated):
   ```bash
   alembic upgrade head
   ```
   (If `alembic` command is not found directly, try `python -m alembic upgrade head`)

5. Start the Flask server:
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

## Testing

### Backend Tests

The backend includes a comprehensive test suite that can be run using the `run_tests.py` script:

```bash
cd backend
python run_tests.py
```

#### Unit Tests
- `tests/unit/test_portfolio_model.py` - Tests for portfolio model operations
- `tests/unit/test_asset_routes.py` - Tests for asset route handlers
  - Tests asset creation, retrieval, updates using an in-memory SQLite database
  - Single and bulk deletion
  - Input validation
  - Error handling

#### Integration Tests
- `tests/integration/test_api_integration.py` - End-to-end API workflow tests
  - Complete CRUD operations for assets
  - Bulk operations
  - API response format validation
  - Error scenarios

### Frontend Tests

Frontend tests are implemented using React Testing Library and Jest:

```bash
cd frontend
npm test
```

#### Component Tests
- `src/tests/unit/App.test.js` - Tests for the main App component
- `src/tests/unit/AssetList.test.js` - Tests for the asset list component
  - Asset rendering
  - Inline editing
  - Deletion operations
  - Bulk selection and deletion

#### Integration Tests
- `src/tests/integration/AppIntegration.test.js` - Tests for component interactions
  - API integration
  - State management
  - User interactions
  - Error handling

## Future Enhancements

- User authentication and user-specific portfolios
- Historical performance tracking and visualization
- Advanced charting and technical analysis
- Database integration for persistent storage
- Mobile application
- API key management for higher rate limits

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
