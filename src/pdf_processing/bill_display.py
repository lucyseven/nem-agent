import streamlit as st
import pandas as pd

def display_bill_data(bill_data: dict):
    """
    Display the extracted bill data in a simple, readable format.
    
    Args:
        bill_data: The structured bill data from extract_bill_data
    """
    if 'error' in bill_data:
        st.error(f"Error processing bill: {bill_data['error']}")
        return
    
    # Display bill summary
    st.subheader("📋 Bill Summary")
    summary = bill_data.get("bill_summary", {})
    
    # Create two columns for summary display
    col1, col2 = st.columns(2)
    
    with col1:
        if "account_number" in summary:
            st.metric("Account Number", summary["account_number"])
        if "billing_period" in summary:
            st.metric("Billing Period", summary["billing_period"])
        if "previous_balance" in summary:
            st.metric("Previous Balance", f"${summary['previous_balance']}")
    
    with col2:
        if "payment_received" in summary:
            st.metric("Payment Received", f"${summary['payment_received']}")
        if "current_charges" in summary:
            st.metric("Current Charges", f"${summary['current_charges']}")
        if "total_amount_due" in summary:
            value = summary["total_amount_due"]
            label = "Total Amount Due"
            if value.startswith("-"):
                label += " (Credit)"
            st.metric(label, f"${value}")
    
    # Display note if present
    if "note" in summary:
        st.info(summary["note"])
    
    # Display charges breakdown
    st.subheader("💰 Charges Breakdown")
    charges = bill_data.get("charges_breakdown", [])
    
    if charges:
        # Create DataFrame for charges
        charge_data = []
        for charge in charges:
            charge_type = charge.get("charge_type", "Unknown")
            amount = charge.get("amount", "0")
            unit = charge.get("unit", "$")
            
            # Format the amount with the unit
            if unit == "$" and not amount.endswith("kWh"):
                formatted_amount = f"${amount}"
            else:
                formatted_amount = f"{amount}"
            
            charge_data.append({
                "Charge Type": charge_type,
                "Amount": formatted_amount
            })
        
        if charge_data:
            # Display as table
            df = pd.DataFrame(charge_data)
            st.table(df)
    else:
        st.info("No detailed charges breakdown available in this bill.") 