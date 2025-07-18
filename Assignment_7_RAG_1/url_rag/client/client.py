# Example of how to use the decision making and action layers with perception and memory
import sys
import os
import asyncio
import uuid

# Add the parent directory (eag_agentic_rag) to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.append(project_root)

# Import core dependencies
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

# Fix for Windows asyncio subprocess
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Import our modules with simple error handling
try:
    # Import LLM provider first to ensure SSL patching happens before any other imports
    from url_rag.client.llm_provider import default_llm
    from url_rag.client.decision import get_llm_decision
    from url_rag.client.action import execute_actions, print_message_chain
    from url_rag.client.memory import ConversationMemory

    # Import utility functions
    from url_rag.client.utils import (
        read_yaml_file,
        log,
        filter_chat_history,
        save_conversation,
        display_conversation_history,
        print_conversation_summary,
        save_session_summary,
    )

    # Only try to import embedding provider if LLM imports succeeded
    try:
        from url_rag.client.embedding_provider import OpenAIEmbeddingProvider

        embedder = OpenAIEmbeddingProvider().embeddings
    except ImportError as e:
        log(f"Embedding provider not available: {e}")
        embedder = None
except ImportError as e:
    print(f"Critical import error: {e}")
    print("Application cannot run without core modules")
    sys.exit(1)

# Get the default LLM
llm = default_llm.chat_model

