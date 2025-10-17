
import streamlit as st
from datetime import datetime
from fetch_news import fetch_all_news
from summarize import summarize_by_category
from chatbot import answer_question
from embeddings import refresh_vector_db

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="NewsSense", layout="wide", page_icon="📰")

# -------------------- CUSTOM CSS --------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600&family=Playfair+Display:ital,wght@0,900&display=swap');

    /* ---------- BODY / BACKGROUND ---------- */
    html, body, [class*="css"] {
        font-family: 'Manrope', sans-serif;
        background-color: #1e1e1e;  /* dark mode */
        color: #e0e0e0;
    }

    /* ---------- APP TITLE / HEADINGS ---------- */
    .app-title {
        font-family: 'Playfair Display', serif;
        font-weight: 900;  /* bold/black style */
        letter-spacing: 1px;
        color: #ffffff;
        font-size: 3em;
        text-align: center;
        margin-bottom: 0.2em;
    }

    .app-caption {
        font-family: 'Manrope', sans-serif;
        font-weight: 400;
        font-size: 1.2em;
        text-align: center;
        color: #b0b0b0;
        margin-bottom: 2em;
    }

    /* ---------- SUMMARY CARDS ---------- */
    .summary-card {
        background-color: #2a2a2a;
        padding: 1em 1.2em;
        border-radius: 12px;
        margin-bottom: 15px;
        color: #f0f0f0;
    }

    .summary-card h4 {
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        margin-bottom: 0.5em;
        color: #ffffff;
    }

    .summary-card p {
        font-family: 'Manrope', sans-serif;
        font-weight: 400;
        color: #d0d0d0;
        margin: 0;
    }

    /* ---------- CHAT BUBBLES ---------- */
    .user-bubble {
        background-color: #3a3a3a;
        color: #f1f1f1;
        padding: 12px;
        border-radius: 15px;
        margin-left: 50%;
        text-align: right;
        width: fit-content;
        max-width: 45%;
        font-family: 'Manrope', sans-serif;
        margin-bottom: 10px;
    }

    .ai-bubble {
        background-color: #2a2a72;
        color: #f1f1f1;
        padding: 12px;
        border-radius: 15px;
        margin-right: 50%;
        text-align: left;
        width: fit-content;
        max-width: 45%;
        font-family: 'Manrope', sans-serif;
        margin-bottom: 10px;
    }

    /* ---------- CHAT SOURCES ---------- */
    .chat-sources {
        font-family: 'Manrope', sans-serif;
        font-size: 0.9em;
        color: #a0a0a0;
        margin-left: 1em;
    }

    /* ---------- BUTTONS ---------- */
    .stButton>button {
        background-color: #4a4aff;
        color: #fff;
        font-family: 'Manrope', sans-serif;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5em 1em;
        transition: 0.2s;
    }

    .stButton>button:hover {
        background-color: #6a6aff;
        cursor: pointer;
    }

    /* ---------- SIDEBAR ---------- */
    [data-testid="stSidebar"] {
        background-color: #2a2a2a;
        color: #e0e0e0;
    }

    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        font-family: 'Playfair Display', serif;
        color: #ffffff;
    }

    [data-testid="stSidebar"] p, [data-testid="stSidebar"] .stText {
        font-family: 'Manrope', sans-serif;
        color: #c0c0c0;
    }

    /* ---------- DIVIDERS ---------- */
    hr {
        border: none;
        border-top: 1px solid #444;
        margin: 1.5em 0;
    }

    /* Title color switch for light mode */
    @media (prefers-color-scheme: light) {
        .app-title {
            color: #000000 !important;  /* black title in light mode */
        }
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
# -------------------- HEADER --------------------
st.markdown(
    """
    <h1 class='app-title'>NewsSense — Daily News Summaries</h1>
    <p class='app-caption'>Stay informed with concise summaries and smart insights.</p>
    """,
    unsafe_allow_html=True
)



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
