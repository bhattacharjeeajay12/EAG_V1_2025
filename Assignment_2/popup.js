// Your API key should be stored securely
const API_KEY = 'AIzaSyBY02JEi8Gnbu_ark0akR4dub7GkArx9fI';
const API_ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';

document.addEventListener('DOMContentLoaded', function() {
    const summarizeBtn = document.getElementById('summarizeBtn');
    const summaryDiv = document.getElementById('summary');
    const loader = document.getElementById('loader');

    summarizeBtn.addEventListener('click', async () => {
        try {
            // Show loader and disable button
            loader.style.display = 'block';
            summarizeBtn.disabled = true;
            summaryDiv.style.display = 'none';

            // Get the active tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

            // Execute script to get page content
            const [{ result: pageContent }] = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                function: () => {
                    // Get main content, remove scripts, styles, and other unnecessary elements
                    const content = document.body.innerText;
                    return content.replace(/\s+/g, ' ').trim();
                }
            });

            // Prepare the prompt for better summarization
            const prompt = `Please summarize the following text in simple English that anyone can understand. Focus on the main points and key information:

${pageContent}

Please provide a concise summary that captures the essential information while being easy to read and understand.`;

            // Call Gemini API
            const response = await fetch(`${API_ENDPOINT}?key=${API_KEY}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    contents: [{
                        parts: [{
                            text: prompt
                        }]
                    }]
                })
            });

            if (!response.ok) {
                throw new Error('API request failed');
            }

            const data = await response.json();
            const summary = data.candidates[0].content.parts[0].text;

            // Display the summary
            summaryDiv.textContent = summary;
            summaryDiv.style.display = 'block';

        } catch (error) {
            console.error('Error:', error);
            summaryDiv.textContent = 'Error generating summary. Please try again.';
            summaryDiv.style.display = 'block';
        } finally {
            // Hide loader and enable button
            loader.style.display = 'none';
            summarizeBtn.disabled = false;
        }
    });
}); 