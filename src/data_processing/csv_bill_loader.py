import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import os

class BillDataManager:
    """Manages bill data loaded from CSV files."""
    
    def __init__(self, csv_path=None):
        """Initialize with optional CSV path."""
        self.data = None
        if csv_path and os.path.exists(csv_path):
            self.load_data(csv_path)
    
    def load_data(self, csv_path):
        """Load bill data from CSV file."""
        try:
            self.data = pd.read_csv(csv_path)
            # Convert column names to lowercase for consistency
            self.data.columns = [col.lower() for col in self.data.columns]
            return True
        except Exception as e:
            st.error(f"Error loading CSV file: {e}")
            return False
    
    def get_all_accounts(self):
        """Return list of all account numbers."""
        if self.data is None:
            return []
        
        # Look for account column (might be named differently)
        account_col = next((col for col in self.data.columns if 'account' in col.lower()), None)
        if account_col:
            return sorted(self.data[account_col].unique().tolist())
        return []
    
    def get_account_data(self, account_number):
        """Get all bill data for a specific account."""
        if self.data is None:
            return None
        
        # Find the account column
        account_col = next((col for col in self.data.columns if 'account' in col.lower()), None)
        if not account_col:
            return None
        
        # Filter data for the specified account
        account_data = self.data[self.data[account_col] == account_number]
        if account_data.empty:
            return None
        
        return account_data
    
    def get_monthly_bills(self, account_number):
        """Get monthly bill amounts for a specific account."""
        account_data = self.get_account_data(account_number)
        if account_data is None:
            return None
        
        # Look for month and amount columns
        month_col = next((col for col in account_data.columns if 'month' in col.lower()), None)
        amount_cols = [col for col in account_data.columns if any(term in col.lower() for term in ['amount', 'balance', 'bill', 'charge'])]
        
        if not month_col or not amount_cols:
            # Try to infer monthly data from column names if they're named by month
            month_cols = [col for col in account_data.columns if any(month in col.lower() for month in 
                         ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])]
            
            if month_cols:
                # Reshape data to have months as rows
                monthly_data = {}
                for col in month_cols:
                    monthly_data[col] = account_data[col].iloc[0]
                return pd.DataFrame(monthly_data.items(), columns=['Month', 'Amount'])
        
        # If we have explicit month and amount columns
        if month_col and amount_cols:
            return account_data[[month_col] + amount_cols]
        
        return None

def load_monthly_bills(file_path):
    """Load monthly bills from a CSV file."""
    try:
        monthly_bills = pd.read_csv(file_path)
        return monthly_bills
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def display_account_bills(account_number, bill_manager):
    """Display monthly bills for a specific account."""
    # Check if bill_manager is a BillDataManager object or a file path
    if isinstance(bill_manager, str):
        monthly_bills = load_monthly_bills(bill_manager)
    else:
        # Assume it's a BillDataManager instance
        monthly_bills = bill_manager.get_monthly_bills(account_number)
    
    if monthly_bills is None or monthly_bills.empty:
        st.warning(f"No bill data found for account {account_number}")
        return
    
    st.subheader(f"📊 Monthly Bills for Account: {account_number}")
    
    # Define the specific columns we want to display
    desired_columns = {
        'month': 'Month',
        'usage_kwh': 'Usage (kWh)',
        'generation': 'Generation (kWh)',
        'net_usage': 'Net Usage (kWh)',
        'cost': 'Cost for Usage ($)',
        'credit': 'Credit for Generation ($)',
        'final amount due': 'Monthly Bill ($)'
    }
    
    # Create a new DataFrame with standardized column names
    standardized_df = pd.DataFrame()
    
    # First try exact matches
    for source_col, target_col in desired_columns.items():
        for col in monthly_bills.columns:
            if source_col.lower() == col.lower():
                standardized_df[target_col] = monthly_bills[col]
                break
    
    # Then try partial matches for any missing columns
    for target_col in desired_columns.values():
        if target_col not in standardized_df.columns:
            for col in monthly_bills.columns:
                col_lower = col.lower()
                for source_col, target_name in desired_columns.items():
                    if target_name == target_col and source_col in col_lower:
                        standardized_df[target_col] = monthly_bills[col]
                        break
    
    # If we have data, display it
    if not standardized_df.empty:
        st.dataframe(standardized_df)
    else:
        # If we couldn't map any columns, show the original data
        st.dataframe(monthly_bills)
    
    # Call the generation vs consumption breakdown function
    try:
        display_generation_consumption_breakdown(standardized_df if not standardized_df.empty else monthly_bills, account_number)
    except Exception as e:
        st.error(f"Error displaying generation vs consumption breakdown: {str(e)}")
        st.info("Could not create visualization with the available data format.")

