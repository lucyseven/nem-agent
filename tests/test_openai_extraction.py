import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pdf_processing.pdf_extractor import extract_with_openai

class TestOpenAIExtraction(unittest.TestCase):
    
    @patch('openai.ChatCompletion.create')
    def test_extract_with_openai(self, mock_openai):
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='''```json
{
  "bill_summary": {
    "account_number": "123456789",
    "billing_period": "July 1, 2024 to July 31, 2024",
    "previous_balance": "-39.59",
    "payment_received": "0.00",
    "credit_balance": "-39.59",
    "current_charges": "22.57",
    "total_amount_due": "-17.02"
  },
  "charges_breakdown": [
    {"charge_type": "Electricity Used (Net Usage)", "amount": "5 kWh"},
    {"charge_type": "Electricity Delivery Charges", "amount": "31.47"},
    {"charge_type": "Non-Bypassable Charges", "amount": "8.77"},
    {"charge_type": "Wildfire Fund Charge", "amount": "2.93"},
    {"charge_type": "Electricity Generation Charges", "amount": "33.29"},
    {"charge_type": "Electricity Generation Credit", "amount": "-33.29"},
    {"charge_type": "Baseline Adjustment Credit", "amount": "-12.57"},
    {"charge_type": "Other Adjustments", "amount": "-19.77"},
    {"charge_type": "Minimum Charge Adjustment", "amount": "10.87"},
    {"charge_type": "Taxes & Fees", "amount": "0.00"}
  ]
}
```'''
                )
            )
        ]
        mock_openai.return_value = mock_response
        
        # Test with sample bill text
        sample_text = """
        Monthly NEM Bill (July 2024)
        Account Number: 123456789
        Previous Balance: -$39.59 (credit)
        Payment Received: $0.00
        Credit Balance: -$39.59
        Current Charges: $22.57
        Total Amount Due: -$17.02 (Credit, meaning no payment is required)
        Breakdown of Charges:

        Electricity Used (Net Usage): 5 kWh
        Electricity Delivery Charges: $31.47
        Non-Bypassable Charges: $8.77
        Wildfire Fund Charge: $2.93
        Electricity Generation Charges: $33.29
        Electricity Generation Credit: -$33.29
        Baseline Adjustment Credit: -$12.57
        Other Adjustments: -$19.77
        Minimum Charge Adjustment: $10.87
        Taxes & Fees: $0.00
        """
        
        result = extract_with_openai(sample_text)
        
        # Verify the result
        self.assertEqual(result["bill_summary"]["account_number"], "123456789")
        self.assertEqual(result["bill_summary"]["total_amount_due"], "-17.02")
        self.assertEqual(len(result["charges_breakdown"]), 10)
        self.assertEqual(result["charges_breakdown"][0]["charge_type"], "Electricity Used (Net Usage)")
        self.assertEqual(result["charges_breakdown"][0]["amount"], "5 kWh")

if __name__ == '__main__':
    unittest.main() 