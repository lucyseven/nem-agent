import streamlit as st
from src.chatbot.rag import get_response
from src.chatbot.conversation import ConversationManager
from src.pdf_processing.pdf_extractor import extract_bill_data
from src.agents.website_agent import execute_website_agent

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
st.image("app/assets/sdcp_logo.jpg", width=200, caption="", use_container_width=False)

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

# We store the user’s typed text in "temp_user_input"
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
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

# ---- Render existing conversation so far ----
display_chat_bubbles()

# ---- Text Input with on_change callback (no Send button needed) ----
st.text_input(
    "Type your message...",
    key="temp_user_input",
    on_change=send_message,
    placeholder="Type here and press Enter to send",
    label_visibility="collapsed"
)

# ---- Check if user wants to switch to annual billing ----
# We'll read the last user message if it exists
if st.session_state.conversation.history:
    last_message = st.session_state.conversation.history[-1]["content"]
    if "switch to annual" in last_message.lower():
        if st.button("⚡ Switch to Annual Billing"):
            with st.spinner("Processing..."):
                result = execute_website_agent()
                st.success("✅ Switched to Annual Billing!")
                st.write(result)

# ---- Upload Bill Section ----
st.markdown("<h3>Upload your NEM Bill:</h3>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["pdf"])
if uploaded_file:
    with st.spinner("Extracting data..."):
        extracted_data = extract_bill_data(uploaded_file)
    st.json(extracted_data)
