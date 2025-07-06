"""
- This script searches a FAISS index built from web content and opens the most relevant URL in a browser.
- Steps performed:
    - Loads the FAISS index and metadata from files.
    - Takes a user query and generates an embedding for it.
    - Searches the index for the most similar chunk.
    - Returns the corresponding URL and opens it in the default web browser.
- Useful for semantic search over indexed web browsing content.
"""

import faiss
import numpy as np
import requests
import json
import webbrowser
import os

# -- CONFIG --
INDEX_PATH = os.path.join("data", "faiss_web_index.bin")
META_PATH = os.path.join("data", "faiss_web_metadata.json")

def get_embedding(text: str) -> np.ndarray:
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "nomic-embed-text",
            "prompt": text
        }
    )
    response.raise_for_status()
    return np.array(response.json()["embedding"], dtype=np.float32)

def search_and_open(query: str, index_path=INDEX_PATH, meta_path=META_PATH):
    """
    Search the FAISS index for the chunk most similar to the query, return and open the corresponding URL.
    """
    # Load index and metadata
    index = faiss.read_index(index_path)
    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    # Embed the query
    query_vec = get_embedding(query).reshape(1, -1)
    D, I = index.search(query_vec, k=1)
    idx = I[0][0]
    match = metadata[idx]
    url = match["url"]
    print(f"Best match URL: {url}")
    print(f"Matched chunk: {match['chunk'][:200]}...")
    webbrowser.open(url)
    return url

if __name__ == "__main__":
    query = input("Enter your search text: ")
    search_and_open(query)  