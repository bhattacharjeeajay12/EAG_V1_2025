"""
MarkItDown is a lightweight Python utility for converting various files to Markdown for use with LLMs and related text analysis pipelines
We will implement it in a basic way and also with openai
"""

from markitdown import MarkItDown
from dotenv import load_dotenv
from pathlib import Path
import os
from openai import OpenAI
load_dotenv()

pth = Path("../documents", "BestRagTech.pdf")
# pth = Path("../documents", "SAMPLE-Indian-Policies-and-Procedures-January-2023.docx")


# first way - basic extraction
md = MarkItDown(enable_plugins=False)  # Set to True to enable plugins
# chk = os.path.exists(pth)
result = md.convert(
    pth
)
print(result.text_content)
print("done")


# second way -  openai extraction
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_base = os.getenv("OPENAI_API_BASE")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

client = OpenAI(api_key=openai_api_key)
md = MarkItDown(llm_client=client, llm_model="gpt-4o")

pth = Path("../documents", "BestRagTech.pdf")
result = md.convert(
    pth
)
print(result.text_content)
