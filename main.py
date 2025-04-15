import streamlit as st
from chat_logger import log_chat
from feedback import log_feedback
from utils import load_chunks_from_txt, embed_chunks_with_faiss, search, query_mistral
import uuid
import os
from dotenv import load_dotenv
import base64
import sys

if 'torch.classes' in sys.modules:
    del sys.modules['torch.classes']


load_dotenv()

st.set_page_config(page_title="🎓 AskAria", layout="wide")

# Set background
def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("logo/bg2.jpg")

# Load logo
def get_image_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_base64 = get_image_base64("logo/acem_logo.png")

st.markdown(f"""
<div style="display: flex; align-items: center; justify-content: center; gap: 15px; margin-top: 20px; margin-bottom: 30px;">
    <img src="data:image/png;base64,{logo_base64}" width="60" />
    <h1 style="margin: 0; font-size: 2.5em;">AskAria: Your ACEM Admission Buddy</h1>
</div>
""", unsafe_allow_html=True)

# Styling
st.markdown("""
    <style>
    .appview-container > .main > div {
        padding-bottom: 0 !important;
    }
    .stChatInput {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100vw;
        background-color: #0e0e0e;
        padding: 1.5rem 2rem;
        z-index: 999;
        border-top: 1px solid #333;
        box-shadow: 0 -1px 8px rgba(0, 0, 0, 0.4);
    }
    .stChatInput textarea {
        background-color: #1c1c1c !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid #444 !important;
    }
    .block-container {
        padding-bottom: 140px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Session state init
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if st.button("Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()

# Load vector DB
@st.cache_resource
def load_vector_db():
    chunks = load_chunks_from_txt("data/main.txt")
    vectordb = embed_chunks_with_faiss(chunks)
    return vectordb




vectordb = load_vector_db()

# Suggested questions
st.markdown("#### 💡 Suggested Questions")
suggested_questions = [
    "What courses are offered at ACEM?",
    "What is the admission process?",
    "Does the college offer scholarships?",
    "What are the placement statistics?",
    "Where is the college located?",
]

selected_question = None
for question in suggested_questions:
    if st.button(question):
        selected_question = question

# Show chat history
for i in range(len(st.session_state.chat_history)):
    chat = st.session_state.chat_history[i]
    with st.chat_message(chat["role"]):
        st.markdown(chat["message"])
        if chat["role"] == "bot":
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍", key=f"like_{chat['id']}"):
                    log_feedback(chat["id"], "like")
                    st.success("Thanks for your feedback!")
            with col2:
                if st.button("👎", key=f"dislike_{chat['id']}"):
                    log_feedback(chat["id"], "dislike")
                    st.info("We'll improve based on your feedback!")

# Chat input (handle selected question or typed input)
query = selected_question or st.chat_input("Ask a question about the college:")

if query:
    greetings = ["hi", "hello", "hey", "hii", "helo", "good morning", "good evening"]
    if query.strip().lower() in greetings:
        response = "Hello! I'm AskAria, your ACEM Admission Buddy. How may I help you today?"
        scores = []
    else:
        top_chunks, scores = search(query, vectordb)
        context = "\n".join(top_chunks)
        short_question = f"{query}\nPlease keep the answer under 100 words."
        response = query_mistral(context, short_question)

    chat_id = str(uuid.uuid4())[:8]
    st.session_state.chat_history.append({"id": chat_id, "role": "user", "message": query})
    st.session_state.chat_history.append({
        "id": chat_id, 
        "role": "bot", 
        "message": response,
        # "confidence": round(scores[0] * 100, 2) if scores else None
    })


    log_chat(query, response, scores)
    st.rerun()
