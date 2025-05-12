import unittest
import json
# Removed: from unittest.mock import patch, MagicMock
from backend import create_app
from backend.models import db, Asset # Added db, Asset
from backend.config.settings import ASSET_TYPE_INDIAN_STOCK, ASSET_TYPE_US_STOCK, ASSET_TYPE_CRYPTO
from datetime import datetime

class TestAssetRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test client and in-memory database"""
        self.app = create_app(config_override={
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False # Good practice to set this explicitly
        })
        # self.app.config['TESTING'] = True # Now set via create_app
        # self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Now set via create_app
        self.client = self.app.test_client()

        with self.app.app_context(): # Create app context
            db.create_all() # Create database tables
        
        # No need for self.test_asset or self.test_assets mock data here
        # We will create real Asset objects in the DB for each test as needed

    def tearDown(self):
        """Clean up database after each test"""
        with self.app.app_context():
            db.session.remove() # Ensure session is clean
            db.drop_all() # Drop all tables
    
    # Removed @patch decorator
    def test_get_assets(self):
        """Test GET /assets/ endpoint"""
        with self.app.app_context():
            asset1 = Asset(symbol='TEST1', asset_type=ASSET_TYPE_INDIAN_STOCK, purchase_price=100.0, quantity=10, purchase_date=datetime.strptime('2023-01-01', '%Y-%m-%d'))
            asset2 = Asset(symbol='TEST2', asset_type=ASSET_TYPE_US_STOCK, purchase_price=200.0, quantity=5, purchase_date=datetime.strptime('2023-02-01', '%Y-%m-%d'))
            db.session.add_all([asset1, asset2])
            db.session.commit()
        
        response = self.client.get('/assets/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['symbol'], 'TEST1')
        self.assertEqual(data[1]['symbol'], 'TEST2')
    
    # Removed @patch decorator
    def test_get_asset(self):
        """Test GET /assets/<asset_id> endpoint"""
        with self.app.app_context():
            asset = Asset(symbol='TEST1', asset_type=ASSET_TYPE_INDIAN_STOCK, purchase_price=100.0, quantity=10, purchase_date=datetime.strptime('2023-01-01', '%Y-%m-%d'))
            db.session.add(asset)
            db.session.commit()
            asset_id = asset.id # Get the actual ID after commit
        
        response = self.client.get(f'/assets/{asset_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['symbol'], 'TEST1')
        self.assertEqual(data['id'], asset_id)
        
        # Test non-existent asset (ID that likely won't exist)
        response = self.client.get('/assets/99999')
        self.assertEqual(response.status_code, 404)
    
    # Removed @patch decorator
    def test_add_asset(self):
        """Test POST /assets/ endpoint"""
        new_asset_data = {
            "symbol": "TESTADD",
            "asset_type": ASSET_TYPE_CRYPTO,
            "purchase_price": 50000.0,
            "quantity": 1,
            "purchase_date": "2023-03-01" # String format as expected by API
        }
        
        response = self.client.post(
            '/assets/',
            data=json.dumps(new_asset_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['symbol'], 'TESTADD')
        self.assertIsNotNone(data['id']) # Check if ID is assigned

        with self.app.app_context():
            added_asset = Asset.query.filter_by(symbol='TESTADD').first()
            self.assertIsNotNone(added_asset)
            self.assertEqual(added_asset.purchase_price, 50000.0)
        
        # Test invalid data (missing fields)
        invalid_asset = {
            "symbol": "TESTFAIL",
            # "asset_type": ASSET_TYPE_CRYPTO, # Missing asset_type
            "purchase_price": 100.0,
            "quantity": 1,
            "purchase_date": "2023-03-01"
        }
        response = self.client.post(
            '/assets/',
            data=json.dumps(invalid_asset),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        # Test invalid purchase_date format
        invalid_date_asset = {
            "symbol": "TESTDATEFAIL",
            "asset_type": ASSET_TYPE_CRYPTO,
            "purchase_price": 100.0,
            "quantity": 1,
            "purchase_date": "01-03-2023" # Wrong format
        }
        response = self.client.post(
            '/assets/',
            data=json.dumps(invalid_date_asset),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("YYYY-MM-DD format", json.loads(response.data).get("error", ""))
    
    # Removed @patch decorator
    def test_update_asset(self):
        """Test PUT /assets/<asset_id> endpoint"""
        with self.app.app_context():
            asset = Asset(symbol='TESTUPDATE', asset_type=ASSET_TYPE_INDIAN_STOCK, purchase_price=100.0, quantity=10, purchase_date=datetime.strptime('2023-01-01', '%Y-%m-%d'))
            db.session.add(asset)
            db.session.commit()
            asset_id = asset.id

        updated_data = {
            "symbol": "TESTUPDATE_NEW",
            "asset_type": ASSET_TYPE_US_STOCK, 
            "purchase_price": 1100.0,
            "quantity": 12,
            "purchase_date": "2023-01-15" # String format
        }
        
        response = self.client.put(
            f'/assets/{asset_id}',
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['symbol'], 'TESTUPDATE_NEW')
        self.assertEqual(data['purchase_price'], 1100.0)
        self.assertEqual(data['quantity'], 12)
        self.assertEqual(data['asset_type'], ASSET_TYPE_US_STOCK)
        self.assertTrue(data['purchase_date'].startswith('2023-01-15'))

        with self.app.app_context():
            updated_db_asset = db.session.get(Asset, asset_id)
            self.assertEqual(updated_db_asset.symbol, 'TESTUPDATE_NEW')
            self.assertEqual(updated_db_asset.purchase_price, 1100.0)
        
        # Test non-existent asset
        response = self.client.put(
            '/assets/99999',
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
    
    # Removed @patch decorator
    def test_delete_asset(self):
        """Test DELETE /assets/<asset_id> endpoint"""
        with self.app.app_context():
            asset = Asset(symbol='TESTDELETE', asset_type=ASSET_TYPE_INDIAN_STOCK, purchase_price=100.0, quantity=10, purchase_date=datetime.strptime('2023-01-01', '%Y-%m-%d'))
            db.session.add(asset)
            db.session.commit()
            asset_id = asset.id
        
        response = self.client.delete(f'/assets/{asset_id}')
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertIsNone(db.session.get(Asset, asset_id))
        
        # Test non-existent asset
        response = self.client.delete('/assets/99999')
        self.assertEqual(response.status_code, 404)
    
    # Removed @patch decorator
    def test_bulk_delete_assets(self):
        """Test DELETE /assets/ endpoint (bulk delete)"""
        with self.app.app_context():
            asset1 = Asset(symbol='BULK1', asset_type=ASSET_TYPE_INDIAN_STOCK, purchase_price=100.0, quantity=10, purchase_date=datetime.strptime('2023-01-01', '%Y-%m-%d'))
            asset2 = Asset(symbol='BULK2', asset_type=ASSET_TYPE_US_STOCK, purchase_price=200.0, quantity=5, purchase_date=datetime.strptime('2023-02-01', '%Y-%m-%d'))
            asset3 = Asset(symbol='BULK3', asset_type=ASSET_TYPE_CRYPTO, purchase_price=300.0, quantity=2, purchase_date=datetime.strptime('2023-03-01', '%Y-%m-%d'))
            db.session.add_all([asset1, asset2, asset3])
            db.session.commit()
            asset1_id = asset1.id # Store ID after commit
            asset2_id = asset2.id # Store ID after commit
            asset3_id = asset3.id # Store ID after commit
            ids_to_delete_payload = {"ids": [asset1_id, asset2_id]}
        
        response = self.client.delete(
            '/assets/',
            data=json.dumps(ids_to_delete_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['message'], "2 assets deleted successfully")

        with self.app.app_context():
            self.assertIsNone(db.session.get(Asset, asset1_id))
            self.assertIsNone(db.session.get(Asset, asset2_id))
            self.assertIsNotNone(db.session.get(Asset, asset3_id)) # asset3 should still exist
        
        # Test invalid request body (e.g. non-integer IDs)
        invalid_ids_payload = {"ids": ["abc", asset3_id]}
        response = self.client.delete(
            '/assets/',
            data=json.dumps(invalid_ids_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("All asset IDs must be integers", json.loads(response.data).get("error", ""))

        # Test empty list of IDs
        empty_ids_payload = {"ids": []}
        response = self.client.delete(
            '/assets/',
            data=json.dumps(empty_ids_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data).get("message", ""), "No asset IDs provided for deletion")


if __name__ == '__main__':
    unittest.main()
