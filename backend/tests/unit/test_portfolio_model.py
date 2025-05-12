import unittest
import uuid
from backend.models import portfolio
from backend.config.settings import ASSET_TYPE_INDIAN_STOCK, ASSET_TYPE_US_STOCK, ASSET_TYPE_CRYPTO

class TestPortfolioModel(unittest.TestCase):
    def setUp(self):
        """Save the original portfolio and set up a test portfolio"""
        self.original_portfolio = portfolio._portfolio.copy()
        # Clear the portfolio for testing
        portfolio._portfolio = []
        
        # Add some test assets
        self.test_assets = [
            {
                "symbol": "TEST1",
                "asset_type": ASSET_TYPE_INDIAN_STOCK,
                "purchase_price": 1000.0,
                "quantity": 10,
                "purchase_date": "2023-01-01"
            },
            {
                "symbol": "TEST2",
                "asset_type": ASSET_TYPE_US_STOCK,
                "purchase_price": 200.0,
                "quantity": 5,
                "purchase_date": "2023-02-01"
            },
            {
                "symbol": "TEST3",
                "asset_type": ASSET_TYPE_CRYPTO,
                "purchase_price": 50000.0,
                "quantity": 0.1,
                "purchase_date": "2023-03-01"
            }
        ]
        
        # Add test assets to the portfolio
        self.asset_ids = []
        for asset in self.test_assets:
            added_asset = portfolio.add_asset(asset)
            self.asset_ids.append(added_asset["id"])
    
    def tearDown(self):
        """Restore the original portfolio after tests"""
        portfolio._portfolio = self.original_portfolio
    
    def test_get_all_assets(self):
        """Test getting all assets from the portfolio"""
        assets = portfolio.get_all_assets()
        self.assertEqual(len(assets), 3)
        self.assertEqual(assets[0]["symbol"], "TEST1")
        self.assertEqual(assets[1]["symbol"], "TEST2")
        self.assertEqual(assets[2]["symbol"], "TEST3")
    
    def test_get_asset_by_id(self):
        """Test getting a specific asset by ID"""
        asset = portfolio.get_asset_by_id(self.asset_ids[0])
        self.assertIsNotNone(asset)
        self.assertEqual(asset["symbol"], "TEST1")
        
        # Test with non-existent ID
        asset = portfolio.get_asset_by_id(str(uuid.uuid4()))
        self.assertIsNone(asset)
    
    def test_add_asset(self):
        """Test adding a new asset to the portfolio"""
        new_asset_data = {
            "symbol": "TEST4",
            "asset_type": ASSET_TYPE_INDIAN_STOCK,
            "purchase_price": 500.0,
            "quantity": 20,
            "purchase_date": "2023-04-01"
        }
        
        new_asset = portfolio.add_asset(new_asset_data)
        self.assertIsNotNone(new_asset["id"])
        self.assertEqual(new_asset["symbol"], "TEST4")
        self.assertEqual(new_asset["purchase_price"], 500.0)
        self.assertEqual(new_asset["quantity"], 20.0)
        
        # Verify it was added to the portfolio
        assets = portfolio.get_all_assets()
        self.assertEqual(len(assets), 4)
    
    def test_update_asset(self):
        """Test updating an existing asset"""
        asset_id = self.asset_ids[1]
        updated_data = {
            "symbol": "TEST2",
            "asset_type": ASSET_TYPE_US_STOCK,
            "purchase_price": 250.0,  # Changed from 200.0
            "quantity": 8,  # Changed from 5
            "purchase_date": "2023-02-15"  # Changed from 2023-02-01
        }
        
        updated_asset = portfolio.update_asset(asset_id, updated_data)
        self.assertIsNotNone(updated_asset)
        self.assertEqual(updated_asset["purchase_price"], 250.0)
        self.assertEqual(updated_asset["quantity"], 8.0)
        self.assertEqual(updated_asset["purchase_date"], "2023-02-15")
        
        # Test with non-existent ID
        result = portfolio.update_asset(str(uuid.uuid4()), updated_data)
        self.assertIsNone(result)
    
    def test_delete_asset(self):
        """Test deleting an asset from the portfolio"""
        asset_id = self.asset_ids[2]
        result = portfolio.delete_asset(asset_id)
        self.assertTrue(result)
        
        # Verify it was removed
        assets = portfolio.get_all_assets()
        self.assertEqual(len(assets), 2)
        
        # Test deleting non-existent asset
        result = portfolio.delete_asset(str(uuid.uuid4()))
        self.assertFalse(result)
    
    def test_bulk_delete_assets(self):
        """Test deleting multiple assets at once"""
        # Delete the first two assets
        ids_to_delete = [self.asset_ids[0], self.asset_ids[1]]
        deleted_count = portfolio.bulk_delete_assets(ids_to_delete)
        
        self.assertEqual(deleted_count, 2)
        
        # Verify they were removed
        assets = portfolio.get_all_assets()
        self.assertEqual(len(assets), 1)
        self.assertEqual(assets[0]["id"], self.asset_ids[2])
        
        # Test with non-existent IDs
        deleted_count = portfolio.bulk_delete_assets([str(uuid.uuid4()), str(uuid.uuid4())])
        self.assertEqual(deleted_count, 0)

if __name__ == '__main__':
    unittest.main()
