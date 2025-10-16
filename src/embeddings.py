# vector_db.py
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import os
import time
from dotenv import load_dotenv
import re
import unicodedata
import uuid

load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

INDEX_NAME = "news-ai"
DIMENSION = 1536  # text-embedding-3-small

def make_safe_id(text):
    # Normalize Unicode and remove non-ASCII characters
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    # Replace spaces and special chars with underscores
    text = re.sub(r'[^a-zA-Z0-9_-]', '_', text)
    return text[:90]  # limit length to be safe


def init_pinecone_index(reset=False):
    """
    Initializes the Pinecone index.
    - If reset=True: deletes and recreates the index.
    - If the index doesn't exist: creates it.
    - Waits until it's ready before returning the index handle.
    """
    existing_indexes = [i.name for i in pc.list_indexes()]

    # If resetting, or if index doesn't exist
    if reset or INDEX_NAME not in existing_indexes:
        if INDEX_NAME in existing_indexes:
            print("🗑️ Deleting existing index...")
            pc.delete_index(INDEX_NAME)
            time.sleep(5)  # brief pause before recreate


        print("🧱 Creating new Pinecone index...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

        # Wait for index to be ready
        print("⏳ Waiting for index to be ready...")
        while True:
            status = pc.describe_index(INDEX_NAME)
            if status.status.get("ready"):
                break
            time.sleep(2)
        print("✅ Pinecone index is ready!")

    return pc.Index(INDEX_NAME)


def get_embedding(text):
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    print("✅ Generated embedding.", res.data[0].embedding[:5], "...")
    return res.data[0].embedding

def store_articles(articles: list, index):
    """
    Takes a list of article dicts and stores their embeddings in Pinecone.
    Each article should look like:
    {
        "title": "Some title",
        "description": "Some description text..."
    }
    """

    existing_ids = set()
    for record in index.list():
        existing_ids.add(record.id)
    vectors = []
    print(f"Storing {len(articles)} articles...")
    for article in articles:
        title = article["title"].strip()
        description = article["description"]

        # Use title as ID (ensure it's not too long for Pinecone)
        article_id = title[:90]  # truncate to avoid Pinecone ID length limit
        if article_id in existing_ids:
            continue

        article_id = make_safe_id(article_id)

        # Add small random suffix to prevent accidental duplicates
        article_id = f"{article_id}_{uuid.uuid4().hex[:6]}"

        embedding = get_embedding(description)
        vectors.append({
            "id": article_id,
            "values": embedding,
            "metadata": article
        })
    print("Storing vectors in Pinecone...")
    index.upsert(vectors=vectors)
    print(f"✅ Stored {len(vectors)} articles in Pinecone.")


def refresh_vector_db(articles):
    """
    Clears any existing Pinecone index and repopulates it with new articles.
    """
    print("🔁 Refreshing Pinecone vector DB...")
    index = init_pinecone_index(reset=True)
    store_articles(articles, index)
    print(f"✅ {len(articles)} articles refreshed in Pinecone.")

def search_articles(query: str, top_k: int = 10):
    """
    Finds the top_k most relevant articles for a given query.
    Returns a list of matched metadata (title, description).
    """
    index = init_pinecone_index(reset=False)
    query_embedding = get_embedding(query)
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    matches = []
    for match in results["matches"]:
        meta = match["metadata"]
        matches.append(meta)
    return matches
