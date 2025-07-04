"""
- This script generates an embedding vector for a given sentence using the Ollama API with the 'nomic-embed-text' model.
- It performs the following steps:
    - Defines a sample sentence to embed.
    - Sends a POST request to the local Ollama server to obtain the embedding.
    - Converts the received embedding to a NumPy array.
    - Prints the length and first five values of the resulting embedding vector.
- Useful for testing and demonstrating how to obtain text embeddings from a locally running Ollama model.
"""

import numpy as np
import requests
import json

# Example sentence to embed
sentence = "How does AlphaFold work?"

# Get embedding from Ollama
response = requests.post(
    "http://localhost:11434/api/embeddings",
    json={
        "model": "nomic-embed-text",
        "prompt": sentence
    }
)
response.raise_for_status()

# Convert to numpy array
embedding_vector = np.array(response.json()["embedding"], dtype=np.float32)

print(f"🔢 Vector length: {len(embedding_vector)}")  # Should be 768 for nomic-embed-text
print(f"📈 First 5 values: {embedding_vector[:5]}")
