"""
- This script builds a FAISS index from scraped web content using OpenAI's text-embedding-3-small model and saves it in a format compatible with LangChain's FAISS.load_local().
- Steps performed:
    - Loads scraped_contents.json (list of {link, content} dicts).
    - Chunks each content into overlapping segments.
    - Gets embeddings for each chunk using OpenAI's API.
    - Stores chunk metadata (URL, chunk text, chunk id) in LangChain Document objects.
    - Creates a FAISS index and adds all chunk embeddings.
    - Saves the index and metadata using LangChain's FAISS.save_local().
- Useful for semantic search over web browsing content with chunk-level granularity.
"""

import os
import openai
import json
import time
from dotenv import load_dotenv
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

# -- CONFIG --
CHUNK_SIZE = 40
CHUNK_OVERLAP = 10
INPUT_JSON = os.path.join("data", "scraped_contents.json")
INDEX_DIR = os.path.join("data", "faiss_web_index_openai_lc")

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# -- HELPERS --
def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunk = " ".join(words[i:i+size])
        if chunk:
            chunks.append(chunk)
    return chunks

def build_index(use_browser_content=False):
    """
    Build FAISS index from scraped content using OpenAI embeddings and save with LangChain.
    """
    if use_browser_content:
        input_json = os.path.join("data", "scraped_contents.json")
    else:
        input_json = INPUT_JSON

    with open(input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    docs = []
    for entry_idx, entry in enumerate(data):
        url = entry["link"]
        content = entry["content"]
        chunks = chunk_text(content)
        for idx, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "url": url,
                    "chunk_id": f"entry{entry_idx}_chunk{idx}"
                }
            )
            docs.append(doc)
        print(f"Processed {len(chunks)} chunks from {url}")
        time.sleep(0.5)  # Small delay to avoid overwhelming OpenAI API

    # -- CREATE FAISS INDEX WITH LANGCHAIN --
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local(INDEX_DIR)
    print(f"✅ Indexed {len(docs)} chunks from {len(data)} web pages. Index saved to {INDEX_DIR} (index.faiss, index.pkl)")

if __name__ == "__main__":
    build_index() 