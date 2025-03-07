import asyncio
import streamlit as st
from src.chatbot.rag import get_response
from src.chatbot.conversation import ConversationManager
from src.pdf_processing.pdf_extractor import extract_bill_data
from src.agents.website_agent import execute_website_agent
from src.utils.customer_database import fetch_customer_details
from src.pdf_processing.bill_visualizer import visualize_bill_data, get_monthly_comparison_chart
from src.pdf_processing.bill_display import display_bill_data

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


# try:
#     asyncio.get_running_loop()
# except RuntimeError:
#     asyncio.set_event_loop(asyncio.new_event_loop())



import os
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

print("✅ Running the updated main.py!")

# ---- Streamlit Page Config ----
st.set_page_config(page_title="NEM Agent", layout="centered")

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

# ---- Center the Logo with Streamlit ----
st.image("app/assets/sdcp_logo.jpg", width=200, caption="", )

# ---- Title ----
st.title("🔹 NEM Agent")

# ---- Subtitle ----
st.markdown(
    "<p style='font-size:1.3rem; font-weight:600;'>Ask me anything about Net Energy Metering (NEM)!</p>",
    unsafe_allow_html=True
)

# ---- Initialize conversation in session state BEFORE using it ----
if "conversation" not in st.session_state:
    st.session_state.conversation = ConversationManager()

# We store the user's typed text in "temp_user_input"
# so we can reset it after sending without conflicting with the widget.
if "temp_user_input" not in st.session_state:
    st.session_state.temp_user_input = ""

