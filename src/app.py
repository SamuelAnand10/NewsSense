import streamlit as st
from fetch_news import fetch_all_news
from summarize import summarize_by_category
from chatbot import answer_question
from embeddings import refresh_vector_db, store_articles
from datetime import datetime

st.set_page_config(page_title="NewsSense", layout="wide")
st.title("📰 NewsSense — Daily News Summaries")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "summaries" not in st.session_state:
    st.session_state.summaries = {}

if "articles" not in st.session_state:
    st.session_state.articles = []

st.markdown(
    """
    <style>
    .user-bubble {
        background-color: #a6f0c6;
        padding: 10px;
        border-radius: 15px;
        margin-left: 50%;
        text-align: right;
        width: fit-content;
        max-width: 45%;
    }
    .ai-bubble {
        background-color: #a0c4ff;
        padding: 10px;
        border-radius: 15px;
        margin-right: 50%;
        text-align: left;
        width: fit-content;
        max-width: 45%;
    }
    </style>
    """, unsafe_allow_html=True
)

# Button to fetch news
if st.button("Fetch Daily News"):
    with st.spinner("Fetching global news..."):
        #articles = fetch_all_news()
        category = "general"  # youst.session_state.articles can change per batch

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


        st.info("Refreshing Vector DB...")
        refresh_vector_db(st.session_state.articles)

        with st.spinner("Summarizing news by category..."):
            st.session_state.summaries = summarize_by_category(st.session_state.articles)

        st.success("✅ Daily news summaries ready!")

# --- Display summaries persistently ---
if st.session_state.summaries:
    st.header("🗂️ Daily News Summaries")
    for category, summary in st.session_state.summaries.items():
        with st.expander(f"{category.upper()}"):
            st.write(summary)


st.header("💬 Ask Questions About the News")

# Using a form for chat input
with st.form("chat_form", clear_on_submit=True):
    user_question = st.text_input("Enter your question here:")
    submitted = st.form_submit_button("Send Question")

    if submitted and user_question:
        with st.spinner("Generating answer..."):
            answer, sources = answer_question(user_question)

        # Add both user and AI messages to chat history
        st.session_state.chat_history.append({"role": "user", "message": user_question})
        st.session_state.chat_history.append({"role": "ai", "message": answer, "sources": sources})

# --- Display chat messages ---
st.header("🗨️ Chat Conversation")
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f'<div class="user-bubble">{chat["message"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-bubble">{chat["message"]}</div>', unsafe_allow_html=True)
        if "sources" in chat and chat["sources"]:
            st.markdown("**Sources:**")
            for s in chat["sources"]:
                # Make the source name a clickable link
                st.markdown(f"- [{s['title']}]({s.get('url', '#')}) by {s.get('source', 'Unknown')}")

