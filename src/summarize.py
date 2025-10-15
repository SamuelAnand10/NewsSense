import os
from dotenv import load_dotenv
import openai
from collections import defaultdict

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_category(descriptions, category):
    """
    descriptions: list of strings (article descriptions)
    category: category name (e.g., 'technology')
    """
    if not descriptions:
        return f"No {category} news available today."

    # Join all descriptions into one string
    text = "\n".join(descriptions)

    prompt = f"""
    You are an analytical journalist AI. Analyze today's {category} news articles.

    1. Summarize the main events and trends into 3-4 concisely.
    2. Determine the overall sentiment (Positive, Negative, or Neutral).
    3. Give a short reasoning for your sentiment classification.

    Articles:
    {text[:8000]}
    """

    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
)

    summary = response.choices[0].message.content
    return summary


def summarize_by_category(articles):
    """
    articles: list of dicts with 'description' and 'category'
    Returns: dict {category: summary}
    """
    grouped = defaultdict(list)

    # Group descriptions by category
    for article in articles:
        desc = article.get("description")
        cat = article.get("category", "General")
        if desc:
            grouped[cat].append(desc)

    # Summarize each category
    summaries = {}
    for cat, desc_list in grouped.items():
        summaries[cat] = summarize_category(desc_list, cat)

    return summaries