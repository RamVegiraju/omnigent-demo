# 💬 Databricks Opus Chatbot (Streamlit)

A minimal, single-file **Streamlit chatbot** whose inference runs on **Claude
Opus**, served through a **Databricks Foundation Model** serving endpoint. It's
a clean, copy-pasteable starting point for a multi-turn conversational UI on top
of a Databricks-hosted frontier model — no framework sprawl, just a chat box
wired to an endpoint with streaming responses.

## Model endpoint

The chatbot targets a single serving endpoint, defined as one constant
(`MODEL_ENDPOINT`) at the top of [`app.py`](app.py) and overridable via the
`MODEL_ENDPOINT` environment variable.

> **Note on the model version.** The original request was for **"Opus 4.6"**.
> We listed the serving endpoints actually exposed by the target workspace and
> pinned the **latest available Claude Opus endpoint**, which is
> **`databricks-claude-opus-4-8`**. (`databricks-claude-opus-4-6` does also
> exist in this workspace, but per the brief we substituted the newest Opus.)
> To use a different endpoint, set `MODEL_ENDPOINT` — no code change needed.

## How it works

```
You (browser)
     │
     ▼
Streamlit chat UI  (app.py)
  · st.chat_input / st.chat_message
  · history in st.session_state
  · streaming via st.write_stream
     │
     ▼  Databricks SDK unified auth (OAuth / PAT / service principal)
        WorkspaceClient().serving_endpoints.get_open_ai_client()
     │
     ▼
Databricks Foundation Model endpoint  (databricks-claude-opus-4-8)
```

The app keeps the full conversation in `st.session_state`, builds an
OpenAI-compatible client via the Databricks SDK (which points at
`<workspace-host>/serving-endpoints`), sends the message history to the
endpoint, and streams the reply back token-by-token.

## Prerequisites

- Python 3.11
- Access to a Databricks workspace with the Claude Opus Foundation Model
  endpoint enabled (Pay-per-token Foundation Model APIs)

## Auth setup (no hardcoded secrets)

Authentication is handled by the Databricks SDK's **unified auth** — the app
never embeds credentials. Use whichever of these the SDK can resolve:

**Option A — OAuth (recommended for local use):**

```bash
databricks auth login --host https://<your-workspace>.cloud.databricks.com
```

This stores an OAuth profile in `~/.databrickscfg` that the app picks up
automatically.

**Option B — Personal access token via environment variables:**

```bash
export DATABRICKS_HOST=https://<your-workspace>.cloud.databricks.com
export DATABRICKS_TOKEN=dapi...        # do NOT commit this
```

**When deployed as a Databricks App**, the platform injects a service principal
(`DATABRICKS_CLIENT_ID` / `DATABRICKS_CLIENT_SECRET`) automatically — no setup
needed.

### Environment variables

| Variable                    | Required | Description                                                                          |
| --------------------------- | -------- | ------------------------------------------------------------------------------------ |
| `MODEL_ENDPOINT`            | ⬜       | Serving endpoint name. Defaults to `databricks-claude-opus-4-8`.                     |
| `DATABRICKS_CONFIG_PROFILE` | ⬜       | Pick a named profile from `~/.databrickscfg`. Defaults to `DEFAULT` / OAuth session. |
| `DATABRICKS_HOST`           | ⬜       | Workspace URL — only needed for token (PAT) auth.                                    |
| `DATABRICKS_TOKEN`          | ⬜       | Personal access token — only needed for token (PAT) auth. Never commit it.           |

## Run locally

```bash
cd app/streamlit_chatbot
pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints a local URL (usually http://localhost:8501) — open it and
start chatting. Follow-up questions retain context across turns; use **Clear
conversation** in the sidebar to reset.

## Deploy to Databricks Apps (optional)

[`app.yaml`](app.yaml) is included for deployment to **Databricks Apps**:

```bash
databricks apps deploy <app-name> --source-code-path .
```

The app's service principal needs `CAN_QUERY` on the serving endpoint. See the
[Databricks Apps docs](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/)
for details.
