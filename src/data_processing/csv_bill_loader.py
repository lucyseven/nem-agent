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
        
        # Return all columns for the account
        return account_data

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
    
    # Clean up column names to remove any special characters or formatting issues
    monthly_bills.columns = [col.strip().replace('\n', ' ').replace('\r', '') for col in monthly_bills.columns]
    
    # Debug info box removed
    
    # Define the specific columns we want to display and their mappings
    display_columns = [
        'Month',
        'Usage (kWh)',
        'Generation (kWh)',
        'Net Usage (kWh)',
        'Cost for Usage ($)',
        'Credit for Generation ($)',
        'Final Monthly Bill ($)'
    ]
    
    # Create a new DataFrame with only the desired columns
    filtered_df = pd.DataFrame(columns=display_columns)
    
    # Map columns based on case-insensitive exact matches
    column_mapping = {}
    for target_col in display_columns:
        for db_col in monthly_bills.columns:
            if target_col.lower() == db_col.lower():
                column_mapping[target_col] = db_col
                break
    
    # Fill in the filtered dataframe with matched columns
    for target_col, db_col in column_mapping.items():
        filtered_df[target_col] = monthly_bills[db_col]
    
    # For any columns that weren't matched, try partial matching
    for target_col in display_columns:
        if target_col not in column_mapping:
            for db_col in monthly_bills.columns:
                # Check if the target column name is contained within the database column name
                if target_col.lower().replace(' ', '') in db_col.lower().replace(' ', ''):
                    filtered_df[target_col] = monthly_bills[db_col]
                    break
    
    # Display the filtered dataframe
    st.dataframe(filtered_df)
    
    # Try to identify columns for visualization
    usage_col = 'Usage (kWh)'
    cost_col = 'Cost for Usage ($)'
    credit_col = 'Credit for Generation ($)'
    bill_col = 'Final Monthly Bill ($)'
    
    # If we have the necessary columns with data, create visualization
    if all(col in filtered_df.columns for col in [usage_col, cost_col, credit_col, bill_col]):
        # Check if we have enough non-null values to create a meaningful visualization
        if (filtered_df[usage_col].notna().sum() > 0 and
            filtered_df[cost_col].notna().sum() > 0 and 
            filtered_df[credit_col].notna().sum() > 0 and 
            filtered_df[bill_col].notna().sum() > 0):
            display_generation_consumption_breakdown(filtered_df, account_number, 
                                                   usage_col, cost_col, 
                                                   credit_col, bill_col)
        else:
            st.info("Not enough data to create a visualization. Please check your bill data.")

def display_generation_consumption_breakdown(monthly_bills, account_number, 
                                           usage_col, cost_col, 
                                           credit_col, bill_col):
    """Display a breakdown of generation credits and consumption costs."""
    st.subheader("⚡ Generation vs. Consumption Breakdown")
    
    try:
        # Create a copy to avoid modifying the original dataframe
        breakdown_data = monthly_bills.copy()
        
        # Ensure the columns are numeric
        for col in [cost_col, credit_col, bill_col]:
            breakdown_data[col] = pd.to_numeric(breakdown_data[col], errors='coerce')
        
        # Create the visualization with a much smaller figure size
        fig, ax = plt.subplots(figsize=(3, 2))  # Significantly smaller
        
        # Set even smaller font sizes for all text elements
        plt.rcParams.update({
            'font.size': 3,          # Base font size
            'axes.titlesize': 4,     # Title font size
            'axes.labelsize': 3.5,   # Axis label font size
            'xtick.labelsize': 3,    # X-axis tick label font size
            'ytick.labelsize': 3,    # Y-axis tick label font size
            'legend.fontsize': 3     # Legend font size
        })
        
        # Get month names for x-axis
        x_values = breakdown_data.index
        if 'Month' in breakdown_data.columns:
            x_values = breakdown_data['Month']
        
        # Plot bars
        usage_bars = ax.bar(x_values, breakdown_data[cost_col], 
                           color='indianred', label='Cost for Usage')
        credit_bars = ax.bar(x_values, -breakdown_data[credit_col], 
                            color='forestgreen', label='Credit for Generation')
        
        # Add bill amount as a line
        bill_line = ax.plot(x_values, breakdown_data[bill_col], 
                          'ko-', linewidth=0.6, label='Monthly Bill')
        
        # Formatting
        ax.set_xlabel('Month')
        ax.set_ylabel('Amount ($)')
        ax.set_title('Generation vs. Consumption')  # Shortened title
        
        # Create legend manually with smaller font
        ax.legend([usage_bars, credit_bars, bill_line[0]], 
                 ['Cost', 'Credit', 'Bill'],  # Shorter labels
                 loc='best', frameon=True, framealpha=0.7, fontsize=3)
        
        # Add grid for better readability
        ax.grid(True, linestyle='--', alpha=0.3, linewidth=0.2)
        
        # Make x-axis labels rotated for better fit
        plt.xticks(rotation=45)
        
        # Adjust layout to ensure everything fits
        plt.tight_layout(pad=0.1)  # Reduce padding
        
        # Display the plot with custom width
        st.pyplot(fig, use_container_width=False)
        
        # Reset rcParams to default for other plots
        plt.rcParams.update(plt.rcParamsDefault)
        
        # Calculate totals
        total_generation = breakdown_data[credit_col].sum()
        total_consumption = breakdown_data[cost_col].sum()
        net_balance = total_consumption - total_generation
        monthly_bills_total = breakdown_data[bill_col].sum()
        
        # Display metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Generation Credits", f"${abs(total_generation):.2f}")
            st.metric("Total Consumption Costs", f"${total_consumption:.2f}")
        
        with col2:
            st.metric("Monthly Bills Total", f"${monthly_bills_total:.2f}")
            st.metric("If paid annually", f"${net_balance:.2f}", 
                     delta="Credit" if net_balance <= 0 else "Debit")
        
        # Add a summary
        if net_balance <= 0:
            st.success(f"✅ Your generation credits exceed your consumption costs by ${abs(net_balance):.2f}.")
        else:
            st.warning(f"⚠️ Your consumption costs exceed your generation credits by ${net_balance:.2f}.")
            
        # Add comparison between monthly bills total and annual payment
        difference = monthly_bills_total - net_balance
        
        # Use a small threshold to account for floating point precision issues
        if abs(difference) < 0.01:
            st.info("💡 There is no significant difference between paying monthly or annually.")
        elif difference > 0:
            st.info(f"💡 By paying annually instead of monthly, you could save ${difference:.2f}.")
        elif difference < 0:
            st.info(f"💡 Paying monthly is ${abs(difference):.2f} less than what you would pay annually.")
    
    except Exception as e:
        st.error(f"Error creating generation vs. consumption breakdown: {str(e)}")
        st.info("Could not create detailed breakdown with the available data.")

