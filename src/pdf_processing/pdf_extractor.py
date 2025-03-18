import pdfplumber
import re
import openai
import os
from typing import Dict, List, Any, Optional
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BillParser:
    """Parser for energy bills in PDF format."""
    
    def __init__(self):
        # Patterns to extract different types of information
        self.patterns = {
            'account_number': r'Account\s*Number[:\s]*([A-Za-z0-9-]+)',
            'billing_period': r'Billing\s*Period[:\s]*([A-Za-z0-9,\s]+to[A-Za-z0-9,\s]+)',
            'total_amount': r'Total\s*Amount\s*Due[:\s]*\$?([0-9,.]+)',
            'due_date': r'Due\s*Date[:\s]*([A-Za-z0-9,\s]+)',
            'energy_usage': r'Total\s*kWh\s*Used[:\s]*([0-9,.]+)',
            'generation_charges': r'Generation\s*Charges[:\s]*\$?([0-9,.]+)',
            'delivery_charges': r'Delivery\s*Charges[:\s]*\$?([0-9,.]+)',
            'nem_credits': r'NEM\s*Credits[:\s]*\$?([0-9,.]+)',
        }
    
    def extract_pattern(self, text: str, pattern: str) -> Optional[str]:
        """Extract information using regex pattern."""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
    
    def extract_table_data(self, pdf, page_num: int) -> List[Dict[str, Any]]:
        """Extract tabular data from a specific page."""
        try:
            page = pdf.pages[page_num]
            tables = page.extract_tables()
            
            if not tables:
                return []
                
            # Process tables into structured data
            result = []
            for table in tables:
                if not table or len(table) <= 1:  # Skip empty tables or just headers
                    continue
                    
                # Assume first row is headers
                headers = [h.strip() if h else f"Column_{i}" for i, h in enumerate(table[0])]
                
                for row in table[1:]:
                    if all(cell is None or cell.strip() == "" for cell in row):
                        continue  # Skip empty rows
                        
                    row_data = {}
                    for i, cell in enumerate(row):
                        if i < len(headers):
                            row_data[headers[i]] = cell.strip() if cell else None
                    
                    result.append(row_data)
            
            return result
        except Exception as e:
            logger.error(f"Error extracting table data: {e}")
            return []
    
    def parse_bill(self, pdf) -> Dict[str, Any]:
        """Parse the entire bill and extract structured information."""
        result = {
            'account_info': {},
            'billing_summary': {},
            'energy_usage': {},
            'charges': {
                'breakdown': [],
                'total': None
            },
            'nem_details': {}
        }
        
        # Extract text from all pages
        full_text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
        
        # Extract basic information using patterns
        result['account_info']['account_number'] = self.extract_pattern(full_text, self.patterns['account_number'])
        result['billing_summary']['billing_period'] = self.extract_pattern(full_text, self.patterns['billing_period'])
        result['billing_summary']['total_amount'] = self.extract_pattern(full_text, self.patterns['total_amount'])
        result['billing_summary']['due_date'] = self.extract_pattern(full_text, self.patterns['due_date'])
        result['energy_usage']['total_kwh'] = self.extract_pattern(full_text, self.patterns['energy_usage'])
        
        # Extract charges
        generation = self.extract_pattern(full_text, self.patterns['generation_charges'])
        if generation:
            result['charges']['breakdown'].append({
                'type': 'Generation Charges',
                'amount': generation
            })
            
        delivery = self.extract_pattern(full_text, self.patterns['delivery_charges'])
        if delivery:
            result['charges']['breakdown'].append({
                'type': 'Delivery Charges',
                'amount': delivery
            })
        
        # Extract NEM credits
        nem_credits = self.extract_pattern(full_text, self.patterns['nem_credits'])
        if nem_credits:
            result['nem_details']['credits'] = nem_credits
        
        # Try to extract detailed charges from tables
        for i in range(len(pdf.pages)):
            tables = self.extract_table_data(pdf, i)
            for table in tables:
                # Look for charge-related tables
                if any(key in str(table).lower() for key in ['charge', 'amount', 'rate', 'kwh']):
                    result['charges']['breakdown'].extend(self._process_charge_table(table))
        
        # Set total amount
        result['charges']['total'] = result['billing_summary']['total_amount']
        
        return result
    
    def _process_charge_table(self, table: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a table that contains charge information."""
        charges = []
        
        # Check if this looks like a charge table
        if not table:
            return charges
            
        # Try to identify charge description and amount columns
        desc_key = next((k for k in table.keys() if 'desc' in k.lower()), None)
        amount_key = next((k for k in table.keys() if 'amount' in k.lower() or '$' in k), None)
        
        if desc_key and amount_key and table[desc_key] and table[amount_key]:
            charges.append({
                'type': table[desc_key],
                'amount': table[amount_key].replace('$', '').strip() if isinstance(table[amount_key], str) else table[amount_key]
            })
            
        return charges

def extract_bill_data(file) -> dict:
    """
    Extract charge information from an energy bill PDF using OpenAI.
    
    Args:
        file: A file-like object containing the PDF data
        
    Returns:
        dict: Structured bill data focusing on charges breakdown
    """
    try:
        with pdfplumber.open(file) as pdf:
            # Extract text from all pages
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
            
            # Use OpenAI to extract structured data
            return extract_with_openai(full_text)
            
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return {
            "error": str(e),
            "message": "Failed to process the PDF bill. Please ensure it's a valid energy bill."
        }

def extract_with_openai(text: str) -> dict:
    """
    Use OpenAI to extract structured data from bill text.
    
    Args:
        text: The extracted text from the PDF
        
    Returns:
        dict: Structured bill data
    """
    try:
        # Create a prompt for OpenAI
        prompt = f"""
        Extract the following information from this energy bill text. Return the data in JSON format.
        
        For the bill summary, extract:
        - Account number
        - Billing period
        - Previous balance
        - Payment received
        - Credit balance
        - Current charges
        - Total amount due
        
        For the charges breakdown, extract all charges mentioned in the bill, such as:
        - Electricity used (in kWh)
        - Electricity delivery charges
        - Non-bypassable charges
        - Wildfire fund charge
        - Electricity generation charges
        - Electricity generation credit
        - Baseline adjustment credit
        - Other adjustments
        - Minimum charge adjustment
        - Taxes & fees
        - NEM credits
        - And any other charges mentioned
        
        Format the response as a JSON object with two main sections:
        1. "bill_summary" - containing the summary fields
        2. "charges_breakdown" - an array of objects with "charge_type" and "amount" fields
        
        Here's the bill text:
        {text}
        """
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use GPT-4 for better extraction accuracy
            messages=[
                {"role": "system", "content": "You are a utility bill parsing assistant. Extract structured data from energy bills accurately."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more deterministic results
            max_tokens=1000
        )
        
        # Extract the JSON response
        content = response.choices[0].message.content
        
        # Find JSON in the response (in case there's additional text)
        json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # If not in code block, try to find JSON directly
            json_match = re.search(r'(\{.*\})', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = content
        
        # Parse the JSON
        try:
            result = json.loads(json_str)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to clean up the string
            json_str = re.sub(r'[\n\r\t]', '', json_str)
            result = json.loads(json_str)
        
        # Ensure the result has the expected structure
        if "bill_summary" not in result:
            result["bill_summary"] = {}
        if "charges_breakdown" not in result:
            result["charges_breakdown"] = []
        
        # Add a note about credit balance if applicable
        if "total_amount_due" in result["bill_summary"]:
            amount = str(result["bill_summary"]["total_amount_due"])
            if amount.startswith("-"):
                result["bill_summary"]["note"] = "Credit balance. No payment required."
        
        return result
        
    except Exception as e:
        logger.error(f"Error using OpenAI for extraction: {e}")
        return {
            "error": str(e),
            "message": "Failed to extract bill data using AI. Please try again or extract manually."
        }
