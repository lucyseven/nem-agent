import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

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
            
            # Create pie chart
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.pie(df['Amount'], labels=df['Charge Type'], autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            plt.title('Charges Distribution')
            
            # Display the chart
            st.pyplot(fig)
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