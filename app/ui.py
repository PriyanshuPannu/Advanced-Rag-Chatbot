import streamlit as st
import requests
from database import (
    init_db,
    create_conversation,
    save_message,
    load_messages,
    load_conversations,
    delete_conversation
)

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="🤖 AI Research Paper Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

# ---------- DARK MODE CSS ----------
st.markdown("""
<style>
[data-testid="stAppViewContainer"], 
[data-testid="stAppViewContainer"] > div:first-child {
    background-color: #0F111A;
    color: #FFFFFF;
}

header, [data-testid="stToolbar"], [data-testid="stHeader"] {
    background-color: #0F111A !important;
}

[data-testid="stSidebar"] {
    background-color: #1A1C29;
    color: #FFFFFF;
}

h1 {
    color: #FFFFFF;
    text-align: center;
}

.stTextInput>div>div>input {
    background-color: #252836;
    color: #FFFFFF;
    border-radius: 12px;
    padding-left: 12px;
    height: 45px;
    font-size: 16px;
}

.stButton>button {
    background-color: #4B5CFF;
    color: white;
    border-radius: 8px;
    width: 100%;
    height: 45px;
    font-size: 16px;
    margin-top: 10px;
}

.user-msg {
    background-color: #4B5CFF;
    color: white;
    padding: 12px;
    border-radius: 12px;
    max-width: 80%;
    margin-bottom: 10px;
    margin-left: auto;
}

.ai-msg {
    background-color: #2A2C37;
    color: #E4E6EB;
    padding: 12px;
    border-radius: 12px;
    max-width: 80%;
    margin-bottom: 10px;
}

.stTextInput>div>div>input::placeholder {
    color: #FFFFFF !important;
    opacity: 1;
}

.source-card {
    background-color: #1A1C29;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 6px;
    font-size: 14px;
}

.stDownloadButton>button {
    background-color: #4B5CFF;
    color: white;
    border-radius: 8px;
    width: 100%;
    height: 45px;
    font-size: 16px;
    margin-top: 10px;
}

.stDownloadButton>button:hover {
    background-color: #6c757d;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("<h1>🤖 ARPA </h1>", unsafe_allow_html=True)

# ---------- SESSION ----------
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

# ---------- SIDEBAR ----------
st.sidebar.title("Conversation History")

if st.sidebar.button("➕ New Conversation"):
    st.session_state.conversation_id = create_conversation()
    st.rerun()

conversations = load_conversations()

for convo in conversations:

    convo_messages = load_messages(convo["id"])

    if convo_messages:
        first_user_msg = next(
            (m["msg"] for m in convo_messages if m["role"] == "user"),
            "New Conversation"
        )
        title = first_user_msg[:40] + ("..." if len(first_user_msg) > 40 else "")
    else:
        title = "New Conversation"

    col1, col2 = st.sidebar.columns([4,1])

    with col1:
        if st.button(title, key=f"select_{convo['id']}"):
            st.session_state.conversation_id = convo["id"]
            st.rerun()

    with col2:
        if st.button("🗑", key=f"delete_{convo['id']}"):
            delete_conversation(convo["id"])

            if st.session_state.conversation_id == convo["id"]:
                st.session_state.conversation_id = None

            st.rerun()

# ---------- MAIN LAYOUT ----------
main_col, _ = st.columns([4,1])

with main_col:
    user_input = st.text_input(
        "",
        placeholder="Type your question here...",
        key="input_box"
    )

    submit_clicked = st.button("Submit")

# ---------- CREATE CONVO IF NONE ----------
if st.session_state.conversation_id is None:
    st.session_state.conversation_id = create_conversation()

# ---------- RUN QUERY ----------
if submit_clicked and user_input:

    with st.spinner("Generating answer..."):

        try:
            response = requests.post(
                "http://127.0.0.1:8000/chat",
                params={"query": user_input}
            )

            if response.status_code == 200:

                data = response.json()

                save_message(
                    st.session_state.conversation_id,
                    "user",
                    user_input
                )

                save_message(
                    st.session_state.conversation_id,
                    "ai",
                    data["response"],
                    data.get("sources", [])
                )

                st.rerun()

        except Exception as e:
            st.error(f"API Error: {e}")

# ---------- LOAD CHAT ----------
messages = load_messages(st.session_state.conversation_id)

# ---------- DISPLAY CHAT ----------
for chat in messages:

    if chat["role"] == "user":

        st.markdown(
            f"<div class='user-msg'>{chat['msg']}</div>",
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"<div class='ai-msg'>{chat['msg']}</div>",
            unsafe_allow_html=True
        )

        if chat["sources"]:

            st.markdown("<b>Sources:</b>", unsafe_allow_html=True)

            for src in chat["sources"]:

                pdf_name = src.get("pdf", "Unknown PDF")
                page = src.get("page", "Unknown")

                st.markdown(
                f"""
                <div class='source-card'>
                📄 <b>{pdf_name}</b><br>
                📑 Page: {page}<br>
                </div>
                """,
                unsafe_allow_html=True
                )

                pdf_path = f"data/{pdf_name}"

                try:
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label=f"Download {pdf_name}",
                            data=f,
                            file_name=pdf_name,
                            mime="application/pdf",
                            key=f"{pdf_name}_{page}",
                        )
                except:
                    pass