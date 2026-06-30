"""Streamlit chatbot backed by a Databricks Foundation Model serving endpoint.

A minimal, single-file multi-turn chat UI that talks to Claude Opus served
through Databricks Model Serving. Auth is handled by the Databricks SDK's
unified auth (OAuth from `~/.databrickscfg`, env vars, or a service principal
when deployed as a Databricks App) — no secrets are hardcoded.
"""

import os

import streamlit as st
from databricks.sdk import WorkspaceClient

# --- Configuration ---------------------------------------------------------
# Single source of truth for the serving endpoint. The user originally asked
# for "Opus 4.6"; we resolved the workspace's serving endpoints and pinned the
# latest available Claude Opus endpoint instead (see README). Override via the
# MODEL_ENDPOINT env var to point at any other endpoint in your workspace.
MODEL_ENDPOINT = os.environ.get("MODEL_ENDPOINT", "databricks-claude-opus-4-8")

SYSTEM_PROMPT = "You are a helpful, concise assistant."

st.set_page_config(page_title="Databricks Opus Chat", page_icon="💬")
st.title("💬 Databricks Opus Chat")
st.caption(f"Powered by Databricks Foundation Models · endpoint: `{MODEL_ENDPOINT}`")


# --- Databricks client -----------------------------------------------------
@st.cache_resource
def get_client():
    """Build an OpenAI-compatible client bound to the workspace serving endpoints.

    The Databricks SDK resolves credentials via unified auth: a named profile
    (DATABRICKS_CONFIG_PROFILE), the DEFAULT profile in ~/.databrickscfg, an
    active `databricks auth login` OAuth session, environment variables
    (DATABRICKS_HOST + DATABRICKS_TOKEN), or — when deployed as a Databricks
    App — the auto-injected service principal. The returned client points at
    `<host>/serving-endpoints`.
    """
    profile = os.environ.get("DATABRICKS_CONFIG_PROFILE")
    workspace = WorkspaceClient(profile=profile) if profile else WorkspaceClient()
    return workspace.serving_endpoints.get_open_ai_client()


try:
    client = get_client()
except Exception as exc:  # noqa: BLE001 - surface any auth/config failure to the user
    st.error(
        "Couldn't initialize the Databricks client. Make sure you're "
        "authenticated, e.g.:\n\n"
        "```bash\n"
        "databricks auth login --host https://<your-workspace>.cloud.databricks.com\n"
        "```\n\n"
        "Or set `DATABRICKS_HOST` and `DATABRICKS_TOKEN`. Optionally set "
        "`DATABRICKS_CONFIG_PROFILE` to choose a named profile.\n\n"
        f"_Details: {exc}_"
    )
    st.stop()


# --- Conversation state ----------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Replay the conversation so far.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def stream_completion(messages):
    """Yield assistant text chunks from a streaming chat completion."""
    stream = client.chat.completions.create(
        model=MODEL_ENDPOINT,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
        stream=True,
    )
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


# --- Handle a new user turn ------------------------------------------------
if prompt := st.chat_input("Ask anything…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = st.write_stream(stream_completion(st.session_state.messages))
        except Exception as exc:  # noqa: BLE001 - keep the app alive on model errors
            response = None
            st.error(f"⚠️ The model call failed: {exc}")

    if response:
        st.session_state.messages.append({"role": "assistant", "content": response})
