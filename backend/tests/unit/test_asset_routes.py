import unittest
import json
from unittest.mock import patch, MagicMock
from backend import create_app
from backend.config.settings import ASSET_TYPE_INDIAN_STOCK, ASSET_TYPE_US_STOCK, ASSET_TYPE_CRYPTO

class TestAssetRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test client"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Mock data for tests
        self.test_asset = {
            "id": "test-id-1",
            "symbol": "TEST1",
            "asset_type": ASSET_TYPE_INDIAN_STOCK,
            "purchase_price": 1000.0,
            "quantity": 10,
            "purchase_date": "2023-01-01"
        }
        
        self.test_assets = [
            self.test_asset,
            {
                "id": "test-id-2",
                "symbol": "TEST2",
                "asset_type": ASSET_TYPE_US_STOCK,
                "purchase_price": 200.0,
                "quantity": 5,
                "purchase_date": "2023-02-01"
            }
        ]
    
    @patch('backend.routes.assets.portfolio.get_all_assets')
    def test_get_assets(self, mock_get_all_assets):
        """Test GET /assets/ endpoint"""
        mock_get_all_assets.return_value = self.test_assets
        
        response = self.client.get('/assets/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['symbol'], 'TEST1')
        self.assertEqual(data[1]['symbol'], 'TEST2')
    
    @patch('backend.routes.assets.portfolio.get_asset_by_id')
    def test_get_asset(self, mock_get_asset_by_id):
        """Test GET /assets/<asset_id> endpoint"""
        mock_get_asset_by_id.return_value = self.test_asset
        
        response = self.client.get('/assets/test-id-1')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['symbol'], 'TEST1')
        
        # Test non-existent asset
        mock_get_asset_by_id.return_value = None
        response = self.client.get('/assets/non-existent-id')
        self.assertEqual(response.status_code, 404)
    
    @patch('backend.routes.assets.portfolio.add_asset')
    def test_add_asset(self, mock_add_asset):
        """Test POST /assets/ endpoint"""
        mock_add_asset.return_value = self.test_asset
        
        new_asset = {
            "symbol": "TEST1",
            "asset_type": ASSET_TYPE_INDIAN_STOCK,
            "purchase_price": 1000.0,
            "quantity": 10,
            "purchase_date": "2023-01-01"
        }
        
        response = self.client.post(
            '/assets/',
            data=json.dumps(new_asset),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['symbol'], 'TEST1')
        
        # Test invalid data
        invalid_asset = {
            "symbol": "TEST1",
            # Missing required fields
        }
        
        response = self.client.post(
            '/assets/',
            data=json.dumps(invalid_asset),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    @patch('backend.routes.assets.portfolio.update_asset')
    def test_update_asset(self, mock_update_asset):
        """Test PUT /assets/<asset_id> endpoint"""
        mock_update_asset.return_value = {
            "id": "test-id-1",
            "symbol": "TEST1",
            "asset_type": ASSET_TYPE_INDIAN_STOCK,
            "purchase_price": 1100.0,  # Updated price
            "quantity": 12,  # Updated quantity
            "purchase_date": "2023-01-15"  # Updated date
        }
        
        updated_data = {
            "symbol": "TEST1",
            "asset_type": ASSET_TYPE_INDIAN_STOCK,
            "purchase_price": 1100.0,
            "quantity": 12,
            "purchase_date": "2023-01-15"
        }
        
        response = self.client.put(
            '/assets/test-id-1',
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['purchase_price'], 1100.0)
        self.assertEqual(data['quantity'], 12)
        
        # Test non-existent asset
        mock_update_asset.return_value = None
        response = self.client.put(
            '/assets/non-existent-id',
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
    
    @patch('backend.routes.assets.portfolio.delete_asset')
    def test_delete_asset(self, mock_delete_asset):
        """Test DELETE /assets/<asset_id> endpoint"""
        mock_delete_asset.return_value = True
        
        response = self.client.delete('/assets/test-id-1')
        self.assertEqual(response.status_code, 200)
        
        # Test non-existent asset
        mock_delete_asset.return_value = False
        response = self.client.delete('/assets/non-existent-id')
        self.assertEqual(response.status_code, 404)
    
    @patch('backend.routes.assets.portfolio.bulk_delete_assets')
    def test_bulk_delete_assets(self, mock_bulk_delete_assets):
        """Test DELETE /assets/ endpoint (bulk delete)"""
        mock_bulk_delete_assets.return_value = 2
        
        ids_to_delete = {
            "ids": ["test-id-1", "test-id-2"]
        }
        
        response = self.client.delete(
            '/assets/',
            data=json.dumps(ids_to_delete),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn("2 assets deleted successfully", data['message'])
        
        # Test invalid request body
        invalid_data = {
            "not_ids": ["test-id-1"]  # Wrong key
        }
        
        response = self.client.delete(
            '/assets/',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
