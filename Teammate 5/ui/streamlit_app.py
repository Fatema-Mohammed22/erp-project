# Streamlit app for Helios ERP Conversational Interface
import streamlit as st
import requests

st.set_page_config(page_title="Helios ERP", layout="wide")

st.title("🌟 Helios ERP - Conversational Interface")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Input box
user_input = st.text_input("Ask a question (e.g., 'Show me the sales report for last month'):")

if st.button("Send") and user_input:
    # Append user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Send request to backend (FastAPI Router Agent)
    try:
        response = requests.post(
            "http://localhost:8000/ask",
            json={
                "question": user_input, 
                "chat_history": st.session_state.messages
                }
        )
        response.raise_for_status()
        data = response.json()
        answer = data.get("answer", "⚠️ No answer found.")
    except requests.exceptions.RequestException as e:
        answer = f"❌ Error: {e}"

    # Append assistant message to chat history
    st.session_state.messages.append({"role": "assistant", "content": answer})

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**🧑 You:** {msg['content']}")
    else:
        st.markdown(f"**🤖 Helios ERP:** {msg['content']}")