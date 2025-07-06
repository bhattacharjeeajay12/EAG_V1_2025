"""
- This script searches a FAISS index built from web content (using OpenAI's text-embedding-3-small model, saved with LangChain) and opens the most relevant URL in a browser.
- Steps performed:
    - Loads the FAISS index and metadata from files using LangChain's FAISS.load_local().
    - Takes a user query and generates an embedding for it using OpenAI API.
    - Searches the index for the most similar chunk.
    - Returns the corresponding URL and opens it in the default web browser.
- Useful for semantic search over indexed web browsing content.
"""

import os
import webbrowser
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# -- CONFIG --
INDEX_DIR = os.path.join("data", "faiss_web_index_openai_lc")

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def search_and_open(query: str, index_dir=INDEX_DIR, k=2):
    """
    Search the FAISS index for the chunk most similar to the query, return and open the corresponding URL.
    """
    vector_store = FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)
    docs = vector_store.similarity_search(query, k=k)
    if not docs:
        print("No results found.")
        return None
    doc = docs[0]
    url = doc.metadata.get("url", "No URL")
    print(f"Best match URL: {url}")
    print(f"Matched chunk: {doc.page_content[:200]}...")
    webbrowser.open(url)
    return url

if __name__ == "__main__":
    query = input("Enter your search text: ")
    search_and_open(query) 