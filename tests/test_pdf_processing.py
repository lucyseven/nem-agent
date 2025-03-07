import unittest
from unittest.mock import patch, MagicMock
import io
import os
import sys
import matplotlib
import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pdf_processing.pdf_extractor import extract_bill_data, BillParser
from src.pdf_processing.parser_rules import ParserRuleSet

class TestPDFProcessing(unittest.TestCase):
    
    def test_extract_pattern(self):
        """Test the pattern extraction functionality."""
        parser = BillParser()
        
        # Test account number extraction
        text = "Account Number: 123456789"
        result = parser.extract_pattern(text, parser.patterns['account_number'])
        self.assertEqual(result, "123456789")
        
        # Test billing period extraction
        text = "Billing Period: January 1, 2023 to January 31, 2023"
        result = parser.extract_pattern(text, parser.patterns['billing_period'])
        self.assertEqual(result, "January 1, 2023 to January 31, 2023")
        
        # Test total amount extraction
        text = "Total Amount Due: $123.45"
        result = parser.extract_pattern(text, parser.patterns['total_amount'])
        self.assertEqual(result, "123.45")
        
        # Test with no match
        text = "This text doesn't contain the pattern"
        result = parser.extract_pattern(text, parser.patterns['account_number'])
        self.assertIsNone(result)
    
    @patch('pdfplumber.open')
    def test_extract_bill_data(self, mock_pdf_open):
        """Test the main extract_bill_data function with a mock PDF."""
        # Create a mock PDF object
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
        Account Number: 123456789
        Billing Period: January 1, 2023 to January 31, 2023
        Total Amount Due: $123.45
        Due Date: February 15, 2023
        Total kWh Used: 500
        Generation Charges: $75.00
        Delivery Charges: $48.45
        NEM Credits: $0.00
        """
        mock_page.extract_tables.return_value = []
        mock_pdf.pages = [mock_page]
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf
        
        # Create a mock file
        mock_file = io.BytesIO(b"mock pdf content")
        
        # Call the function
        result = extract_bill_data(mock_file)
        
        # Check the results
        self.assertEqual(result['account_info']['account_number'], "123456789")
        self.assertEqual(result['billing_summary']['billing_period'], "January 1, 2023 to January 31, 2023")
        self.assertEqual(result['billing_summary']['total_amount'], "123.45")
        self.assertEqual(result['billing_summary']['due_date'], "February 15, 2023")
        self.assertEqual(result['energy_usage']['total_kwh'], "500")
        
        # Check charges
        self.assertEqual(len(result['charges']['breakdown']), 2)
        self.assertEqual(result['charges']['breakdown'][0]['type'], "Generation Charges")
        self.assertEqual(result['charges']['breakdown'][0]['amount'], "75.00")
        self.assertEqual(result['charges']['breakdown'][1]['type'], "Delivery Charges")
        self.assertEqual(result['charges']['breakdown'][1]['amount'], "48.45")
        
        # Check NEM details
        self.assertEqual(result['nem_details']['credits'], "0.00")
    
    def test_parser_rules(self):
        """Test the utility-specific parser rules."""
        # Test SDGE rules
        sdge_rules = ParserRuleSet("sdge")
        self.assertEqual(sdge_rules.utility_name, "sdge")
        self.assertIn('account_number', sdge_rules.patterns)
        
        # Test PG&E rules
        pge_rules = ParserRuleSet("pge")
        self.assertEqual(pge_rules.utility_name, "pge")
        self.assertIn('account_number', pge_rules.patterns)
        
        # Test SCE rules
        sce_rules = ParserRuleSet("sce")
        self.assertEqual(sce_rules.utility_name, "sce")
        self.assertIn('account_number', sce_rules.patterns)
        
        # Test generic rules
        generic_rules = ParserRuleSet("unknown")
        self.assertEqual(generic_rules.utility_name, "unknown")
        self.assertIn('account_number', generic_rules.patterns)

def visualize_bill_data(bill_data: dict):
    """
    Create visualizations for the extracted bill data.
    
    Args:
        bill_data: The structured bill data from extract_bill_data
    """
    if 'error' in bill_data:
        st.error(f"Error processing bill: {bill_data['error']}")
        return
    
    # Display bill summary
    st.subheader("📋 Bill Summary")
    summary = bill_data.get('summary', {})
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Account Number", summary.get('account_number', 'N/A'))
        st.metric("Billing Period", summary.get('billing_period', 'N/A'))
        st.metric("Due Date", summary.get('due_date', 'N/A'))
    
    with col2:
        st.metric("Total Amount Due", f"${summary.get('total_amount', 'N/A')}")
        st.metric("Total kWh Used", summary.get('total_kwh', 'N/A'))
    
    # Display charges breakdown
    st.subheader("💰 Charges Breakdown")
    charges = bill_data.get('charges', {}).get('breakdown', [])
    
    if charges:
        # Create DataFrame for charges
        charge_data = []
        for charge in charges:
            charge_type = charge.get('type', 'Unknown')
            amount = charge.get('amount', '0')
            # Convert amount to float if possible
            try:
                amount = float(amount.replace(',', '')) if isinstance(amount, str) else float(amount)
            except (ValueError, TypeError):
                amount = 0
            
            charge_data.append({
                'Charge Type': charge_type,
                'Amount': amount
            })
        
        if charge_data:
            df = pd.DataFrame(charge_data)
            
            # Display as table
            st.dataframe(df)
            
            # Create pie chart only if we have valid data
            if len(df) > 0 and df['Amount'].sum() > 0:
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.pie(df['Amount'], labels=df['Charge Type'], autopct='%1.1f%%', startangle=90)
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                plt.title('Charges Distribution')
                
                # Display the chart
                st.pyplot(fig)
            else:
                st.info("Cannot create chart: No charge amounts available.")
    else:
        st.info("No detailed charges breakdown available in this bill.")
    
    # Display NEM details if available
    nem_details = bill_data.get('nem_details', {})
    if nem_details:
        st.subheader("⚡ NEM Details")
        
        for key, value in nem_details.items():
            st.metric(key.replace('_', ' ').title(), value)

def get_monthly_comparison_chart(bills_data: list):
    """
    Create a comparison chart for multiple bills.
    
    Args:
        bills_data: List of bill data dictionaries
        
    Returns:
        HTML string with the embedded chart
    """
    # Extract relevant data from each bill
    months = []
    amounts = []
    usage = []
    
    for bill in bills_data:
        summary = bill.get('summary', {})
        billing_period = summary.get('billing_period', '')
        
        # Extract month from billing period
        month = billing_period.split('to')[0].strip().split(' ')[-1] if billing_period else 'Unknown'
        months.append(month)
        
        # Get amount and usage
        amount = summary.get('total_amount', '0')
        try:
            amount = float(amount.replace(',', '')) if isinstance(amount, str) else float(amount)
        except (ValueError, TypeError):
            amount = 0
        amounts.append(amount)
        
        kwh = summary.get('total_kwh', '0')
        try:
            kwh = float(kwh.replace(',', '')) if isinstance(kwh, str) else float(kwh)
        except (ValueError, TypeError):
            kwh = 0
        usage.append(kwh)
    
    # Check if we have valid data
    if not months or all(a == 0 for a in amounts) and all(u == 0 for u in usage):
        return "<p>No valid bill data available for comparison.</p>"
    
    # Create the chart
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Plot amount bars
    x = range(len(months))
    ax1.bar(x, amounts, alpha=0.7, color='blue', label='Bill Amount ($)')
    ax1.set_xlabel('Billing Period')
    ax1.set_ylabel('Amount ($)', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    
    # Create second y-axis for usage
    ax2 = ax1.twinx()
    ax2.plot(x, usage, 'r-', marker='o', linewidth=2, label='Energy Usage (kWh)')
    ax2.set_ylabel('Energy Usage (kWh)', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    
    # Set x-ticks to months
    plt.xticks(x, months)
    
    # Add title and legend
    plt.title('Monthly Bill Amount and Energy Usage')
    
    # Add legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    # Save to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Encode the image to base64
    img_str = base64.b64encode(buf.read()).decode()
    
    # Create HTML with the embedded image
    html = f'<img src="data:image/png;base64,{img_str}" width="100%">'
    
    return html

if __name__ == '__main__':
    print(matplotlib.__version__)
    unittest.main()
