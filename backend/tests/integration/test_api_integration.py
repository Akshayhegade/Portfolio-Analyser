import unittest
import json
import uuid
from backend import create_app
from backend.models import portfolio
from backend.config.settings import ASSET_TYPE_INDIAN_STOCK, ASSET_TYPE_US_STOCK, ASSET_TYPE_CRYPTO

class TestAPIIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test client and initialize test data"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Save original portfolio
        self.original_portfolio = portfolio._portfolio.copy()
        
        # Clear the portfolio for testing
        portfolio._portfolio = []
        
        # Add test assets
        self.test_assets = [
            {
                "symbol": "INFY.NS",
                "asset_type": ASSET_TYPE_INDIAN_STOCK,
                "purchase_price": 1500.0,
                "quantity": 10,
                "purchase_date": "2023-01-15"
            },
            {
                "symbol": "AAPL",
                "asset_type": ASSET_TYPE_US_STOCK,
                "purchase_price": 14000.0,
                "quantity": 5,
                "purchase_date": "2023-02-20"
            },
            {
                "symbol": "BTC",
                "asset_type": ASSET_TYPE_CRYPTO,
                "purchase_price": 2500000.0,
                "quantity": 0.05,
                "purchase_date": "2023-03-25"
            }
        ]
        
        # Add test assets and store their IDs
        self.asset_ids = []
        for asset in self.test_assets:
            response = self.client.post(
                '/assets/',
                data=json.dumps(asset),
                content_type='application/json'
            )
            data = json.loads(response.data)
            self.asset_ids.append(data['id'])
    
    def tearDown(self):
        """Restore original portfolio after tests"""
        portfolio._portfolio = self.original_portfolio
    
    def test_full_asset_lifecycle(self):
        """Test the complete lifecycle of assets: create, read, update, delete"""
        # 1. Verify all assets were created in setUp
        response = self.client.get('/assets/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
        
        # 2. Get a specific asset
        asset_id = self.asset_ids[0]
        response = self.client.get(f'/assets/{asset_id}')
        self.assertEqual(response.status_code, 200)
        asset = json.loads(response.data)
        self.assertEqual(asset['symbol'], 'INFY.NS')
        
        # 3. Update an asset
        updated_data = {
            "symbol": "INFY.NS",
            "asset_type": ASSET_TYPE_INDIAN_STOCK,
            "purchase_price": 1600.0,  # Changed from 1500.0
            "quantity": 12,  # Changed from 10
            "purchase_date": "2023-01-20"  # Changed from 2023-01-15
        }
        
        response = self.client.put(
            f'/assets/{asset_id}',
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        updated_asset = json.loads(response.data)
        self.assertEqual(updated_asset['purchase_price'], 1600.0)
        self.assertEqual(updated_asset['quantity'], 12.0)
        
        # 4. Delete one asset
        response = self.client.delete(f'/assets/{self.asset_ids[2]}')
        self.assertEqual(response.status_code, 200)
        
        # Verify it was deleted
        response = self.client.get('/assets/')
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        
        # 5. Bulk delete remaining assets
        response = self.client.delete(
            '/assets/',
            data=json.dumps({"ids": [self.asset_ids[0], self.asset_ids[1]]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn("2 assets deleted successfully", result['message'])
        
        # Verify all assets are gone
        response = self.client.get('/assets/')
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)
    
    def test_error_handling(self):
        """Test API error handling"""
        # 1. Try to get non-existent asset
        non_existent_id = str(uuid.uuid4())
        response = self.client.get(f'/assets/{non_existent_id}')
        self.assertEqual(response.status_code, 404)
        
        # 2. Try to update non-existent asset
        updated_data = {
            "symbol": "FAKE",
            "asset_type": ASSET_TYPE_INDIAN_STOCK,
            "purchase_price": 1000.0,
            "quantity": 10,
            "purchase_date": "2023-01-01"
        }
        
        response = self.client.put(
            f'/assets/{non_existent_id}',
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        
        # 3. Try to add asset with invalid data
        invalid_asset = {
            "symbol": "TEST",
            "asset_type": "Invalid Type",  # Invalid asset type
            "purchase_price": 1000.0,
            "quantity": 10,
            "purchase_date": "2023-01-01"
        }
        
        response = self.client.post(
            '/assets/',
            data=json.dumps(invalid_asset),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # 4. Try bulk delete with invalid format
        response = self.client.delete(
            '/assets/',
            data=json.dumps({"invalid_key": [self.asset_ids[0]]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
