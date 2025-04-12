// Import the required functions from tools.js
import { count_vowels, compute_factorial, get_today_day, get_current_hour, 
         compute_a_squared_minus_b_cubed, split_number_into_digits, 
         square_numbers_in_list, sum_numbers_in_list, convert_string_to_ascii, 
         multiply_list_elements, compute_log2 } from './tools.js';

const API_KEY = "AIzaSyBY02JEi8Gnbu_ark0akR4dub7GkArx9fI";
const API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent";

// Parse input function
function parse_input(text) {
    text = text.trim();
    
    try {
        const parsed = JSON.parse(text);
        if (Array.isArray(parsed)) return parsed;
        if (typeof parsed === 'number') return parsed;
        if (Array.isArray(parsed)) return parsed;
    } catch {
        // Continue if parsing fails
    }

    if (text.includes(',')) {
        return text.split(',').map(part => part.trim());
    }
    
    if (/^\d+$/.test(text)) return parseInt(text);
    
    return text;
}

// Function caller
function function_caller(func_name, params) {
    const function_map = {
        count_vowels,
        compute_factorial,
        get_today_day,
        get_current_hour,
        compute_a_squared_minus_b_cubed,
        split_number_into_digits,
        square_numbers_in_list,
        sum_numbers_in_list,
        convert_string_to_ascii,
        multiply_list_elements,
        compute_log2
    };

    if (func_name in function_map) {
        if (params === '') return function_map[func_name]();
        
        // Special handling for list-related functions
        if (['square_numbers_in_list', 'sum_numbers_in_list', 'multiply_list_elements'].includes(func_name)) {
            try {
                // If params is already an array, use it directly
                if (Array.isArray(params)) {
                    return function_map[func_name](params);
                }
                
                // Try to parse as JSON array first
                if (params.startsWith('[') && params.endsWith(']')) {
                    params = JSON.parse(params);
                } else {
                    // If not JSON, try to split by comma and convert to numbers
                    params = params.split(',').map(x => {
                        const num = parseFloat(x.trim());
                        return isNaN(num) ? x.trim() : num;
                    });
                }
                return function_map[func_name](params);
            } catch (e) {
                console.error('Error parsing params:', e);
                return `Error: Could not parse input as array`;
            }
        }
        
        // For other functions, use parse_input
        else {
            params = parse_input(params);
            if (Array.isArray(params)) {
                return function_map[func_name](...params);
            }
            return function_map[func_name](params);
        }
    }
    return `Function ${func_name} not found`;
}

// Function to call Gemini API
async function callGeminiAPI(prompt) {
    const system_prompt = `You are a math agent solving problems in iterations. Respond with EXACTLY ONE of these formats:
1. FUNCTION_CALL: python_function_name|input
2. FINAL_ANSWER: [number]

where python_function_name is one of the following:
1. count_vowels(string) It takes a string as an input and count the number of vowels in the given sentence.
2. compute_factorial(int) It takes an integer and compute the factorial of a non-negative integer n.
3. get_today_day() It returns todays day of the month 1-31.
4. get_current_hour() It return the current hour of the day in 24-hour format (0–23).
5. compute_a_squared_minus_b_cubed(int, int): It takes two integers - a and b. Computes the result of (a^2 - b^3). 
6. split_number_into_digits(int): Takes an integer number and splits it into individual digits.
7. square_numbers_in_list(list): Takes a list of numbers and Square each number in the given list. Returns the squared list.
8. sum_numbers_in_list(list): Takes a list and calculate the sum of all numbers in the given list.
9. convert_string_to_ascii(string): Takes a string and converts it into ASCII value.
10. multiply_list_elements(list): Takes a list of numbers and multiplies all the number. Returns the result. 
11. compute_log2(int): Takes an integer and computes the base-2 logarithm (log₂).
DO NOT include multiple responses. Give ONE response at a time.`;

    const fullPrompt = `${system_prompt}\n\nQuery: ${prompt}`;

    try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${API_KEY}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: fullPrompt
                    }]
                }],
                generationConfig: {
                    temperature: 0.1,
                    topK: 1,
                    topP: 1,
                    maxOutputTokens: 1024,
                }
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('API Error Response:', errorData);
            throw new Error(`API request failed with status ${response.status}: ${JSON.stringify(errorData)}`);
        }

        const data = await response.json();
        console.log('API Response:', data); // Debug log
        
        // Check if the response has the expected structure
        if (!data.candidates || !data.candidates[0] || !data.candidates[0].content || !data.candidates[0].content.parts) {
            console.error('Unexpected API response structure:', data);
            throw new Error('Unexpected API response structure');
        }

        const text = data.candidates[0].content.parts[0].text;
        if (!text) {
            throw new Error('No text in API response');
        }

        return text;
    } catch (error) {
        console.error('Error calling Gemini API:', error);
        throw error;
    }
}

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'processQuery') {
        const query = request.query;
        let last_response = null;
        let iteration = 0;
        let iteration_response = [];
        let result = '';

        const processIteration = async () => {
            while (iteration < 4) {
                const current_query = last_response === null 
                    ? query 
                    : `${query}\n\n${iteration_response.join(' ')} What should I do next?`;

                try {
                    const response = await callGeminiAPI(current_query);
                    console.log('API Response:', response); // Debug log
                    
                    if (!response) {
                        throw new Error('No response from API');
                    }

                    if (response.includes('FUNCTION_CALL:')) {
                        const parts = response.split(':');
                        if (parts.length < 2) {
                            throw new Error('Invalid FUNCTION_CALL format');
                        }
                        const function_info = parts[1].trim();
                        const [func_name, params] = function_info.split('|').map(x => x.trim());
                        
                        if (!func_name) {
                            throw new Error('No function name in FUNCTION_CALL');
                        }

                        result += `\n--- Iteration ${iteration + 1} ---\n`;
                        result += `Executing function: ${func_name}\n`;
                        result += `Parameters: ${params || 'none'}\n`;
                        
                        const iteration_result = function_caller(func_name, params || '');
                        result += `Result: ${iteration_result}\n`;
                        
                        last_response = iteration_result;
                        iteration_response.push(`In iteration ${iteration + 1} you called ${func_name} with ${params || 'no'} parameters, and the function returned ${iteration_result}.`);
                    } else if (response.includes('FINAL_ANSWER:')) {
                        const parts = response.split(':');
                        if (parts.length < 2) {
                            throw new Error('Invalid FINAL_ANSWER format');
                        }
                        result += `\n--- Final Answer ---\n`;
                        result += `${parts[1].trim()}\n`;
                        break;
                    } else {
                        throw new Error(`Unexpected response format: ${response}`);
                    }
                    iteration++;
                } catch (error) {
                    result += `\n--- Error in Iteration ${iteration + 1} ---\n`;
                    result += `Error: ${error.message}\n`;
                    break;
                }
            }
            return result;
        };

        processIteration().then(result => {
            sendResponse({ result });
        });

        return true; // Keep the message channel open for async response
    }
}); 