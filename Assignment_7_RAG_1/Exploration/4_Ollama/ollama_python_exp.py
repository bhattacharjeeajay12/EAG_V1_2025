from ollama import chat
from ollama import ChatResponse
from ollama import Client
import asyncio
from ollama import AsyncClient

"""
This script demonstrates multiple ways to interact with Ollama language models using the Python client library:

- Shows how to use the synchronous `chat` function to get a response from a local Ollama model.
- Demonstrates streaming responses from the model for real-time output.
- Illustrates how to use a custom `Client` instance with custom headers and host configuration.
- Provides an example of using the asynchronous `AsyncClient` for non-blocking chat calls.

Prerequisites:
- The Ollama Python package must be installed (`pip install ollama`).
- The Ollama CLI must be installed, running, and the desired model (e.g., `smollm2:135m`) must be pulled locally.
- Useful for testing, experimenting, and understanding different interaction patterns with Ollama models in Python.

Tips:
- You can find a list of available models at https://ollama.com/models.
- You can also use the `ollama list` command to see a list of all models you have downloaded.
- chat function is a wrapper around the Ollama CLI chat command to interact with models.
- we are using the chat function to get a response from a model.
- The chat function takes a model name and a list of messages as input.
- The messages are a list of dictionaries, where each dictionary has a role (user or assistant) and content (the message text).
"""

# Example 1: Synchronous chat using the chat function
# - The chat function takes a model name and a list of messages as input.
response: ChatResponse = chat(
    model="smollm2:135m",
    messages=[
        {
            "role": "user",
            "content": "Why is the sky blue?",
        },
    ],
)
print("Response:")
print(response["message"]["content"])
# or access fields directly from the response object
print(response.message.content)

# Example 2: Streaming chat using the chat function with stream=True
stream = chat(
    model="smollm2:135m",
    messages=[{"role": "user", "content": "Why is the sky blue?"}],
    stream=True,
)
print("\n\n")
print("Streaming response:")
for chunk in stream:
    print(chunk["message"]["content"], end="", flush=True)


client = Client(host="http://localhost:11434", headers={"x-some-header": "some-value"})
response = client.chat(
    model="smollm2:135m",
    messages=[
        {
            "role": "user",
            "content": "Why is the sky blue?",
        },
    ],
)
print("\n\n")
print("Custom Client Response:")
print(response["message"]["content"])

# Example 4: Asynchronous chat using AsyncClient


async def chat():
    message = {"role": "user", "content": "Why is the sky blue?"}
    response = await AsyncClient().chat(model="smollm2:135m", messages=[message])
    return response


print("\n\n")
print("Async Client Response:")
response = asyncio.run(chat())
print(response["message"]["content"])

