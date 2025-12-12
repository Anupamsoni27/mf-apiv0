
import unittest
import sys
import os
from unittest.mock import MagicMock
import mongomock

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock pymongo before importing app
mock_pymongo = MagicMock()
mock_pymongo.MongoClient = mongomock.MongoClient
sys.modules['pymongo'] = mock_pymongo

# Verify bson import works or is available
try:
    import bson
except ImportError:
    pass

# Import app - this will use the mocked MongoClient
from app import app, favorites, stocks, fund_holdings, users

class TestFavorites(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        # Clear collections in the mock DB
        favorites.delete_many({})
        stocks.delete_many({})
        fund_holdings.delete_many({})
        users.delete_many({})
        
        # Setup test data
        self.user_id = "test_user_001"
        self.stock_data = {"name": "Test Stock", "symbol": "TEST"}
        self.stock_id = str(stocks.insert_one(self.stock_data).inserted_id)

    def test_add_favorite_stock(self):
        print("\nTesting Add Favorite Stock...")
        payload = {
            "userId": self.user_id,
            "itemId": self.stock_id,
            "itemType": "stock"
        }
        response = self.client.post('/api/favorites', json=payload)
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Added')
        
        # Verify in DB
        fav = favorites.find_one({"userId": self.user_id, "itemId": self.stock_id})
        self.assertIsNotNone(fav)
        print("Add Favorite Stock Passed")

    def test_add_duplicate_favorite(self):
        print("\nTesting Add Duplicate Favorite...")
        payload = {
            "userId": self.user_id,
            "itemId": self.stock_id,
            "itemType": "stock"
        }
        # Add once
        self.client.post('/api/favorites', json=payload)
        # Add again
        response = self.client.post('/api/favorites', json=payload)
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Already in favorites')
        print("Add Duplicate Favorite Passed")

    def test_get_favorite_stocks(self):
        print("\nTesting Get Favorite Stocks...")
        # Add favorite first
        favorites.insert_one({
            "userId": self.user_id,
            "itemId": self.stock_id,
            "itemType": "stock"
        })
        
        response = self.client.get(f'/api/favorites/stocks?userId={self.user_id}')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['records']), 1)
        self.assertEqual(data['records'][0]['_id'], self.stock_id)
        print("Get Favorite Stocks Passed")

    def test_remove_favorite(self):
        print("\nTesting Remove Favorite...")
        # Add favorite
        favorites.insert_one({
            "userId": self.user_id,
            "itemId": self.stock_id,
            "itemType": "stock"
        })
        
        # Remove
        response = self.client.delete(f'/api/favorites/{self.stock_id}?userId={self.user_id}&type=stock')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Removed')
        
        # Verify gone
        fav = favorites.find_one({"userId": self.user_id, "itemId": self.stock_id})
        self.assertIsNone(fav)
        print("Remove Favorite Passed")
        
    def test_remove_nonexistent_favorite(self):
        print("\nTesting Remove Non-Existent Favorite...")
        response = self.client.delete(f'/api/favorites/{self.stock_id}?userId={self.user_id}&type=stock')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'Favorite not found')
        print("Remove Non-Existent Favorite Passed")

if __name__ == '__main__':
    unittest.main()
