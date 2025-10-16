import os
from openai import OpenAI
from embeddings import search_articles  # your vector DB functions
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def answer_question(question: str, top_k: int = 10):
    """
    1. Search Pinecone for relevant articles
    2. Build GPT prompt using full article metadata
    3. Return GPT's answer + list of articles used
    """
    results = search_articles(question, top_k=top_k)

    if not results:
        return "Sorry, I couldn't find any relevant news articles.", []

    # Build GPT context using full metadata
    context_text = ""
    for i, article in enumerate(results, 1):
        context_text += (
            f"{i}. Title: {article.get('title', 'N/A')}\n"
            f"   Description: {article.get('description', 'N/A')}\n"
            f"   Content: {article.get('content', 'N/A')}\n"
            f"   Author: {article.get('author', 'Unknown')}\n"
            f"   Source: {article.get('source', 'Unknown')}\n"
            f"   Published At: {article.get('publishedAt', 'Unknown')}\n"
            f"   URL: {article.get('url', 'No URL')}\n\n"
        )

    prompt = f"""
             are a helpful news assistant. Using the following news articles, answer the question below.

            News Articles:
            {context_text}

            Question: {question}

            Answer based only on the articles above. If the articles don't contain the answer, say "I don't know based on the available articles."
            """

    # GPT call
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    answer = response.choices[0].message.content.strip()

    # Return answer + list of full articles used
    return answer, results
