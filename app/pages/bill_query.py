import streamlit as st
import os
from src.data_processing.csv_bill_loader import BillDataManager, display_account_bills

def bill_query_page():
    st.title("📊 Yearly Bill Query")
    
    # Initialize session state for bill data manager
    if "bill_data_manager" not in st.session_state:
        # Default path to the CSV file
        default_csv_path = os.path.join("data", "Monthly_Bills_for_Each_Account.csv")
        st.session_state.bill_data_manager = BillDataManager(default_csv_path)
    
    # Account selection
    st.subheader("🔍 Select Account")
    accounts = st.session_state.bill_data_manager.get_all_accounts()
    
    if not accounts:
        st.warning("No account data available. Please check the default data file.")
    else:
        # Allow user to select an account
        selected_account = st.selectbox(
            "Select an account number:",
            options=accounts
        )
        
        # Add a text input for direct account number entry
        account_input = st.text_input("Or enter account number directly:")
        
        if st.button("View Bill Data"):
            # Determine which account to use
            account_to_query = account_input if account_input else selected_account
            
            # Display the bill data
            display_account_bills(account_to_query, st.session_state.bill_data_manager)

if __name__ == "__main__":
    bill_query_page() 