# Page Summarizer Chrome Extension

A Chrome extension that summarizes web pages in simple English using the Gemini AI model.

## Features

- One-click page summarization
- Simple and clean user interface
- Summarizes content in easy-to-understand language
- Loading indicator for better user experience

## Setup Instructions

1. Clone or download this repository
2. Get your Gemini API key from Google AI Studio
3. Open `popup.js` and replace `'YOUR_API_KEY'` with your actual Gemini API key
4. Open Chrome and go to `chrome://extensions/`
5. Enable "Developer mode" in the top right corner
6. Click "Load unpacked" and select the extension directory

## Usage

1. Click the extension icon in your Chrome toolbar
2. Click the "Summarize Page" button
3. Wait for the summary to appear
4. The summary will be displayed in simple, easy-to-understand English

## Files Structure

- `manifest.json`: Extension configuration
- `popup.html`: Extension popup UI
- `popup.js`: Main logic for summarization
- `images/`: Contains extension icons
- `README.md`: Documentation

## Note

Make sure to keep your API key secure and never share it publicly. The extension requires an active internet connection to work.

## Technical Requirements

- Chrome browser
- Gemini API key
- Active internet connection

## Privacy

This extension only accesses the content of the current tab when you click the summarize button. No data is stored or sent anywhere except to the Gemini API for summarization purposes. 