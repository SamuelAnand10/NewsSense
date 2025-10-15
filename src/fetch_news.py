import os 
import requests
from dotenv import load_dotenv
load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

CATEGORIES = [
    "world",
    "politics",
    "technology",
    "business",
    "science",
    "health",
    "entertainment",
    "sports"
]

def fetch_global_news(category, page_size=20):
    """
    Fetch global news using the 'everything' endpoint.
    You can specify a query like 'technology', 'politics', or 'world' for general news.
    """
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={category}&"
        f"language=en&"
        f"pageSize={page_size}&"
        f"sortBy=publishedAt&"
        f"apiKey={NEWS_API_KEY}"
    )
    
    response = requests.get(url)
    data = response.json()

    if data.get("status") != "ok":
        print(f"Error fetching news: {data.get('message')}")
        return []

    articles = []
    for article in data.get("articles", []):
        articles.append({
            "title": article.get("title"),
            "description": article.get("description"),
            "content": article.get("content"),
            "url": article.get("url"),
            "source": article["source"]["name"],
            "publishedAt": article.get("publishedAt"),
            "category": category
        })

    return articles


def fetch_all_news():
    """
    Fetch news from all categories and combine them into a single list.
    """
    all_articles = []
    for category in CATEGORIES:
        articles = fetch_global_news(category)
        all_articles.extend(articles)
    
    # Sort articles by published date, most recent first
    all_articles.sort(key=lambda x: x['publishedAt'], reverse=True)
    
    return all_articles
