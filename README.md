# My AI Friend

A mobile-friendly personal AI companion with saved chat history, new chat, rename, clear and delete controls. It supports English, Malayalam and Manglish by asking the AI model to follow the language used in each message.

## Run locally

1. Install Python 3.10 or newer.
2. Create and activate a virtual environment.
3. Run `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and add your AI API key.
5. Run `python app.py` and open http://127.0.0.1:5000.

## Deploy

Deploy as a Python web service with start command `gunicorn app:app` (add gunicorn to requirements) and set `AI_API_KEY`, `AI_BASE_URL`, and `AI_MODEL` as private environment variables. Use persistent disk/storage for `chats.db`.

## Important security notes

This is an initial personal-use prototype, not yet hardened for public multi-user deployment. Add authentication before exposing it to the internet. Do not commit API keys. The chat database stores messages on the server, and the configured AI provider processes messages sent to it; review that provider's data policy.
