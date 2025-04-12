import os
import logging
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
from google import genai
from concurrent.futures import TimeoutError
from functools import partial

# Setup logging
logging.basicConfig(
    filename="mcp_llm_session.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("SessionLogger")

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

max_iterations = 6
last_response = None
iteration = 0
iteration_response = []

async def generate_with_timeout(client, prompt, timeout=10):
    print("Starting LLM generation...")
    logger.info("Starting LLM generation...")
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        print("LLM generation completed")
        logger.info("LLM generation completed")
        return response
    except TimeoutError:
        print("LLM generation timed out!")
        logger.error("LLM generation timed out!")
        raise
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        logger.error(f"Error in LLM generation: {e}")
        raise

def reset_state():
    global last_response, iteration, iteration_response
    last_response = None
    iteration = 0
    iteration_response = []
    print("State reset")
    logger.info("State reset")

async def main():
    reset_state()
    print("Starting main execution...")
    logger.info("Starting main execution...")
    try:
        server_params = StdioServerParameters(
            command="python",
            args=["example2-3.py"]
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("Session created, initializing...")
                logger.info("Session created, initializing...")
                await session.initialize()
                print("Initialized session")
                logger.info("Initialized session")
                tools_result = await session.list_tools()
                tools = tools_result.tools
                print(f"Retrieved {len(tools)} tools")
                logger.info(f"Retrieved {len(tools)} tools")

                tools_description = []
                for i, tool in enumerate(tools):
                    try:
                        params = tool.inputSchema
                        desc = getattr(tool, 'description', 'No description available')
                        name = getattr(tool, 'name', f'tool_{i}')

                        if 'properties' in params:
                            param_details = [
                                f"{param_name}: {param_info.get('type', 'unknown')}"
                                for param_name, param_info in params['properties'].items()
                            ]
                            params_str = ', '.join(param_details)
                        else:
                            params_str = 'no parameters'

                        tools_description.append(f"{i+1}. {name}({params_str}) - {desc}")
                        print(f"Tool added: {name}")
                        logger.info(f"Tool added: {name}")
                    except Exception as e:
                        tools_description.append(f"{i+1}. Error processing tool")
                        print(f"Error processing tool {i}: {e}")
                        logger.error(f"Error processing tool {i}: {e}")

                tools_description = "\n".join(tools_description)
                system_prompt = f"""You are a math and paint agent solving problems in iterations. You have access to mathematical, GUI drawing tools and an email tool.

Available tools:
{tools_description}

You must respond with EXACTLY ONE line in one of these formats (no additional text):
1. For function calls:
   FUNCTION_CALL: function_name|param1|param2|...
2. For final answers:
   FINAL_ANSWER: [number]

Important:
- When a function returns multiple values, you need to process all of them
- Only give FINAL_ANSWER when you have completed all necessary calculations
- Do not repeat function calls with the same parameters
- You can open Paint using open_paint, draw on it using draw_rectangle, and add text using add_text_in_paint
- Send all logs generated to the email mentioned in query.
Examples:
- FUNCTION_CALL: strings_to_chars_to_int|INDIA
- FUNCTION_CALL: draw_rectangle|780|380|1140|700
- FUNCTION_CALL: send_email_log|bhattacharjeeajay16@gmail.com|'assignment-4 logs in email', path of log file)
- FINAL_ANSWER: [42]

DO NOT include any explanations or additional text."""

                query = """Find the ASCII values of characters in INDIA and then return sum of exponentials of 
                those values. Then open paint and create a rectangle at coordinates (780, 380) to (1140, 700) 
                inside which write the result obtained. All the logs which are generated is saved in a log file named 'mcp_llm_session.log'. 
                Send 'mcp_llm_session.log' to the email bhattacharjeeajay16@gmail.com and give subject as 'assignment-4 logs 
                in email' """

                global iteration, last_response

                while iteration < max_iterations:
                    print(f"\n--- Iteration {iteration + 1} ---")
                    logger.info(f"--- Iteration {iteration + 1} ---")
                    if last_response is None:
                        current_query = query
                    else:
                        current_query = current_query + "\n\n" + " ".join(iteration_response) + "  What should I do next?"

                    prompt = f"{system_prompt}\n\nQuery: {current_query}"
                    try:
                        print("Generating response from model...")
                        logger.info("Generating response from model...")
                        response = await generate_with_timeout(client, prompt)
                        response_text = response.text.strip()
                        print(f"Model response: {response_text}")
                        logger.info(f"Model response: {response_text}")
                        for line in response_text.split('\n'):
                            if line.startswith("FUNCTION_CALL:"):
                                response_text = line
                                break
                    except Exception as e:
                        print(f"Failed to get LLM response: {e}")
                        logger.error(f"Failed to get LLM response: {e}")
                        break

                    if response_text.startswith("FUNCTION_CALL:"):
                        _, function_info = response_text.split(":", 1)
                        parts = [p.strip() for p in function_info.split("|")]
                        func_name, params = parts[0], parts[1:]
                        print(f"Calling function: {func_name} with parameters {params}")
                        logger.info(f"Calling function: {func_name} with parameters {params}")

                        try:
                            tool = next((t for t in tools if t.name == func_name), None)
                            if not tool:
                                raise ValueError(f"Unknown tool: {func_name}")

                            arguments = {}
                            schema_properties = tool.inputSchema.get('properties', {})

                            for param_name, param_info in schema_properties.items():
                                if not params:
                                    raise ValueError(f"Not enough parameters provided for {func_name}")

                                value = params.pop(0)
                                param_type = param_info.get('type', 'string')

                                if param_type == 'integer':
                                    arguments[param_name] = int(value)
                                elif param_type == 'number':
                                    arguments[param_name] = float(value)
                                elif param_type == 'array':
                                    if isinstance(value, str):
                                        value = value.strip('[]').split(',')
                                    arguments[param_name] = [int(x.strip()) for x in value]
                                else:
                                    arguments[param_name] = str(value)

                            print(f"Calling tool with arguments: {arguments}")
                            logger.info(f"Calling tool with arguments: {arguments}")
                            result = await session.call_tool(func_name, arguments=arguments)

                            if hasattr(result, 'content'):
                                if isinstance(result.content, list):
                                    iteration_result = [
                                        item.text if hasattr(item, 'text') else str(item)
                                        for item in result.content
                                    ]
                                else:
                                    iteration_result = str(result.content)
                            else:
                                iteration_result = str(result)

                            if isinstance(iteration_result, list):
                                result_str = f"[{', '.join(iteration_result)}]"
                            else:
                                result_str = str(iteration_result)
                            
                            print(f"Function result: {result_str}")
                            logger.info(f"Function result: {result_str}")
                            iteration_response.append(
                                f"In the {iteration + 1} iteration you called {func_name} with {arguments} parameters, "
                                f"and the function returned {result_str}."
                            )
                            last_response = iteration_result

                        except Exception as e:
                            import traceback
                            print(f"Error in tool execution: {e}")
                            logger.error(f"Error in tool execution: {e}")
                            iteration_response.append(f"Error in iteration {iteration + 1}: {str(e)}")
                            break

                    iteration += 1

    except Exception as e:
        import traceback
        print(f"Unhandled exception in main: {e}")
        logger.error(f"Unhandled exception in main: {e}")
    finally:
        reset_state()
        print("Session ended. State reset.")
        logger.info("Session ended. State reset.")

if __name__ == "__main__":
    asyncio.run(main())
