# Mega Project AI Chatbot

This repository contains a simple AI chat interface (frontend) and a Python/Flask backend that proxies requests to the Groq/OpenAI‑compatible API using an API key stored in an environment variable.

## Files

- `index.html` – frontend chat UI; fetches from the backend.
- `app.py` – Flask server and API implementation.
- `.env` – environment variables (should contain `GROK_API_KEY`).
- `requirements.txt` – Python dependencies.

## Setup

1. **Create a Python virtual environment** (recommended):
   ```powershell
   cd "c:\Users\biswa\Desktop\ALL PDF\mega_project"
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # PowerShell
   # or `source .venv/bin/activate` on Unix
   ```

2. **Install packages**:
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

Copy your API key into `.env` or set the `GROK_API_KEY` environment variable.  You can also override the API URL and model names:
   ```dotenv
   GROK_API_KEY=groq_your_real_key_here
   # custom endpoint (defaults to Groq chat/completions URL)
   # GROK_API_URL=https://api.groq.com/openai/v1/chat/completions
   # primary model to use
   # GROK_MODEL=llama-3.1-8b-instant
   # optional fallback if primary returns model_not_found
   # GROK_FALLBACK_MODEL=gpt-3.5-turbo
   ```

4. **Run the server**:
   ```powershell
   python app.py
   ```
   The app listens on `http://localhost:5000` and will serve the chat UI. Open that URL in your browser.

## Usage

- Type a message in the input box and press enter or click the send button.
* The frontend sends the message to `/api/chat`; the backend passes it to
  the Groq/OpenAI‑compatible API using the `GROK_MODEL` value (default
  `llama-3.1-8b-instant`). If the model is not accessible with your key the server
  automatically retries once using the `GROK_FALLBACK_MODEL`.
* Responses appear in the chat window.  If you see `API error: <something>`
  the text after `error:` will now contain a human‑readable message instead of
  `[object Object]`.  For missing-model errors you’ll also get a hint about
  which models to set in `.env`.

## Notes

- All secret keys are kept on the server. The frontend no longer contains any API key.
- You can enhance the backend (logging, models, error handling) as needed.

---

## Render Deployment

This project is ready for deployment on [Render](https://render.com).

1. **Connect your GitHub repository** to Render and create a new "Web Service".
2. **Environment variables:** set `GROK_API_KEY` (required) and
   optionally `GROK_MODEL` / `GROK_FALLBACK_MODEL` in the Render dashboard.
3. Build & deploy; Render will install dependencies from `requirements.txt` and
   use the provided `Procfile` to launch the app with Gunicorn.

The service listens on the port specified by the `PORT` environment variable
(automatically supplied by Render).  The `runtime.txt` locks the Python version
for reproducible builds.

---

If you change the frontend filename in the future, update the `index()` route in `app.py` accordingly.

> **Tip:** an older copy named `APP1.html` may still exist in the repo. You can remove it if it’s no longer needed to avoid confusion.