def display_chat_bubbles():
    """Renders the conversation as bubble-style messages."""
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in st.session_state.conversation.history:
        role = msg["role"]  # "user" or "assistant"
        content = msg["content"]
        bubble_class = "assistant-bubble" if role == "assistant" else "user-bubble"
        st.markdown(f"<div class='chat-bubble {bubble_class}'>{content}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def send_message():
    """Callback triggered when user presses Enter in the text_input."""
    user_text = st.session_state.temp_user_input
    if user_text.strip():
        # 1) Add user message
        st.session_state.conversation.add_message("user", user_text)

        # 2) Build conversation context
        conversation_history = st.session_state.conversation.get_formatted_history()

        # 3) Get RAG-based answer
        answer = get_response(conversation_history)

        # 4) Add assistant's message
        st.session_state.conversation.add_message("assistant", answer)

    # Clear the text box
    st.session_state.temp_user_input = ""

    # Rerun to refresh the UI
    if hasattr(st, "rerun"):
        st.experimental_rerun()

# ---- Render existing conversation so far ----
display_chat_bubbles()

# ---- Text Input with on_change callback (no Send button needed) ----
st.text_input(
    "Message:What do you have in mind?",  # Provide a valid label
    key="temp_user_input",
    on_change=send_message,
    placeholder="Type here and press Enter to send",
    label_visibility="hidden"  # Instead of collapsed
)


# # ---- Check if user wants to switch to annual billing ----
# if "switch_to_annual_stage" not in st.session_state:
#     st.session_state.switch_to_annual_stage = None  # Track confirmation state

# if st.session_state.conversation.history:
#     last_message = st.session_state.conversation.history[-1]["content"]
    
#     if "switch to annual" in last_message.lower():
#         if st.session_state.switch_to_annual_stage is None:
#             # Step 1: Show confirmation message with Yes/No buttons
#             st.warning("⚠️ Please double-check if you want to switch to annual.")
#             col1, col2 = st.columns(2)

#             with col1:
#                 if st.button("✅ Yes, switch to annual"):
#                     st.session_state.switch_to_annual_stage = "ask_account"

#             with col2:
#                 if st.button("❌ No, go back to chat"):
#                     st.session_state.switch_to_annual_stage = "cancel"

#         elif st.session_state.switch_to_annual_stage == "ask_account":
#             # Step 2: Ask for the user's account number
#             account_number = st.text_input("Please enter your account number:")
        
#             if account_number:
#                 customer_data = fetch_customer_details(account_number)  # ✅ Fetch details from backend
            
#                 if customer_data:  # ✅ Make sure the account exists
#                     with st.spinner("Processing..."):
#                         result = execute_website_agent(customer_data, account_number)  # ✅ Pass correct data
#                         st.success(f"✅ Switched to Annual Billing for Account: {account_number}")
#                         st.write(result)
#                 else:
#                     st.error("❌ Account number not found! Please try again.")

#                 st.session_state.switch_to_annual_stage = None  # Reset the state

#         elif st.session_state.switch_to_annual_stage == "cancel":
#             st.info("❌ Action canceled. Returning to chat...")
#             st.session_state.switch_to_annual_stage = None  # Reset state


if "switch_to_annual_stage" not in st.session_state:
    st.session_state.switch_to_annual_stage = None  # Track confirmation state

if st.session_state.conversation.history:
    last_message = st.session_state.conversation.history[-1]["content"]

    if "switch to annual" in last_message.lower():
        if st.session_state.switch_to_annual_stage is None:
            # Step 1: Show confirmation message with Yes/No buttons
            st.warning("⚠️ Please double-check if you want to switch to annual.")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Yes, switch to annual"):
                    st.session_state.switch_to_annual_stage = "ask_account"
                    st.experimental_rerun()  # ✅ Force UI update after first click

            with col2:
                if st.button("❌ No, go back to chat"):
                    st.session_state.switch_to_annual_stage = "cancel"
                    st.experimental_rerun()  # ✅ Force UI update after first click

        elif st.session_state.switch_to_annual_stage == "ask_account":
            # Step 2: Ask for the user's account number
            account_number = st.text_input("Please enter your account number:")

            if account_number:
                customer_data = fetch_customer_details(account_number)  # ✅ Fetch details from backend

                if customer_data:  # ✅ Make sure the account exists
                    with st.spinner("Processing..."):
                        result = execute_website_agent(customer_data, account_number)  # ✅ Pass correct data
                        st.session_state.result_message = result  # Store result in session
                        #st.session_state.pre_screenshot = pre_screenshot
                        #st.session_state.post_screenshot = post_screenshot
                        st.session_state.switch_to_annual_stage = "completed"  # ✅ Change state to keep message visible
                        st.experimental_rerun()

                else:
                    st.error("❌ Account number not found! Please try again.")

        elif st.session_state.switch_to_annual_stage == "completed":
            # ✅ Show the final success message and screenshots
            st.success(st.session_state.result_message)
            #st.image(st.session_state.pre_screenshot, caption="Pre-Submission Screenshot")
            #st.image(st.session_state.post_screenshot, caption="Post-Submission Screenshot")

            # ✅ Button to return to chat
            if st.button("⬅ Go back to chat"):
                st.session_state.switch_to_annual_stage = None  # Reset state
                st.experimental_rerun()

            elif st.session_state.switch_to_annual_stage == "cancel":
                st.session_state.switch_to_annual_stage = None  # Reset state
                st.session_state.conversation.history.append({"role": "assistant", "content": "Okay! Returning to chat mode. Feel free to ask anything else."})
                st.experimental_rerun()  # ✅ Ensure it fully resets back to chat UI




# ---- Upload Bill Section ----
st.markdown("<h3>📄 Upload your NEM Bill:</h3>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["pdf"])

if uploaded_file:
    with st.spinner("Extracting data from your bill..."):
        extracted_data = extract_bill_data(uploaded_file)
        
        # Display the bill data
        display_bill_data(extracted_data)
        
        # Add the bill data to the conversation context
        if 'error' not in extracted_data:
            summary = extracted_data.get('bill_summary', {})
            bill_info = (
                f"I've uploaded a bill with "
                f"total amount ${summary.get('total_amount_due', 'unknown')}."
            )
            st.session_state.conversation.add_message("user", bill_info)
            
            # Get assistant response about the bill
            conversation_history = st.session_state.conversation.get_formatted_history()
            answer = get_response(conversation_history)
            st.session_state.conversation.add_message("assistant", answer)
