import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
import sys

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_processing.csv_bill_loader import BillDataManager

class TestCSVBillLoader(unittest.TestCase):
    
    def setUp(self):
        # Create sample data for testing
        self.sample_data = pd.DataFrame({
            'Account': ['A001', 'A002', 'A003'],
            'Jan': [100.50, -25.30, 0.00],
            'Feb': [120.75, -15.20, 10.50],
            'Mar': [95.25, 0.00, 22.75]
        })
    
    @patch('pandas.read_csv')
    def test_load_data(self, mock_read_csv):
        # Mock the read_csv function
        mock_read_csv.return_value = self.sample_data
        
        # Create an instance of BillDataManager
        manager = BillDataManager()
        
        # Test loading data
        result = manager.load_data('dummy_path.csv')
        
        # Verify the result
        self.assertTrue(result)
        self.assertIsNotNone(manager.data)
        
        # Check that column names were converted to lowercase
        self.assertIn('account', manager.data.columns)
        self.assertIn('jan', manager.data.columns)
    
    def test_get_all_accounts(self):
        # Create an instance with our sample data
        manager = BillDataManager()
        manager.data = self.sample_data.copy()
        manager.data.columns = [col.lower() for col in manager.data.columns]
        
        # Test getting all accounts
        accounts = manager.get_all_accounts()
        
        # Verify the result
        self.assertEqual(len(accounts), 3)
        self.assertIn('A001', accounts)
        self.assertIn('A002', accounts)
        self.assertIn('A003', accounts)
    
    def test_get_account_data(self):
        # Create an instance with our sample data
        manager = BillDataManager()
        manager.data = self.sample_data.copy()
        manager.data.columns = [col.lower() for col in manager.data.columns]
        
        # Test getting data for a specific account
        account_data = manager.get_account_data('A002')
        
        # Verify the result
        self.assertIsNotNone(account_data)
        self.assertEqual(len(account_data), 1)
        self.assertEqual(account_data.iloc[0]['jan'], -25.30)
        self.assertEqual(account_data.iloc[0]['feb'], -15.20)
        self.assertEqual(account_data.iloc[0]['mar'], 0.00)
    
    def test_get_monthly_bills(self):
        # Create an instance with our sample data
        manager = BillDataManager()
        manager.data = self.sample_data.copy()
        manager.data.columns = [col.lower() for col in manager.data.columns]
        
        # Test getting monthly bills for a specific account
        monthly_bills = manager.get_monthly_bills('A001')
        
        # Verify the result
        self.assertIsNotNone(monthly_bills)
        self.assertIn('jan', monthly_bills.columns)
        self.assertIn('feb', monthly_bills.columns)
        self.assertIn('mar', monthly_bills.columns)

if __name__ == '__main__':
    unittest.main() 