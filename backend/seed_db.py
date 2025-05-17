from datetime import datetime, timedelta
import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import the app and db
from app import create_app
from backend import db
from backend.models.asset import Asset

def seed_database():
    app = create_app()
    
    with app.app_context():
        # Initialize the database
        db.create_all()
        
        # Clear existing data
        db.session.query(Asset).delete()
        
        # Add sample assets
        assets = [
            {
                'symbol': 'RELIANCE.NS',
                'asset_type': 'Indian Stock',
                'quantity': 10,
                'purchase_price': 2450.50,
                'purchase_date': (datetime.now() - timedelta(days=90)).isoformat(),
                'last_price': 2800.00,
                'last_price_updated': datetime.now().isoformat()
            },
            {
                'symbol': 'TCS.NS',
                'asset_type': 'Indian Stock',
                'quantity': 5,
                'purchase_price': 3200.75,
                'purchase_date': (datetime.now() - timedelta(days=60)).isoformat(),
                'last_price': 3400.50,
                'last_price_updated': datetime.now().isoformat()
            },
            {
                'symbol': 'AAPL',
                'asset_type': 'US Stock',
                'quantity': 2,
                'purchase_price': 170.25,
                'purchase_date': (datetime.now() - timedelta(days=30)).isoformat(),
                'last_price': 185.30,
                'last_price_updated': datetime.now().isoformat()
            },
            {
                'symbol': 'BTC',
                'asset_type': 'Crypto',
                'quantity': 0.5,
                'purchase_price': 40000.00,
                'purchase_date': (datetime.now() - timedelta(days=120)).isoformat(),
                'last_price': 65000.00,
                'last_price_updated': datetime.now().isoformat()
            }
        ]
        
        # Add assets to database
        for asset_data in assets:
            asset = Asset(
                symbol=asset_data['symbol'],
                asset_type=asset_data['asset_type'],
                quantity=asset_data['quantity'],
                purchase_price=asset_data['purchase_price'],
                purchase_date=datetime.fromisoformat(asset_data['purchase_date']),
                last_price=asset_data['last_price'],
                last_price_updated=datetime.fromisoformat(asset_data['last_price_updated'])
            )
            db.session.add(asset)
        
        # Commit the changes
        db.session.commit()
        print("✅ Database seeded with sample data!")

if __name__ == '__main__':
    seed_database()
