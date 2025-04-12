# 🧠 AI Query Processor – Chrome Extension + Python Backend

This project is a simple AI-powered Chrome extension connected to a Python backend server. You can run the server locally and interact with it through a Chrome extension. Logs will guide you through the interaction in real time.

---

## 🚀 Getting Started

Follow the steps below to set up and run the project on your local machine.

### 1️⃣ Run the Python Server

Make sure you have Python installed. Then, open your terminal and run:

```bash
python server.py
```

This will start a Flask server locally.

---

### 2️⃣ Check if Server is Running

Once the server is running, visit the following URL in your browser:

[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

If everything is working, you should see a response from the server.

---

### 3️⃣ Load the Chrome Extension

1. Open Google Chrome.
2. Go to `chrome://extensions/`
3. Enable **Developer mode** (top-right corner).
4. Click **Load unpacked**.
5. Select the extension folder from this project.

The extension will now be available in your Chrome toolbar.

---

### 4️⃣ Use the Extension

- Click on the extension icon in your browser.
- Enter your query in the input box.
- Submit the query.
- Observe the logs printed below the query box to see how the backend processes it.

---

## 🛠 Tech Stack

- **Frontend:** HTML, JavaScript (Chrome Extension APIs)
- **Backend:** Python, Flask
- **Communication:** HTTP Requests from Extension → Flask Server

---

## 🤝 Contributing

Feel free to fork this repo and open a pull request if you'd like to contribute or enhance functionality.

---

## 💡 Author

Made with ❤️ by [Ajay Bhattacharjee]