def display_generation_consumption_breakdown_dynamic(monthly_bills, account_number, 
                                                   usage_col, cost_col, 
                                                   credit_col, bill_col):
    """Display a breakdown of generation credits and consumption costs with dynamic column detection."""
    st.subheader("⚡ Generation vs. Consumption Breakdown")
    
    try:
        # Create a copy to avoid modifying the original dataframe
        breakdown_data = monthly_bills.copy()
        
        # Ensure the columns are numeric
        for col in [cost_col, credit_col, bill_col]:
            breakdown_data[col] = pd.to_numeric(breakdown_data[col], errors='coerce')
        
        # Create the visualization
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Get month names or index for x-axis
        x_values = breakdown_data.index
        month_col = next((col for col in breakdown_data.columns if 'month' in col.lower()), None)
        if month_col:
            x_values = breakdown_data[month_col]
        
        # Plot bars
        usage_bars = ax.bar(x_values, breakdown_data[cost_col], 
                           color='indianred', label=f'{cost_col}')
        credit_bars = ax.bar(x_values, -breakdown_data[credit_col], 
                            color='forestgreen', label=f'{credit_col}')
        
        # Add bill amount as a line
        bill_line = ax.plot(x_values, breakdown_data[bill_col], 
                          'ko-', linewidth=2, label=f'{bill_col}')
        
        # Formatting
        ax.set_xlabel('Month')
        ax.set_ylabel('Amount ($)')
        ax.set_title('Generation vs. Consumption Breakdown')
        
        # Create legend manually
        ax.legend([usage_bars, credit_bars, bill_line[0]], 
                 [cost_col, credit_col, bill_col])
        
        # Add grid for better readability
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Display the plot
        st.pyplot(fig)
        
        # Calculate totals
        total_generation = breakdown_data[credit_col].sum()
        total_consumption = breakdown_data[cost_col].sum()
        net_balance = total_consumption - total_generation
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Generation Credits", f"${abs(total_generation):.2f}")
        
        with col2:
            st.metric("Total Consumption Costs", f"${total_consumption:.2f}")
        
        with col3:
            st.metric("Net Balance", f"${net_balance:.2f}", 
                     delta="Credit" if net_balance <= 0 else "Debit")
        
        # Add a summary
        if net_balance <= 0:
            st.success(f"✅ Your generation credits exceed your consumption costs by ${abs(net_balance):.2f}.")
        else:
            st.warning(f"⚠️ Your consumption costs exceed your generation credits by ${net_balance:.2f}.")
    
    except Exception as e:
        st.error(f"Error creating generation vs. consumption breakdown: {str(e)}")
        st.info("Could not create detailed breakdown with the available data.")

# Remove or comment out these lines
# file_path = '/Users/junjiezhang/Documents/GitHub/nem-agent/data/Monthly_Bills_for_Each_Account.csv'
# display_account_bills('123456', file_path) 