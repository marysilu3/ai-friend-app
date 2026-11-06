# My AI Friend

A mobile-friendly personal AI companion with saved chat history, new chat, rename, clear and delete controls. It supports English, Malayalam and Manglish by asking the AI model to follow the language used in each message.

## AI provider

This app is configured for Groq's OpenAI-compatible chat completions API:
- Base URL: `https://api.groq.com/openai/v1`
- Default model: `llama-3.3-70b-versatile`
- Set `AI_API_KEY` to your Groq API key in the hosting provider's private environment settings.

Groq usage is subject to the current account plan, model availability, and rate limits.

## Private login

Before exposing this app publicly, configure:
- `APP_USERNAME` (defaults to `friend`)
- `APP_PASSWORD` (required; the app returns HTTP 503 if it is missing)

The app uses browser HTTP Basic Authentication. Choose a long, unique password and do not commit it to GitHub.

## Run locally

1. Install Python 3.10 or newer.
2. Create and activate a virtual environment.
3. Run `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and set your Groq API key and a private app password.
5. Run `python app.py` and open http://127.0.0.1:5000.

## Deploy

Deploy as a Python web service with build command `pip install -r requirements.txt` and start command `gunicorn app:app`. Set `AI_API_KEY`, `APP_USERNAME`, and `APP_PASSWORD` as private environment variables. Use persistent storage for `chats.db` if chat history must survive restarts and deployments.

The chat database stores messages on the server, and the configured AI provider processes messages sent to it; review that provider's data policy. Do not commit API keys or passwords.
