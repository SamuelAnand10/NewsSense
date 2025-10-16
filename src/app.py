
import streamlit as st
from datetime import datetime
from fetch_news import fetch_all_news
from summarize import summarize_by_category
from chatbot import answer_question
from embeddings import refresh_vector_db

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="NewsSense", layout="wide", page_icon="🧠")

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
    html, body, [class*="css"] {
        font-family: 'Manrope', sans-serif !important;
        background-color: #121212;
        color: #EAEAEA;
    }

    .user-bubble {
        background-color: #007AFF;
        color: white;
        padding: 10px 15px;
        border-radius: 16px;
        margin-left: auto;
        text-align: right;
        width: fit-content;
        max-width: 60%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        font-weight: 500;
        letter-spacing: 0.1px;
    }

    .ai-bubble {
        background-color: #1E1E1E;
        color: #EAEAEA;
        padding: 10px 15px;
        border-radius: 16px;
        margin-right: auto;
        text-align: left;
        width: fit-content;
        max-width: 60%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        font-weight: 400;
        letter-spacing: 0.1px;
    }

    h1, h2, h3, h4 {
        font-family: 'Manrope', sans-serif !important;
        font-weight: 600;
        color: #FFFFFF;
        letter-spacing: 0.4px;
    }

    div.stButton > button {
        background-color: #007AFF;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6em 1.2em;
        font-weight: 600;
        font-family: 'Manrope', sans-serif;
        transition: background-color 0.3s ease, transform 0.2s ease;
    }

    div.stButton > button:hover {
        background-color: #409CFF;
        transform: translateY(-2px);
    }

    textarea, input {
        background-color: #1E1E1E !important;
        color: #EAEAEA !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
        font-family: 'Manrope', sans-serif !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #1E1E1E;
    }
    section[data-testid="stSidebar"] * {
        color: #EAEAEA !important;
    }

    .streamlit-expanderHeader {
        font-weight: 600 !important;
        color: #007AFF !important;
        font-family: 'Manrope', sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)


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
        # articles = fetch_all_news()  # Real API call
        category = "general"

        st.session_state.articles = [
    {
        "title": "Scientists Discover Chocolate Moon",
        "description": "A group of researchers claim they found evidence of a moon made entirely of chocolate orbiting a distant planet.",
        "content": "In a shocking revelation, scientists from the Galactic Institute announced that a distant moon is composed entirely of chocolate. While evidence is still being verified, the news has gone viral.",
        "url": "https://fake-news.com/chocolate-moon",
        "source": "Galactic News",
        "publishedAt": datetime.now().isoformat(),
        "category": category
    },
    {
        "title": "AI Predicts Next Year's Fashion Trends",
        "description": "An AI system predicts neon colors will dominate the fashion scene next year.",
        "content": "By analyzing millions of social media posts, AI TrendBot has predicted that neon colors will take over fashion runways next year, sparking excitement among designers.",
        "url": "https://fake-news.com/ai-fashion-trends",
        "source": "TechStyle",
        "publishedAt": datetime.now().isoformat(),
        "category": category
    },
    {
        "title": "Flying Cars Approved in Europe",
        "description": "The European Transportation Agency has approved regulations for flying cars in select cities.",
        "content": "Europe is set to become the first continent to allow flying cars in urban areas by 2026, with strict safety regulations in place for operators.",
        "url": "https://fake-news.com/flying-cars-europe",
        "source": "Future Transport Daily",
        "publishedAt": datetime.now().isoformat(),
        "category": category
    },
    {
        "title": "Cats Form Union to Demand Better Treats",
        "description": "Domestic cats are allegedly organizing to demand higher-quality treats and longer nap times.",
        "content": "Pet owners are surprised as cats across several households appear to be coordinating actions through social media to demand better treats and more frequent naps.",
        "url": "https://fake-news.com/cat-union",
        "source": "Feline Times",
        "publishedAt": datetime.now().isoformat(),
        "category": category
    },
    {
        "title": "Time Travel Tourism Launches in 2030",
        "description": "A tech startup claims to have created a safe time travel experience for tourists.",
        "content": "ChronoTravel, a startup specializing in temporal tourism, announced its first commercial time travel tours starting in 2030. Interested tourists can book trips to the past or future.",
        "url": "https://fake-news.com/time-travel-tourism",
        "source": "Temporal News Network",
        "publishedAt": datetime.now().isoformat(),
        "category": category
    }
]

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
