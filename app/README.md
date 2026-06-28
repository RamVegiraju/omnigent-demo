# 💬 Opus 4.6 Chatbot on Databricks Foundation Models

A minimal, single-file **Streamlit chatbot** whose inference runs on
**Claude Opus 4.6**, served through **Databricks Foundation Model** serving
endpoints. It's a clean, copy-pasteable starting point for anyone who wants a
real conversational UI on top of a Databricks-hosted frontier model — no
framework sprawl, no boilerplate, just a chat box wired to an endpoint.

## Why it's useful

- **Frontier model, your governance.** Chat with Claude Opus 4.6 while inference
  stays inside your Databricks workspace, using your identity and your access
  controls — not a third-party SaaS.
- **OAuth, no long-lived tokens.** Authentication uses the Databricks SDK's
  unified auth (`databricks auth login`), so the app picks up your OAuth session
  from `~/.databrickscfg` — no personal access tokens to export or leak.
- **Drop-in OpenAI-compatible client.** The SDK hands you an OpenAI client wired
  to your workspace's serving endpoints, so the `openai` API you already know
  works unchanged.
- **Tiny and readable.** The entire app is ~60 lines in one file. Easy to read,
  fork, and extend into your own product.
- **Streaming out of the box.** Responses render token-by-token for a
  responsive, ChatGPT-like feel.

## Architecture

```
You (browser)
     │
     ▼
Streamlit chat UI  (app.py)
  · st.chat_input / st.chat_message
  · history in st.session_state
     │
     ▼  Databricks SDK unified auth (OAuth from ~/.databrickscfg)
        WorkspaceClient().serving_endpoints.get_open_ai_client()
     │
     ▼
Databricks Foundation Model endpoint
        databricks-claude-opus-4-6  (Claude Opus 4.6)
```

The Streamlit front end keeps the conversation in session state. It builds a
`WorkspaceClient` via the Databricks SDK's unified auth — resolving an OAuth
profile from `~/.databrickscfg` — and asks the SDK for an OpenAI-compatible
client bound to the workspace's serving endpoints. It then sends the full
message history to the Databricks endpoint and streams the model's reply back
into the chat window.

## What you'll see in the demo

1. A browser tab opens with a titled chat interface: **"💬 Opus 4.6 Chat"** and a
   caption showing the active Databricks endpoint.
2. If you're not logged in, a friendly warning tells you exactly how to run
   `databricks auth login` — the app never crashes on missing auth.
3. Type a question into the chat box and watch **Opus 4.6 stream its answer**
   token-by-token.
4. Keep chatting — the app remembers the full conversation, so follow-up
   questions retain context across turns.

## Setup

### 1. Log in with Databricks OAuth (unified auth)

Authentication uses the Databricks SDK's unified auth flow — no
`DATABRICKS_HOST` / `DATABRICKS_TOKEN` exports required. Log in once:

```bash
databricks auth login --host https://<your-workspace>.cloud.databricks.com
```

This stores an OAuth profile in `~/.databrickscfg` that the app picks up
automatically.

**Optional environment variables:**

| Variable                    | Required | Description                                                                          |
| --------------------------- | -------- | ------------------------------------------------------------------------------------ |
| `DATABRICKS_CONFIG_PROFILE` | ⬜       | Pick a named profile from `~/.databrickscfg`. Defaults to `DEFAULT` / OAuth session. |
| `OPUS_ENDPOINT`             | ⬜       | Serving endpoint name. Defaults to `databricks-claude-opus-4-6`.                     |

```bash
export DATABRICKS_CONFIG_PROFILE=my-profile          # optional; pick a named profile
export OPUS_ENDPOINT=databricks-claude-opus-4-6       # optional; this is the default
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run it

```bash
streamlit run app.py
```

Streamlit will print a local URL (usually http://localhost:8501) — open it and
start chatting.
