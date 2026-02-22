import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# load environment variables from .env (development only)
load_dotenv()

# Grok-style configuration: API key, endpoint URL and model name. The
# provided project originally targeted the Groq/OpenAI responses endpoint; the
# user now has a Grok model key, which uses a chat/completions URL.
GROK_API_KEY = os.getenv("GROK_API_KEY")
if not GROK_API_KEY:
    raise RuntimeError("GROK_API_KEY not set in environment")

GROK_API_URL = os.getenv(
    "GROK_API_URL",
    "https://api.groq.com/openai/v1/chat/completions"
)

# primary model to request. default to llama-3.1-8b-instant as per user's note.
MODEL_NAME = os.getenv("GROK_MODEL", "llama-3.1-8b-instant")
# optional fallback model name, only used if the first model is not found.
FALLBACK_MODEL = os.getenv("GROK_FALLBACK_MODEL")

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # allow cross‑origin for development; remove or lock down in production

@app.route('/')
def index():
    # serve the frontend HTML file (now named index.html)
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Receive a JSON body with {"message": "..."} and forward it to Groq.
    The Groq service is OpenAI-compatible so we hit the `/responses` endpoint.
    """

    data = request.get_json(silent=True)
    if not data or 'message' not in data:
        return jsonify(error="Missing 'message' in JSON"), 400

    user_message = data['message']

    def _call_model(model_name):
        return requests.post(
            GROK_API_URL,
            headers={
                "Authorization": f"Bearer {GROK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model_name,
                # chat/completions endpoint expects messages list
                "messages": [{"role": "user", "content": user_message}],
            },
            timeout=30,
        )

    try:
        resp = _call_model(MODEL_NAME)
    except requests.RequestException as e:
        return jsonify(error="backend request failed: " + str(e)), 500

    try:
        groq_data = resp.json()
    except ValueError:
        return jsonify(error="invalid JSON from groq"), 500

    if not resp.ok:
        # Attempt to help with a missing-model error by falling back once.
        err_obj = groq_data.get("error") or groq_data.get("message") or resp.text
        code = None
        if isinstance(err_obj, dict):
            code = err_obj.get("code")
            err_msg = err_obj.get("message", str(err_obj))
        else:
            err_msg = str(err_obj)

        # if the error indicates the model is not found and we have a
        # different fallback model configured, try again automatically.
        if code == "model_not_found" and FALLBACK_MODEL and FALLBACK_MODEL != MODEL_NAME:
            try:
                fallback_resp = _call_model(FALLBACK_MODEL)
                fb_data = fallback_resp.json()
            except Exception as e:
                # if fallback attempt fails, return original error
                return jsonify(error=err_msg), resp.status_code

            if fallback_resp.ok:
                # extract from chat/completions response
                ai_text = ""
                if isinstance(fb_data, dict):
                    choices = fb_data.get('choices', [])
                    if choices:
                        msg = choices[0].get('message', {})
                        # messages may have content structured as list
                        content = msg.get('content')
                        if isinstance(content, list):
                            ai_text = "".join(c.get('text','') for c in content if isinstance(c, dict))
                        elif isinstance(content, str):
                            ai_text = content
                if not ai_text:
                    ai_text = "Sorry, I didn't get a response from the AI."
                return jsonify(response=ai_text)
            else:
                # fallback also failed; update message accordingly
                err_msg = f"{err_msg} (fallback model {FALLBACK_MODEL} also unavailable)"
                return jsonify(error=err_msg), fallback_resp.status_code

        # otherwise just return the original error message
        return jsonify(error=err_msg), resp.status_code

    # extract text from a chat/completions response
    ai_text = ""
    if isinstance(groq_data, dict):
        choices = groq_data.get('choices', [])
        if choices:
            msg = choices[0].get('message', {})
            content = msg.get('content')
            if isinstance(content, list):
                ai_text = "".join(c.get('text','') for c in content if isinstance(c, dict))
            elif isinstance(content, str):
                ai_text = content

    if not ai_text:
        ai_text = "Sorry, I didn't get a response from the AI."

    return jsonify(response=ai_text)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
