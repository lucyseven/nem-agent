# ⚡ NEM Bill Explainer Chatbot ⚡

<p style="font-family: 'Courier New', monospace; font-size: 18px;">
  A conversational agent that helps you understand your Net Energy Metering (NEM) bills by chatting about billing details, reading PDF bills, and offering flexible billing views.
</p>

## 💬 Overview

This chatbot is designed to help you:

- **Chat about NEM Bills:** Ask questions and get clear explanations about your energy usage and charges.
- **Read PDF Bills:** Automatically extract key billing information from uploaded PDF bills.
- **Switch Billing Modes:** Toggle between a detailed monthly breakdown and an annual billing view—including the true-up process.

<h2 style="font-family: 'Courier New', monospace; font-size: 20px;">🔍 Key Features</h2>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  <strong>🗣️ Interactive Chat:</strong><br>
  Engage in natural conversation about your NEM bill. Ask questions like "What is NEM?" and receive personalized, plain language responses.
</p>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  <strong>📄 PDF Reading:</strong><br>
  Upload your NEM bill in PDF format, and the agent extracts crucial data such as usage, credits, and total charges.
</p>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  <strong>🔄 Billing Mode Switch:</strong><br>
  <strong>Monthly Mode:</strong> View detailed information for the current billing period.<br>
  <strong>Annual Mode:</strong> Switch to an annual billing view that includes cumulative usage, credits, and the true-up process, providing a complete picture of your energy management.
</p>

<h2 style="font-family: 'Courier New', monospace; font-size: 20px;">📚 Knowledge Sources</h2>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  The chatbot uses Retrieval-Augmented Generation (RAG) with the following document sources:
</p>

<ul style="font-family: 'Arial', sans-serif; font-size: 16px;">
  <li><strong>FAQ Document:</strong> Comprehensive answers to the top 20 frequently asked questions about Net Energy Metering</li>
  <li><strong>NEM Policy Document:</strong> Official policy information and guidelines about Net Energy Metering</li>
  <li><strong>Website Scraped Data:</strong> Up-to-date information collected from relevant utility websites about NEM programs</li>
</ul>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  These documents are processed using advanced natural language processing techniques to provide accurate and relevant responses to your queries.
</p>

<h2 style="font-family: 'Courier New', monospace; font-size: 20px;">🧠 AI Models Used</h2>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  This project leverages multiple AI models to deliver accurate and helpful responses:
</p>

<ul style="font-family: 'Arial', sans-serif; font-size: 16px;">
  <li><strong>OpenAI GPT-3.5 Turbo:</strong> Powers the main conversational interface, generating natural language responses based on retrieved context</li>
  <li><strong>OpenAI GPT-4:</strong> Used specifically for PDF bill extraction, providing enhanced accuracy when parsing complex bill structures</li>
  <li><strong>SentenceTransformers (all-MiniLM-L6-v2):</strong> A lightweight local embedding model that converts text into vector representations for efficient retrieval</li>
</ul>

<h2 style="font-family: 'Courier New', monospace; font-size: 20px;">🔄 RAG Architecture</h2>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  The NEM Bill Explainer uses a Retrieval-Augmented Generation (RAG) pipeline that:
</p>

<ol style="font-family: 'Arial', sans-serif; font-size: 16px;">
  <li><strong>Processes Documents:</strong> Loads and chunks documents into manageable pieces (300 words with 50-word overlap)</li>
  <li><strong>Generates Embeddings:</strong> Creates vector representations of document chunks using SentenceTransformers locally</li>
  <li><strong>Retrieves Context:</strong> When a user asks a question, finds the most relevant document chunks</li>
  <li><strong>Generates Responses:</strong> Combines the retrieved context with the user query to create accurate, contextual answers</li>
</ol>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  This approach ensures that the chatbot provides responses grounded in accurate NEM information while maintaining conversational fluency.
</p>

<h2 style="font-family: 'Courier New', monospace; font-size: 20px;">📊 Bill Analysis Features</h2>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  The system provides detailed analysis of your NEM bills:
</p>

<ul style="font-family: 'Arial', sans-serif; font-size: 16px;">
  <li><strong>Monthly Breakdown:</strong> Visualize charges, credits, and usage for each billing period</li>
  <li><strong>Annual Comparison:</strong> Compare monthly bills throughout the year to identify trends</li>
  <li><strong>Generation vs. Consumption:</strong> See how your solar generation offsets your energy consumption</li>
  <li><strong>True-up Estimation:</strong> Understand what your annual settlement might look like</li>
</ul>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  The system automatically calculates totals and provides insights about whether your generation credits exceed your consumption costs.
</p>

<h2 style="font-family: 'Courier New', monospace; font-size: 20px;">🔍 Utility-Specific Support</h2>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  The system includes specialized parsing rules for different utility companies, ensuring accurate extraction regardless of bill format:
</p>

<ul style="font-family: 'Arial', sans-serif; font-size: 16px;">
  <li><strong>San Diego Gas & Electric (SDGE):</strong> Custom patterns for SDGE's unique bill layout and terminology</li>
  <li><strong>Pacific Gas & Electric (PG&E):</strong> Specialized extraction for PG&E's billing format</li>
  <li><strong>Other Utilities:</strong> Fallback to generic patterns for other utility companies</li>
</ul>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  This multi-utility support ensures the system can handle bills from various energy providers across California.
</p>

<h2 style="font-family: 'Courier New', monospace; font-size: 20px;">🧪 Testing and Reliability</h2>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  The system includes comprehensive testing to ensure reliable bill processing:
</p>