# Create output directory for conversation logs
OUTPUT_DIR = os.path.join(os.getcwd(), "url_rag", "conversation_logs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# Load config with smart defaults
def load_config():
    config = {}
    try:
        config = read_yaml_file("url_rag/utility/config.yaml")
        if config:
            log(f"Config loaded: {config}")
        else:
            log("Empty config file, using defaults")
    except Exception as e:
        log(f"Error reading config: {e}")

    # Set up defaults for required values
    if "history_index_name" not in config:
        config["history_index_name"] = "history_index"
        log(f"Using default history index name: {config['history_index_name']}")

    # Convert relative paths to absolute if needed
    if "history_index_name" in config:
        if not os.path.isabs(config["history_index_name"]):
            config["history_index_name"] = os.path.join(
                os.getcwd(), "url_rag", config["history_index_name"]
            )

    return config


# Load config once at startup
config = load_config()
print(f"Config: {config}")

# Initialize memory store if embeddings are available
memory_store = None
if embedder:
    try:
        reset_index = config.get("reset_index", False)
        memory_store = ConversationMemory(
            embedder, index_folder=config["history_index_name"], reset_index=reset_index
        )
        log(f"Memory store initialized with index: {config['history_index_name']}")
    except Exception as e:
        log(f"Error initializing memory store: {e}")
else:
    log("No embeddings available, memory store not initialized")

# Find server path - try only the most likely location
server_path = os.path.join(os.getcwd(), "url_rag", "server", "server.py")
if not os.path.exists(server_path):
    # Try relative path as fallback
    server_path = "url_rag/server/server.py"
log(f"Using server path: {server_path}")

# Set up server parameters
server_params = StdioServerParameters(
    command=sys.executable,
    args=[server_path],
    cwd=os.getcwd(),
)


def convert_messages_to_memory_format(messages):
    """Convert LangChain message objects to the format expected by ConversationMemory"""
    memory_messages = []
    for msg in messages:
        if hasattr(msg, "content"):
            if isinstance(msg, HumanMessage):
                memory_messages.append({"sender": "human", "content": msg.content})
            elif isinstance(msg, AIMessage):
                memory_messages.append({"sender": "ai", "content": msg.content})
            else:
                # Default to tool for other message types
                memory_messages.append({"sender": "tool", "content": msg.content})
    return memory_messages


async def process_step(step_name, outputs, func, *args, **kwargs):
    """Process a step with consistent tracking and error handling"""
    outputs["steps"].append({"name": step_name, "status": "started"})
    log(f"Starting: {step_name}")

    try:
        result = await func(*args, **kwargs)
        outputs["steps"][-1]["status"] = "completed"
        return result
    except Exception as e:
        outputs["steps"][-1]["status"] = "failed"
        outputs["steps"][-1]["error"] = str(e)
        log(f"Error in {step_name}: {e}")
        raise


async def main(query: str, conversation_id=None, chat_history=None):
    """Main function that coordinates the decision making and action layers for a single query."""
    # Generate a conversation ID if none provided
    if conversation_id is None:
        conversation_id = uuid.uuid4().hex

    # Use provided chat history or initialize empty list
    if chat_history is None:
        chat_history = []

        # If memory store is available, get conversation history
        if memory_store:
            log(f"Retrieving conversation history for ID: {conversation_id}")
            chat_history = memory_store.get_conversation_as_lc_messages(conversation_id)
            if chat_history:
                log(f"Found {len(chat_history)} messages in conversation history")

                # Filter chat history to only include human and AI messages
                filtered_chat_history = filter_chat_history(chat_history)
                log(f"Filtered to {len(filtered_chat_history)} human/AI messages")
                chat_history = filtered_chat_history
            else:
                log("No previous history found")

    # Log the start of processing
    log(f"Processing query: {query}")

    # Dictionary to track step outputs for logging
    step_outputs = {
        "query": query,
        "conversation_id": conversation_id,
        "steps": [],
    }

    try:
        # Connect to the MCP server
        async with stdio_client(server_params) as (read, write):
            log("Connection established")

            async with ClientSession(read, write) as session:
                await session.initialize()
                log("Session initialized")

                # Load tools
                tools = await process_step(
                    "Loading tools", step_outputs, load_mcp_tools, session
                )
                step_outputs["steps"][-1]["tools_count"] = len(tools)
                log(f"Loaded {len(tools)} tools")

                # Get LLM decision
                try:
                    response, messages = await process_step(
                        "Getting LLM decision",
                        step_outputs,
                        get_llm_decision,
                        session=session,
                        query=query,
                        tools=tools,
                        llm=llm,
                        chat_history=chat_history,
                    )
                except Exception as e:
                    # Handle error in LLM decision and return early
                    error_msg = AIMessage(
                        content=f"I'm sorry, but I encountered an error processing your request: {str(e)}"
                    )
                    return (
                        f"Error: {str(e)}",
                        [HumanMessage(content=query), error_msg],
                        step_outputs,
                    )

                # Execute tool calls if present
                has_tool_calls = hasattr(response, "tool_calls") and response.tool_calls
                step_name = (
                    "Executing tool calls" if has_tool_calls else "Processing response"
                )

                response, messages = await process_step(
                    step_name,
                    step_outputs,
                    execute_actions,
                    response=response,
                    messages=messages,
                    tools=tools,
                )

                if has_tool_calls:
                    step_outputs["steps"][-1]["tools_used"] = [
                        tc["name"] for tc in response.tool_calls
                    ]

                # Print the final message chain
                log("Conversation results:")
                print_message_chain(messages)

                # Save conversation
                save_conversation(conversation_id, query, messages, OUTPUT_DIR)
                step_outputs["steps"].append(
                    {"name": "Saving conversation", "status": "completed"}
                )

                # Store in memory if available
                if memory_store:
                    memory_messages = convert_messages_to_memory_format(messages)
                    if memory_messages:
                        log(f"Storing {len(memory_messages)} messages in memory")
                        memory_store.store_conversation(
                            conversation_id, memory_messages
                        )
                        step_outputs["steps"].append(
                            {
                                "name": "Storing in memory",
                                "status": "completed",
                                "message_count": len(memory_messages),
                            }
                        )

                return response, messages, step_outputs

    except Exception as e:
        # Handle any uncaught exceptions
        log(f"Error occurred in main: {e}")
        import traceback

        traceback.print_exc()

        # Create error message
        error_msg = AIMessage(
            content=f"I'm sorry, but I encountered an error processing your request: {str(e)}"
        )

        return error_msg, [HumanMessage(content=query), error_msg], step_outputs


async def run_conversation():
    """Run a conversation with multiple queries."""
    # Generate a unique conversation ID for this session
    conversation_id = uuid.uuid4().hex
    log(f"Starting conversation with ID: {conversation_id}")

    # Get user input for queries
    print("\nEnter your questions (one per line, press Enter twice to finish):")
    user_queries = []
    while True:
        query = input()
        if not query:
            if user_queries:  # If we have at least one query already
                break
            else:
                print("Please enter at least one question:")
                continue
        user_queries.append(query)

    # Use user-provided queries or fallback to examples if none provided
    queries = (
        user_queries
        if user_queries
        else [
            "What is the use of docker?",
            "What are the benefits of the same?",
        ]
    )

    log(f"Processing {len(queries)} queries")

    # Process each query in sequence
    results = []
    chat_history = []  # Initialize empty chat history

    for i, query in enumerate(queries, 1):
        print("\n" + "=" * 50)
        print(f"QUERY {i}/{len(queries)}: {query}")
        print("=" * 50 + "\n")

        # Run the main function with the current query and accumulated chat history
        response, messages, step_outputs = await main(
            query, conversation_id, chat_history
        )

        # Update chat history for next query
        chat_history = []  # Reset and get fresh from memory
        if memory_store:
            chat_history = memory_store.get_conversation_as_lc_messages(conversation_id)

        # Save results for summary
        results.append(
            {
                "conversation_id": conversation_id,
                "query": query,
                "response": response,
                "messages": messages,
                "step_outputs": step_outputs,
            }
        )

        # Print conversation summary
        print_conversation_summary(
            conversation_id, query, response, messages, step_outputs
        )
        print("\n" + "-" * 50 + "\n")

    log(f"Conversation session complete. Processed {len(queries)} queries.")

    # Save session summary
    save_session_summary(conversation_id, queries, results, OUTPUT_DIR)

    # Display full conversation history at the end
    if memory_store:
        print("\nFull conversation history from memory store:")
        display_conversation_history(conversation_id, memory_store)

    return results


if __name__ == "__main__":
    try:
        asyncio.run(run_conversation())
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
        print("This is likely due to Windows asyncio subprocess issues.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()