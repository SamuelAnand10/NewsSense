
import streamlit as st
from datetime import datetime
from fetch_news import fetch_all_news
from summarize import summarize_by_category
from chatbot import answer_question
from embeddings import refresh_vector_db

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="NewsSense", layout="wide", page_icon="🧠")

# -------------------- CUSTOM CSS --------------------
# -------------------- HEADER --------------------
st.markdown(
    """
    <h1 class='app-title'>📰 NewsSense — Daily News Summaries</h1>
    <p class='app-caption'>Stay informed with concise summaries and smart insights.</p>
    """,
    unsafe_allow_html=True
)

# CSS addition for caption
st.markdown(
    """
    <style>
    .app-caption {
        font-family: 'Manrope', sans-serif;
        font-weight: 400;
        font-size: 1.2em;
        color: #d0d0d0;
        text-align: center;
        margin-bottom: 30px;
    }

    /* Optional: Summary cards styling */
    .summary-card {
        background-color: #2a2a2a;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)




# -------------------- SIDEBAR --------------------

st.sidebar.title("NewsSense")
st.sidebar.markdown("**Your Daily AI-Powered News Digest**")
st.sidebar.markdown("---")
st.sidebar.markdown("### Options")
refresh_news = st.sidebar.button("🔄 Fetch Latest News")
st.sidebar.markdown("### About")
st.sidebar.info("Powered by advanced summarization and question-answering models to keep you informed.")

# -------------------- SESSION STATE --------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "summaries" not in st.session_state:
    st.session_state.summaries = {}

if "articles" not in st.session_state:
    st.session_state.articles = []

# -------------------- HEADER --------------------
st.title("NewsSense — Daily News Summaries")
st.caption("Stay informed with concise summaries and smart insights.")

# -------------------- FETCH NEWS --------------------
if refresh_news:
    with st.spinner("Fetching global news..."):
        st.session_state.articles = fetch_all_news()  # Real API call
        category = "general"

        st.info("Updating knowledge base...")
        refresh_vector_db(st.session_state.articles)

        with st.spinner("Summarizing news by category..."):
            st.session_state.summaries = summarize_by_category(st.session_state.articles)

        st.success("**News updated**")

# -------------------- DISPLAY SUMMARIES --------------------
if st.session_state.summaries:
    st.subheader("Today's Summaries")

    for category, summary in st.session_state.summaries.items():
        st.markdown(f"<div class='summary-card'><h4>{category.title()}</h4><p>{summary}</p></div>", unsafe_allow_html=True)
else:
    st.info("Click **'Fetch Latest News'** in the sidebar to get today's summaries.")

# -------------------- CHAT INTERFACE --------------------
st.markdown("---")
st.subheader("Chat with NewsSense")

with st.form("chat_form", clear_on_submit=True):
    user_question = st.text_input("Ask a question about today's news:")
    submitted = st.form_submit_button("Send")

    if submitted and user_question:
        with st.spinner("Thinking..."):
            answer, sources = answer_question(user_question)

        st.session_state.chat_history.append({
            "role": "user", "message": user_question
        })
        st.session_state.chat_history.append({
            "role": "ai", "message": answer, "sources": sources
        })

# -------------------- DISPLAY CHAT --------------------
if st.session_state.chat_history:
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f"<div class='user-bubble'>{chat['message']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ai-bubble'>{chat['message']}</div>", unsafe_allow_html=True)
            if "sources" in chat and chat["sources"]:
                st.markdown("**Sources:**")
                for s in chat["sources"]:
                    st.markdown(f"- [{s['title']}]({s.get('url', '#')}) — {s.get('source', 'Unknown')}")