<ul style="font-family: 'Arial', sans-serif; font-size: 16px;">
  <li><strong>Unit Tests:</strong> Automated tests for PDF extraction, pattern matching, and data processing</li>
  <li><strong>Mock Testing:</strong> Simulated bill processing to verify extraction accuracy</li>
  <li><strong>Error Handling:</strong> Robust error detection and user-friendly error messages</li>
</ul>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  The testing framework ensures that bill data is extracted accurately and consistently across different bill formats and edge cases.
</p>

<h2 style="font-family: 'Courier New', monospace; font-size: 20px;">📊 Data Visualization Features</h2>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  The system provides rich visualizations to help understand your energy usage and billing:
</p>

<ul style="font-family: 'Arial', sans-serif; font-size: 16px;">
  <li><strong>Charges Breakdown:</strong> Pie charts showing the distribution of different charge types</li>
  <li><strong>Monthly Comparison:</strong> Bar and line charts comparing bill amounts and energy usage across months</li>
  <li><strong>Generation vs. Consumption:</strong> Side-by-side comparison of energy generation credits and consumption costs</li>
  <li><strong>Annual Summary:</strong> Visualization of cumulative generation, consumption, and net balance</li>
</ul>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  These visualizations make complex billing information more accessible and help identify patterns in your energy usage and costs.
</p>

<h2 style="font-family: 'Courier New', monospace; font-size: 20px;">💬 Conversation Management</h2>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  The chatbot maintains context throughout your conversation:
</p>

<ul style="font-family: 'Arial', sans-serif; font-size: 16px;">
  <li><strong>History Tracking:</strong> Remembers previous questions and answers for contextual responses</li>
  <li><strong>Bill Context Integration:</strong> Automatically incorporates uploaded bill data into the conversation</li>
  <li><strong>Natural Follow-ups:</strong> Supports follow-up questions about previously discussed topics</li>
</ul>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  This conversational memory allows for more natural and helpful interactions about your energy bills.
</p>

<h2 style="font-family: 'Courier New', monospace; font-size: 20px;">🔐 Privacy and Security</h2>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  The system is designed with privacy in mind:
</p>

<ul style="font-family: 'Arial', sans-serif; font-size: 16px;">
  <li><strong>Local Processing:</strong> Embeddings are generated locally using SentenceTransformers</li>
  <li><strong>Secure API Usage:</strong> OpenAI API calls follow best practices for data security</li>
  <li><strong>No Data Storage:</strong> Bill data is processed in-memory and not permanently stored</li>
</ul>

<p style="font-family: 'Arial', sans-serif; font-size: 16px;">
  Your bill information remains private and secure throughout the analysis process.
</p>

## 🔧 Technical Implementation

The NEM Bill Explainer is built with the following technical components:

- **Streamlit Frontend**: Interactive web interface with chat bubbles, file uploading, and data visualization.
  - **Reference**: The Streamlit configuration and custom CSS for chat bubbles are set up in `main.py`.
  ```python
  # ---- Streamlit Page Config ----
  st.set_page_config(page_title="NEM Agent", layout="wide")

  # ---- Inject Custom CSS for Chat Bubbles ----
  st.markdown(
      """
      <style>
      .chat-container {
          display: flex;
          flex-direction: column;
          margin-top: 1rem;
      }
      .chat-bubble {
          padding: 10px 15px;
          margin: 5px;
          border-radius: 10px;
          max-width: 60%;
          line-height: 1.4;
          font-size: 1rem;
          word-wrap: break-word;
      }
      /* Assistant messages (left) */
      .assistant-bubble {
          background-color: #f1f1f1;
          align-self: flex-start;
      }
      /* User messages (right) */
      .user-bubble {
          background-color: #d2f8d2; /* Light green bubble */
          align-self: flex-end;
      }
      .chat-input-container {
          margin-top: 1rem;
          display: flex;
          gap: 0.5rem;
      }
      </style>
      """,
      unsafe_allow_html=True
  )
  ```

- **PDF Processing**: Uses `pdfplumber` for text extraction and GPT-4 for structured data parsing.
  - **Reference**: The PDF processing and extraction logic is implemented in `pdf_extractor.py`.
  ```python
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
  ```

- **Vector Search**: FAISS implementation for efficient similarity search of document embeddings.
  - **Reference**: The vector search functionality is defined in `vector_search.py`.
  ```python
  import faiss
  import numpy as np
  from langchain.embeddings import OpenAIEmbeddings
  from langchain.vectorstores import FAISS

  class VectorSearch:
      def __init__(self):
          self.embeddings_model = OpenAIEmbeddings()
          self.vector_db = None

      def create_vector_store(self, docs):
          """Create FAISS vector store from NEM documents"""
          embeddings = self.embeddings_model.embed_documents(docs)
          index = faiss.IndexFlatL2(len(embeddings[0]))
          index.add(np.array(embeddings, dtype=np.float32))
          self.vector_db = index

      def search(self, query, k=3):
          """Retrieve top-k relevant documents"""
          query_embedding = self.embeddings_model.embed_query(query)
          distances, indices = self.vector_db.search(np.array([query_embedding]), k)
          return indices[0]  # Return indices of relevant documents
  ```

- **Data Visualization**: Matplotlib and Pandas for creating interactive charts of bill data.
  - **Reference**: The data visualization logic is implemented in `bill_visualizer.py`.
  ```python
  def visualize_bill_data(bill_data: dict):
      """
      Visualize the bill data using charts.
      """
      charges = bill_data.get('charges_breakdown', [])
      
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
  ```

- **Utility-Specific Parsing**: Custom regex patterns for different utility companies (PG&E, SDGE, etc.).
  - **Reference**: The regex patterns for parsing are defined in `ParserRuleSet` class in `parser_rules.py`.
  ```python
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
  ```

This section provides a comprehensive overview of the technical components and their implementation within the project. Each component is crucial for ensuring the chatbot's functionality and user experience.
