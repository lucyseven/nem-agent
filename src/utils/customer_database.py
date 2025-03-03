def fetch_customer_details(account_number):
    
    """Simulate backend lookup for customer details."""
    # Fake database with 3 customers
    
    customer_database = {
        "100001": {
            "first_name": "TEST Michael",
            "last_name": "TEST Anderson",
            "address": "789 Birch Lane",
            "zip": "94102",
            "city": "San Francisco",
            "phone": "415-555-1234",
            "email": "michael.anderson@email.com"
        },
        # "100002": {
        #     "first_name": "TEST Samantha",
        #     "last_name": "TEST Carter",
        #     "address": "456 Maple Avenue",
        #     "zip": "60611",
        #     "city": "Chicago",
        #     "phone": "312-555-5678",
        #     "email": "samantha.carter@email.com"
        # },
        # "100003": {
        #     "first_name": "TEST Daniel",
        #     "last_name": "TEST Martinez",
        #     "address": "321 Oak Drive",
        #     "zip": "10001",
        #     "city": "New York",
        #     "phone": "212-555-9876",
        #     "email": "daniel.martinez@email.com"
        # }
    }
    return customer_database.get(account_number, None)  # Return customer data or None
