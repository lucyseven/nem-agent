import fitz  # PyMuPDF
import re

def extract_text_from_pdf(uploaded_file):
    """Extracts text from an uploaded PDF file and ensures it is a valid string."""
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""

    for page in doc:
        page_text = page.get_text("text")
        if page_text:
            text += page_text + "\n"

    return text.strip()

def identify_bill_type(text):
    """Determines if the bill is Monthly or Annual based on key text patterns."""
    
    # Look for key phrases that indicate it's an **Annual Bill**
    if "Your account will true-up on" in text or "Annual Net Usage (kWh)" in text:
        return "Annual"

    # Look for key phrases that indicate it's a **Monthly Bill**
    if "Total Charges this Month" in text or re.search(r"Billing Period\s+[\w\d,\s-]+", text):
        return "Monthly"

    return "Unknown"  # If no clear indicators are found

def extract_bill_data(uploaded_file):
    """Extract structured bill details and determine if the bill is Monthly or Annual."""
    text = extract_text_from_pdf(uploaded_file)

    if not text:
        return {"Error": "Failed to extract text from PDF. Ensure the file is not empty or corrupted."}

    bill_type = identify_bill_type(text)

    data = {"Bill Type": bill_type}

    # --- Account Information ---
    data["Account Number"] = extract_match(r"ACCOUNT NUMBER\s+([\d\s]+)", text)
    data["Service Address"] = extract_match(r"SERVICE ADDRESS:\s+(.*?)\n", text)
    data["Date Mailed"] = extract_match(r"DATE MAILED\s+([\w\s\d,]+)", text)

    # --- Billing Details ---
    data["Billing Period"] = extract_match(r"Billing Period\s+([\w\d,\s-]+)", text)
    data["Electric Usage (kWh)"] = extract_match(r"Electric\s+\w+\s+(\d+)\s+kWh", text)

    # --- Payment Summary ---
    data["Previous Balance"] = extract_currency(r"Previous Balance\s+\$([\d\.,-]+)", text)
    data["Payment Received"] = extract_currency(r"Payment Received\s+\$?(-?[\d\.,]+)", text)
    data["Current Charges"] = extract_currency(r"Current Charges\s+\+?\$([\d\.,]+)", text)
    data["Total Amount Due"] = extract_currency(r"Total Amount Due\s+\$([\d\.,-]+)", text)

    # --- Net Energy Metering (NEM) - Annual Bill Only ---
    if bill_type == "Annual":
        data["True-Up Date"] = extract_match(r"Your account will true-up on ([\w\s\d,]+)\.", text)
        data["Net Metering Charges YTD"] = extract_currency(r"YTD Net Metering Charges/Credits\s+\$([\d\.,]+)", text)
        data["Current Account Balance"] = extract_currency(r"Current Account Balance\s+\$([\d\.,]+)", text)
        data["Annual Net Usage (kWh)"] = extract_match(r"Annual Net Usage \(kWh\)\s+([\d\.,]+)", text)

    # --- CCA & NEM Data - Monthly Bill Only ---
    if bill_type == "Monthly":
        data["CCA Electric Generation Charges"] = extract_currency(r"Total CCA Electric Generation Charges\s+\$([\d\.,]+)", text)
        data["Cumulative NEM Balance Credit"] = extract_currency(r"Your cumulative NEM Balance credit is now\s+\$([\d\.,]+)", text)

    return data

def extract_match(pattern, text):
    """Extracts the first regex match as a string."""
    if isinstance(text, str):
        match = re.search(pattern, text, re.MULTILINE)
        return match.group(1).strip() if match else "Not Found"
    return "Error"

def extract_currency(pattern, text):
    """Extracts and formats currency values."""
    if isinstance(text, str):
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            return f"${match.group(1)}"
    return "Not Found"

