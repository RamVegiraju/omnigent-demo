import os

import streamlit as st
from databricks.sdk import WorkspaceClient

# --- Configuration (read from environment; never hardcode secrets) ---
MODEL = os.environ.get("OPUS_ENDPOINT", "databricks-claude-opus-4-6")

st.set_page_config(page_title="Opus 4.6 Chat on Databricks", page_icon="💬")
st.title("💬 Opus 4.6 Chat")
st.caption(f"Powered by Databricks Foundation Models · endpoint: `{MODEL}`")

# --- Authenticate via Databricks SDK unified auth (OAuth from ~/.databrickscfg) ---
# An optional named profile can be selected; otherwise unified auth falls back to
# the DEFAULT profile, environment config, or an active OAuth session.
try:
    profile = os.environ.get("DATABRICKS_CONFIG_PROFILE")
    w = WorkspaceClient(profile=profile) if profile else WorkspaceClient()
    # OpenAI-compatible client, authenticated transparently via SDK unified auth.
    client = w.serving_endpoints.get_open_ai_client()
except Exception as e:
    st.warning(
        "Couldn't resolve Databricks credentials. Log in with the unified auth "
        "(OAuth) flow before chatting:\n\n"
        "```bash\n"
        "databricks auth login --host https://<your-workspace>.cloud.databricks.com\n"
        "```\n\n"
        "Optionally set `DATABRICKS_CONFIG_PROFILE` to pick a named profile.\n\n"
        f"_Details: {e}_"
    )
    st.stop()

# --- Conversation state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay the existing conversation.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle a new user turn ---
if prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=st.session_state.messages,
                stream=True,
            )
            response = st.write_stream(stream)
        except Exception as e:
            response = f"⚠️ Error calling the endpoint: {e}"
            st.error(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
