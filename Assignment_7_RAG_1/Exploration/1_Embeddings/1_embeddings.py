"""
- This script generates an embedding vector for a given sentence using the Google Gemini API.
- It performs the following steps:
    - Loads the API key from an environment variable.
    - Sends a sample sentence for embedding using the Gemini API.
    - Prints the length and first five values of the resulting embedding vector.
- The 'task_type' parameter in EmbedContentConfig is important:
    - Here, 'RETRIEVAL_DOCUMENT' is used because it is relevant for Retrieval-Augmented Generation (RAG) tasks.
    - Other possible values for 'task_type' (as per Gemini API documentation) include:
        - RETRIEVAL_DOCUMENT: For document retrieval (RAG)
        - RETRIEVAL_QUERY: For query embedding (search queries)
        - SEMANTIC_SIMILARITY: For general semantic similarity tasks
        - CLASSIFICATION: For classification tasks
        - CLUSTERING: For clustering tasks
"""
from google import genai
from google.genai import types
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

sentence = "How does AlphaFold work?"

response = client.models.embed_content(
    model="gemini-embedding-exp-03-07",
    contents=sentence,
    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
)

embedding_vector = np.array(response.embeddings[0].values, dtype=np.float32)

print(f"🔢 Vector length: {len(embedding_vector)}")
print(f"📈 First 5 values: {embedding_vector[:5]}")
