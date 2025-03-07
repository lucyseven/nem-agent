from typing import Dict, List, Pattern
import re

class ParserRuleSet:
    """
    Defines regex patterns and extraction rules for different utility companies.
    """
    
    def __init__(self, utility_name: str):
        self.utility_name = utility_name
        self.patterns = self._get_patterns_for_utility(utility_name)
    
    def _get_patterns_for_utility(self, utility_name: str) -> Dict[str, str]:
        """
        Get the appropriate regex patterns for the specified utility.
        """
        # Default patterns (generic)
        default_patterns = {
            'account_number': r'Account\s*Number[:\s]*([A-Za-z0-9-]+)',
            'billing_period': r'Billing\s*Period[:\s]*([A-Za-z0-9,\s]+to[A-Za-z0-9,\s]+)',
            'total_amount': r'Total\s*Amount\s*Due[:\s]*\$?([0-9,.]+)',
            'due_date': r'Due\s*Date[:\s]*([A-Za-z0-9,\s]+)',
            'energy_usage': r'Total\s*kWh\s*Used[:\s]*([0-9,.]+)',
            'generation_charges': r'Generation\s*Charges[:\s]*\$?([0-9,.]+)',
            'delivery_charges': r'Delivery\s*Charges[:\s]*\$?([0-9,.]+)',
            'nem_credits': r'NEM\s*Credits[:\s]*\$?([0-9,.]+)',
        }
        
        # Utility-specific patterns
        utility_patterns = {
            'sdge': {  # San Diego Gas & Electric
                'account_number': r'Account\s*Number[:\s]*([A-Za-z0-9-]+)',
                'billing_period': r'Billing\s*period[:\s]*([A-Za-z0-9,\s]+to[A-Za-z0-9,\s]+)',
                'total_amount': r'TOTAL\s*AMOUNT\s*DUE[:\s]*\$?([0-9,.]+)',
                'due_date': r'Due\s*Date[:\s]*([A-Za-z0-9,\s]+)',
                'energy_usage': r'Total\s*kWh\s*this\s*month[:\s]*([0-9,.]+)',
                'generation_charges': r'Generation[:\s]*\$?([0-9,.]+)',
                'delivery_charges': r'Delivery[:\s]*\$?([0-9,.]+)',
                'nem_credits': r'NEM\s*Credit[:\s]*\$?([0-9,.]+)',
            },
            'pge': {  # Pacific Gas & Electric
                'account_number': r'Account\s*No[:\s]*([A-Za-z0-9-]+)',
                'billing_period': r'Service\s*from[:\s]*([A-Za-z0-9,\s]+to[A-Za-z0-9,\s]+)',
                'total_amount': r'Total\s*Amount\s*Due[:\s]*\$?([0-9,.]+)',
                'due_date': r'Due\s*Date[:\s]*([A-Za-z0-9,\s]+)',
                'energy_usage': r'Total\s*Usage[:\s]*([0-9,.]+)\s*kWh',
                'generation_charges': r'Generation[:\s]*\$?([0-9,.]+)',
                'delivery_charges': r'Delivery[:\s]*\$?([0-9,.]+)',
                'nem_credits': r'Net\s*Surplus\s*Compensation[:\s]*\$?([0-9,.]+)',
            },
            'sce': {  # Southern California Edison
                'account_number': r'Account\s*number[:\s]*([A-Za-z0-9-]+)',
                'billing_period': r'Billing\s*period[:\s]*([A-Za-z0-9,\s]+to[A-Za-z0-9,\s]+)',
                'total_amount': r'Total\s*amount\s*due[:\s]*\$?([0-9,.]+)',
                'due_date': r'Payment\s*Due\s*by[:\s]*([A-Za-z0-9,\s]+)',
                'energy_usage': r'Total\s*kWh[:\s]*([0-9,.]+)',
                'generation_charges': r'Generation[:\s]*\$?([0-9,.]+)',
                'delivery_charges': r'Delivery[:\s]*\$?([0-9,.]+)',
                'nem_credits': r'NEM\s*Credits[:\s]*\$?([0-9,.]+)',
            },
        }
        
        # Return utility-specific patterns if available, otherwise default
        return utility_patterns.get(utility_name.lower(), default_patterns)
    
    def detect_utility_from_text(text: str) -> str:
        """
        Detect which utility company the bill is from based on text content.
        """
        text_lower = text.lower()
        
        if "san diego gas & electric" in text_lower or "sdg&e" in text_lower:
            return "sdge"
        elif "pacific gas and electric" in text_lower or "pg&e" in text_lower:
            return "pge"
        elif "southern california edison" in text_lower or "sce" in text_lower:
            return "sce"
        
        # Default to generic if can't determine
        return "generic"