def display_generation_consumption_breakdown(monthly_bills, account_number):
    """Display a breakdown of generation credits and consumption costs."""
    st.subheader("⚡ Generation vs. Consumption Breakdown")
    
    try:
        # Check if we have the required columns
        required_cols = ['Cost for Usage ($)', 'Credit for Generation ($)', 'Monthly Bill ($)']
        
        if all(col in monthly_bills.columns for col in required_cols):
            # Create a copy to avoid modifying the original dataframe
            breakdown_data = monthly_bills.copy()
            
            # Ensure the columns are numeric
            for col in required_cols:
                breakdown_data[col] = pd.to_numeric(breakdown_data[col], errors='coerce')
            
            # Create the visualization
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Get month names if 'Month' column exists
            x_values = breakdown_data.index
            if 'Month' in breakdown_data.columns:
                x_values = breakdown_data['Month']
            
            # Plot bars
            usage_bars = ax.bar(x_values, breakdown_data['Cost for Usage ($)'], 
                               color='indianred', label='Cost for Usage ($)')
            credit_bars = ax.bar(x_values, -breakdown_data['Credit for Generation ($)'], 
                                color='forestgreen', label='Credit for Generation ($)')
            
            # Add bill amount as a line
            bill_line = ax.plot(x_values, breakdown_data['Monthly Bill ($)'], 
                              'ko-', linewidth=2, label='Monthly Bill ($)')
            
            # Formatting
            ax.set_xlabel('Month')
            ax.set_ylabel('Amount ($)')
            ax.set_title('Generation vs. Consumption Breakdown')
            
            # Create legend manually to avoid the error
            ax.legend([usage_bars, credit_bars, bill_line[0]], 
                     ['Cost for Usage ($)', 'Credit for Generation ($)', 'Monthly Bill ($)'])
            
            # Add grid for better readability
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Display the plot
            st.pyplot(fig)
            
            # Calculate totals
            total_generation = breakdown_data['Credit for Generation ($)'].sum()
            total_consumption = breakdown_data['Cost for Usage ($)'].sum()
            net_balance = total_generation - total_consumption
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Generation Credits", f"${total_generation:.2f}")
            
            with col2:
                st.metric("Total Consumption Costs", f"${total_consumption:.2f}")
            
            with col3:
                st.metric("Net Balance", f"${net_balance:.2f}", 
                         delta="Credit" if net_balance >= 0 else "Debit")
            
            # Add a summary
            if net_balance >= 0:
                st.success(f"✅ Your generation credits exceed your consumption costs by ${net_balance:.2f}.")
            else:
                st.warning(f"⚠️ Your consumption costs exceed your generation credits by ${abs(net_balance):.2f}.")
        else:
            missing_cols = [col for col in required_cols if col not in monthly_bills.columns]
            st.info(f"Could not create detailed breakdown. Missing columns: {', '.join(missing_cols)}")
    
    except Exception as e:
        st.error(f"Error creating generation vs. consumption breakdown: {str(e)}")
        st.info("Could not create detailed breakdown with the available data.")

# Remove or comment out these lines
# file_path = '/Users/junjiezhang/Documents/GitHub/nem-agent/data/Monthly_Bills_for_Each_Account.csv'
# display_account_bills('123456', file_path) 