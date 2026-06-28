# 💬 Opus 4.6 Chatbot — Streamlit × Databricks Foundation Models

A dead-simple, single-file chatbot that puts **Claude Opus 4.6** — a frontier-class
model — behind a clean Streamlit chat interface, with inference served by
**Databricks Foundation Models**.

The whole point: show how little code it takes to ship a production-shaped chat app
on top of an enterprise model-serving platform. No frameworks, no boilerplate, no
secrets in code — just `streamlit run app.py`.

## Why it matters (the value proposition)

- **Frontier intelligence, enterprise serving.** Opus 4.6 runs on Databricks
  Foundation Models, so the model lives next to your governed data and serving
  infrastructure — no GPUs to provision, no model to host.
- **Drop-in OpenAI compatibility.** Databricks serves the model behind an
  OpenAI-compatible endpoint, so the same `OpenAI()` client you already know just
  works — only the `base_url` and `api_key` change.
- **Resilient by design.** If Databricks credentials are missing *or* a live call
  fails, the app automatically falls back to the standard OpenAI API so the demo
  never dead-ends. The UI always shows **which engine answered**.
- **Minimal & readable.** ~120 lines in one file. Easy to read on screen, easy to
  fork.

## Architecture

```
┌──────────────┐     OpenAI-compatible       ┌──────────────────────────────┐
│  Streamlit   │  chat.completions.create    │  Databricks Foundation       │
│  chat UI     │ ──────────────────────────► │  Models  →  Opus 4.6         │
│  (app.py)    │                             │  (databricks-claude-opus-4-6) │
└──────┬───────┘                             └──────────────────────────────┘
       │  no creds OR call fails → fall back
       ▼
┌─────────────────────────────┐
│  OpenAI API (OPENAI_API_KEY)│
└─────────────────────────────┘
```

- **Frontend:** Streamlit (`st.chat_input`, `st.chat_message`). Conversation
  history is kept in `st.session_state` and replayed on every rerun.
- **Inference (primary):** `OpenAI(base_url=f"{DATABRICKS_HOST}/serving-endpoints",
  api_key=DATABRICKS_TOKEN)` pointed at the Opus 4.6 serving endpoint.
- **Inference (fallback):** the standard `OpenAI()` client reading
  `OPENAI_API_KEY` from the environment.
- Responses are **streamed** token-by-token with `st.write_stream`.

## What you'll see in the demo

1. The app opens to a clean **"💬 Opus 4.6 Chatbot"** screen.
2. As the first answer streams in, a caption reads
   **"Engine: Databricks FM · databricks-claude-opus-4-6"** — confirming inference
   is running on Databricks-served Opus 4.6.
3. Type a question into the chat box; the assistant's reply **streams in live**,
   token by token.
4. Keep the conversation going — earlier turns stay on screen because history is
   kept in session state, so follow-ups answer with full context.
5. Resilience in action: if Databricks creds are absent or a call fails, the app
   shows a friendly banner and **transparently falls back to the OpenAI API**
   instead of crashing — and the engine caption updates to match.

## Configure environment variables

No secrets are stored in the code — everything is read from the environment.

**Primary engine — Databricks Foundation Models (Opus 4.6):**

```bash
export DATABRICKS_HOST="https://<your-workspace>.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi..."                    # Databricks personal access token
export OPUS_ENDPOINT="databricks-claude-opus-4-6"    # optional; this is the default
```

**Fallback engine — OpenAI API (optional):**

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-4o-mini"                    # optional; this is the default
```

If neither Databricks nor OpenAI is configured, the app shows a friendly warning
naming the variables to set rather than crashing.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (usually http://localhost:8501).

## Files

| File               | Purpose                                      |
| ------------------ | -------------------------------------------- |
| `app.py`           | The entire Streamlit chat app.               |
| `requirements.txt` | Python dependencies (`streamlit`, `openai`). |
| `README.md`        | This file.                                   |
