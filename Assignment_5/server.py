from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import sys
import logging
from dotenv import load_dotenv
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

load_dotenv()

def format_tool_output(output):
    """Format the tool output to make it more readable"""
    formatted_output = []
    
    # Split the output into lines
    lines = output.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for FUNCTION_CALL
        if line.startswith('FUNCTION_CALL:'):
            current_tool = line.replace('FUNCTION_CALL:', '').strip()
            formatted_output.append(f"\n🔧 Tool Called: {current_tool}")
        
        # Check for REASONING
        elif line.startswith('REASONING'):
            current_reasoning = line.replace('REASONING:', '').strip()
            formatted_output.append(f"📝 Reasoning: {current_reasoning}")
        
        # Check for tool results
        elif 'Function result:' in line:
            result = line.split('Function result:')[1].strip()
            formatted_output.append(f"✅ Result: {result}")
        
        # Check for errors
        elif 'Error in tool execution:' in line:
            error = line.split('Error in tool execution:')[1].strip()
            formatted_output.append(f"❌ Error: {error}")
        
        # Include all print statements and log messages
        elif line.startswith('Starting') or line.startswith('Session') or line.startswith('Retrieved') or line.startswith('Tool added'):
            formatted_output.append(f"📜 {line}")
        
        # Include any other relevant output
        elif '[' in line and ']' in line:  # Likely a log message
            formatted_output.append(f"📜 {line}")
    
    return '\n'.join(formatted_output)

@app.route('/')
def index():
    return jsonify({
        'status': 'running',
        'message': 'Math GUI Agent Server is running',
        'endpoints': {
            '/process': 'POST - Process mathematical and GUI operations'
        }
    })

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_query():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({'error': 'No JSON data received'}), 400

        query = data.get('query')
        if not query:
            logger.error("No query provided in request")
            return jsonify({'error': 'No query provided'}), 400

        logger.info(f"Received query: {query}")

        # Create a temporary file with the query
        try:
            with open('temp_query.txt', 'w') as f:
                f.write(query)
            logger.info("Successfully wrote query to temp_query.txt")
        except Exception as e:
            logger.error(f"Error writing to temp_query.txt: {str(e)}")
            return jsonify({'error': f'Error writing query file: {str(e)}'}), 500

        # Run the Python script with the query
        try:
            logger.info("Starting talk2mcp-2-UPDATED.py")
            result = subprocess.run(
                [sys.executable, 'talk2mcp-2-UPDATED.py'],
                capture_output=True,
                text=True
            )
            logger.info(f"Script execution completed with return code: {result.returncode}")
            
            # Combine stdout and stderr
            full_output = result.stdout + "\n" + result.stderr
            
            if result.returncode != 0:
                error_msg = f"Script failed with error: {result.stderr}"
                logger.error(error_msg)
                return jsonify({'error': error_msg}), 500

            # Format the output
            formatted_output = format_tool_output(full_output)
            
            # Add a summary of the execution
            summary = f"""
📋 Execution Summary:
-------------------
Query: {query}
Status: {'Success' if result.returncode == 0 else 'Failed'}
Return Code: {result.returncode}

📜 Log Output:
-------------------
{formatted_output}
"""
            
            response = jsonify({'result': summary})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

        except Exception as e:
            logger.error(f"Error executing script: {str(e)}")
            return jsonify({'error': f'Error executing script: {str(e)}'}), 500

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    try:
        logger.info("Starting Flask server...")
        # Check if all required files exist
        required_files = ['talk2mcp-2-UPDATED.py', 'example2-3.py', '.env']
        missing_files = [f for f in required_files if not os.path.exists(f)]
        if missing_files:
            raise FileNotFoundError(f"Missing required files: {', '.join(missing_files)}")
        
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start Flask server: {str(e)}")
        sys.exit(1) 