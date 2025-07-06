import os
import sys
import json
import asyncio
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack

print(f"Current working directory: {os.getcwd()}")


class MCPEmbeddingClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.tools = []

    async def connect_to_server(self, server_script_path: str):
        """Start an MCP server (subprocess) and connect."""
        print(f"Starting Embedding server from: {server_script_path}")

        if server_script_path.endswith(".py"):
            command = "python"
        else:
            raise ValueError("Server script must be .py")

        # Start the server process and connect to it via stdio
        server_params = StdioServerParameters(
            # command=command,
            command=sys.executable,
            args=[server_script_path],
            cwd=os.getcwd(),
        )
        # stdio_transport is a context manager that returns a tuple of (stdio, write)
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        # Initialize the session
        await self.session.initialize()

        # Get list of tools
        tool_list = await self.session.list_tools()
        self.tools = tool_list.tools
        print(
            f"Connected to Embedding server. Available tools: {[t.name for t in tool_list.tools]}"
        )
        return tool_list.tools

    async def inspect_tools(self):
        """Inspect the tools available from the server"""
        if not self.tools:
            print("No tools available. Did you connect to the server?")
            return

        for tool in self.tools:
            print("\n" + "=" * 50)
            print(f"Tool Name: {tool.name}")
            print(f"Description: {tool.description}")
            print("\nInput Schema:")
            print(json.dumps(tool.inputSchema, indent=2))

            # Check if outputSchema exists before trying to access it
            if hasattr(tool, "outputSchema") and tool.outputSchema:
                print("\nOutput Schema:")
                print(json.dumps(tool.outputSchema, indent=2))
            else:
                print("\nOutput Schema: Not available")

    async def test_calculate_embedding_sum(self, text: str):
        """Test the calculate_embedding_sum tool"""
        if not self.session:
            raise RuntimeError("No MCP session found. Did you call connect_to_server?")

        print(f"\nTesting calculate_embedding_sum with text='{text}'")
        tool_args = {"input_data": {"text": text}}

        try:
            result = await self.session.call_tool("calculate_embedding_sum", tool_args)
            print(f"Result: {result.content}")
            return result.content
        except Exception as e:
            print(f"Error calling calculate_embedding_sum: {e}")
            import traceback

            traceback.print_exc()
            return None

    async def test_retrieve_documents(self, query: str, k: int = 3):
        """Test the retrieve_documents tool"""
        if not self.session:
            raise RuntimeError("No MCP session found. Did you call connect_to_server?")

        print(f"\nTesting retrieve_documents with query='{query}', k={k}")
        tool_args = {"input_data": {"query": query, "k": k}}

        try:
            result = await self.session.call_tool("retrieve_documents", tool_args)
            print(f"Result: {result.content}")
            # Parse the JSON result for a cleaner display
            try:
                # Fix: Access the first element if content is a list
                content = (
                    result.content[0].text
                    if isinstance(result.content, list)
                    else result.content
                )
                json_result = json.loads(content)
                print("\nRetrieved documents:")
                print(f"Found {json_result['count']} document(s)")
                urls = json_result["urls"]
                contents = json_result["contents"]
                for i in range(len(urls)):
                    print(f"\nDocument {i+1}:")
                    print(f"URL: {urls[i]}")
                    print(f"Content preview: {contents[i][:100]}...")
            except (json.JSONDecodeError, TypeError, IndexError, KeyError) as e:
                # If JSON parsing fails, just use the raw content
                print(f"Error parsing JSON response: {e}")
            return result.content
        except Exception as e:
            print(f"Error calling retrieve_documents: {e}")
            import traceback

            traceback.print_exc()
            return None

    async def run_all_tests(self):
        """Run all tests"""

        # Test embedding sum calculation
        await self.test_calculate_embedding_sum(
            "This is a test for embedding vector sum calculation"
        )

        # Test document retrieval (if the index exists)
        try:
            await self.test_retrieve_documents("What is Helm?", 2)
        except Exception as e:
            print(f"Skipping document retrieval test: {e}")

    async def interactive_mode(self):
        """Run an interactive session"""
        print("\nInteractive Mode")
        print(
            "Available operations: embedding, retrieve, quit"
        )

        while True:
            try:
                operation = input("\nEnter operation: ").strip().lower()

                if operation == "quit":
                    break

                if operation == "embedding":
                    text = input("Enter text for embedding: ")
                    await self.test_calculate_embedding_sum(text)

                elif operation == "retrieve":
                    query = input("Enter search query: ")
                    k = int(input("Enter number of documents to retrieve: "))
                    await self.test_retrieve_documents(query, k)

                else:
                    print(f"Unknown operation: {operation}")
                    print(
                        "Available operations: add, subtract, multiply, divide, eval, "
                        "percentage, sqrt, embedding, retrieve, quit"
                    )

            except ValueError as e:
                print(f"Invalid input: {e}")
            except Exception as e:
                print(f"Error: {e}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    """Main function to run the client"""
    # Get the path to the server script
    server_script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../server/test_server.py")
    )

    if not os.path.exists(server_script_path):
        print(f"Error: Server script not found at {server_script_path}")
        sys.exit(1)

    print(f"Server script path: {server_script_path}")

    client = MCPEmbeddingClient()
    try:
        # Connect to the server
        print("\nConnecting to MCP server...")
        await client.connect_to_server(server_script_path)

        # Inspect available tools
        print("\nInspecting available tools:")
        await client.inspect_tools()

        # Choose testing mode
        mode = input("\nChoose mode (1: Run all tests, 2: Interactive mode): ")

        if mode == "1":
            # Run all tests
            await client.run_all_tests()
        else:
            # Run interactive mode
            await client.interactive_mode()

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Clean up
        print("\nCleaning up...")
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
