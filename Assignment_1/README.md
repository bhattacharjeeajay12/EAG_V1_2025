# Multi-Language Translator Chrome Extension

This Chrome extension allows you to translate selected English text to Hindi, German, or Kannada with a simple selection.

## Features

- Translate selected text instantly
- Support for Hindi, German, and Kannada
- Easy language preference selection
- Clean floating translation display

## Setup Instructions

1. Get a Google Cloud Translation API key:
   - Go to the Google Cloud Console
   - Create a new project or select an existing one
   - Enable the Cloud Translation API
   - Create credentials (API key)
   - Copy your API key

2. Replace the API key:
   - Open `content.js`
   - Replace `YOUR_API_KEY` with your actual Google Cloud Translation API key

3. Load the extension in Chrome:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" in the top right
   - Click "Load unpacked"
   - Select the directory containing these extension files

## Usage

1. Click the extension icon to select your preferred target language
2. Select any English text on any webpage
3. A translation will appear in a floating box near the selected text
4. Click anywhere outside the translation to dismiss it

## Files Structure

- `manifest.json`: Extension configuration
- `popup.html`: Language selection UI
- `popup.js`: Handles language preference
- `content.js`: Handles text selection and translation
- `background.js`: Background initialization
- `README.md`: This documentation

## Note

You must have a valid Google Cloud Translation API key for the extension to work. The API key should be kept private and not shared publicly. 