"""
- This script builds a FAISS index from scraped web content using Ollama's nomic-embed-text embeddings.
- Steps performed:
    - Loads scraped_contents.json (list of {link, content} dicts).
    - Chunks each content into overlapping segments.
    - Gets embeddings for each chunk using Ollama's local API.
    - Stores chunk metadata (URL, chunk text, chunk id).
    - Creates a FAISS index and adds all chunk embeddings.
    - Saves the index and metadata for later retrieval.
- Useful for semantic search over web browsing content with chunk-level granularity.
"""

import os
import faiss
import numpy as np
import requests
import json
import time

# -- CONFIG --
CHUNK_SIZE = 40
CHUNK_OVERLAP = 10
INPUT_JSON = os.path.join("data", "scraped_contents.json")
INDEX_PATH = os.path.join("data", "faiss_web_index.bin")
META_PATH = os.path.join("data", "faiss_web_metadata.json")

# -- HELPERS --
def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunk = " ".join(words[i:i+size])
        if chunk:
            chunks.append(chunk)
    return chunks

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

def build_index():
    """
    Build FAISS index from scraped content.
    """
    all_chunks = []
    metadata = []

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    for entry_idx, entry in enumerate(data[:30]):
        url = entry["link"]
        content = entry["content"]
        chunks = chunk_text(content)
        for idx, chunk in enumerate(chunks):
            try:
                emb = get_embedding(chunk)
                all_chunks.append(emb)
                metadata.append({
                    "url": url,
                    "chunk": chunk,
                    "chunk_id": f"entry{entry_idx}_chunk{idx}"
                })
            except Exception as e:
                print(f"Error embedding chunk from {url}: {e}")
        print(f"Processed {len(chunks)} chunks from {url}")
        time.sleep(0.5)  # Small delay to avoid overwhelming Ollama

    # -- CREATE FAISS INDEX --
    if not all_chunks:
        raise ValueError("No chunks to index!")
    dimension = len(all_chunks[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.stack(all_chunks))

    # -- SAVE INDEX & METADATA --
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Indexed {len(all_chunks)} chunks from {len(data)} web pages. Index saved to {INDEX_PATH}, metadata to {META_PATH}.")

if __name__ == "__main__":
    build_index() 