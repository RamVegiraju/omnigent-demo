"""Minimal Streamlit chatbot.

Inference runs on Claude Opus 4.6 served by Databricks Foundation Models via the
OpenAI-compatible client. If Databricks is unavailable -- creds missing OR a call
fails at runtime -- it falls back to the standard OpenAI API. The UI always shows
which engine answered. No secrets are hardcoded; everything comes from the env.
"""

import os

import streamlit as st
from openai import OpenAI

# --- Configuration (read from environment; never hardcode secrets) ------------
DATABRICKS_HOST = os.environ.get("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN")
OPUS_ENDPOINT = os.environ.get("OPUS_ENDPOINT", "databricks-claude-opus-4-6")

# Fallback engine: standard OpenAI API authenticated in the terminal.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def databricks_engine():
    """Return (client, model, label) for Databricks FM, or None if unconfigured."""
    if DATABRICKS_HOST and DATABRICKS_TOKEN:
        client = OpenAI(
            base_url=f"{DATABRICKS_HOST.rstrip('/')}/serving-endpoints",
            api_key=DATABRICKS_TOKEN,
        )
        return client, OPUS_ENDPOINT, f"Databricks FM · {OPUS_ENDPOINT}"
    return None


def openai_engine():
    """Return (client, model, label) for the OpenAI fallback, or None if no key."""
    if OPENAI_API_KEY:
        return OpenAI(api_key=OPENAI_API_KEY), OPENAI_MODEL, f"OpenAI · {OPENAI_MODEL}"
    return None


# --- UI -----------------------------------------------------------------------
st.set_page_config(page_title="Opus 4.6 Chatbot", page_icon="💬")
st.title("💬 Opus 4.6 Chatbot")
st.caption("Streamlit chat UI · Claude Opus 4.6 on Databricks Foundation Models")

primary = databricks_engine()
fallback = openai_engine()

if primary is None and fallback is None:
    st.warning(
        "No LLM engine configured. Set `DATABRICKS_HOST` and `DATABRICKS_TOKEN` "
        "to use Databricks Foundation Models (Opus 4.6), or set `OPENAI_API_KEY` "
        "for the OpenAI fallback, then reload.",
        icon="⚠️",
    )
    st.stop()

# Conversation history survives Streamlit reruns via session_state.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay the conversation so far.
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


def stream_reply(engine):
    """Stream a completion from (client, model, label); returns the full text."""
    client, model, _ = engine
    stream = client.chat.completions.create(
        model=model,
        messages=st.session_state.messages,
        stream=True,
    )
    return st.write_stream(stream)


# Handle a new user turn.
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reply = None
        # Try the primary engine (Databricks) first when available.
        if primary is not None:
            try:
                st.caption(f"Engine: **{primary[2]}**")
                reply = stream_reply(primary)
            except Exception as primary_error:  # noqa: BLE001
                if fallback is not None:
                    st.warning(
                        f"Databricks FM call failed ({primary_error}). "
                        "Falling back to the OpenAI API.",
                        icon="⚠️",
                    )
                else:
                    st.error(f"Databricks FM call failed: {primary_error}")

        # Use the OpenAI fallback if there's no primary, or the primary failed.
        if reply is None and fallback is not None:
            try:
                st.caption(f"Engine: **{fallback[2]}**")
                reply = stream_reply(fallback)
            except Exception as fallback_error:  # noqa: BLE001
                st.error(f"OpenAI fallback failed: {fallback_error}")

    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})
