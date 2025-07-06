import os
import sys
import ssl
import numpy as np
import json

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Disable SSL verification for testing
if hasattr(ssl, "_create_unverified_context"):
    ssl._create_default_https_context = ssl._create_unverified_context

# Import MCP server
from mcp.server.fastmcp import FastMCP
from loguru import logger
from embedding_provider import OpenAIEmbeddingProvider
from tools import get_retrieved_docs
from models import (
    CalculateEmbeddingSumInput,
    CalculateEmbeddingSumOutput,
    RetrieveDocumentsInput,
    RetrieveDocumentsOutput,
    Document,
)

# Initialize embedding provider
embedding_provider = OpenAIEmbeddingProvider()

# Create the MCP server with the name "Embedding"
mcp = FastMCP("Embedding")

@mcp.tool()
def calculate_embedding_sum(
    input_data: CalculateEmbeddingSumInput,
) -> CalculateEmbeddingSumOutput:
    """Calculate the sum of all values in the embedding vector for the given text.

    Args:
        input_data: The CalculateEmbeddingSumInput model containing the text

    Returns:
        The CalculateEmbeddingSumOutput model containing the result
    """
    try:
        # Generate embedding for the text
        embedding = embedding_provider.embeddings.embed_query(input_data.text)
        # Calculate and return the sum of the embedding vector
        result = float(np.sum(embedding))
        return CalculateEmbeddingSumOutput(result=result)
    except Exception as e:
        raise ValueError(f"Error calculating embedding sum: {e}")


@mcp.tool()
def retrieve_documents(input_data: RetrieveDocumentsInput) -> str:
    """Retrieve documents from the vector store based on the query.

    Args:
        input_data: The RetrieveDocumentsInput model containing the query and k value

    Returns:
        A JSON string containing the retrieved web URLs and page content
    """
    try:
        # Get the retrieved documents using the function from tools.py
        web_urls, page_contents = get_retrieved_docs(input_data.query, input_data.k)

        # Create a list of Document objects
        documents = [
            Document(url=url, content=content)
            for url, content in zip(web_urls, page_contents)
        ]

        # Convert to dictionary first for simple JSON serialization
        response = {
            "urls": web_urls,
            "contents": page_contents,
            "count": len(documents),
        }

        # Return the response as a JSON string
        return json.dumps(response, indent=2)
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}")
        raise ValueError(f"Error retrieving documents: {e}")


def mcp_log(level: str, message: str) -> None:
    """Log a message to stderr to avoid interfering with JSON communication"""
    sys.stderr.write(f"{level}: {message}\n")
    sys.stderr.flush()


if __name__ == "__main__":
    logger.info(f"Starting MCP Calculator server in directory: {os.getcwd()}")
    mcp.run(transport="stdio")
