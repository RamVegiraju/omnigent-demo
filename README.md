# yt-demo — a two-harness Omnigent meta-harness

A small prototype showing **two agent harnesses working together** under one
Omnigent orchestrator, with an **enforced human-in-the-loop approval gate**
before any deliverable is written. Text only — no image generation.

- **`coder`** — **Claude Code** (`claude-native`) builds a simple **Streamlit
  chatbot** backed by **Opus 4.6 via Databricks Foundation Models**, plus a README.
- **`marketer`** — an **OpenAI agent** (`openai-agents`, `gpt-4o`) reads that
  README and **authors marketing text** — proposed directions first, then, after
  a human approves, the final YouTube description + repo summary. It returns text
  in its reply and writes nothing to disk.
- The **orchestrator** (`claude-sdk`) sequences the sub-agents, surfaces the
  marketer's options for **human approval**, then persists the approved text.

## What it shows off

- **Multi-harness orchestration** — a `claude-sdk` brain drives a `claude-native`
  coder *and* an `openai-agents` marketer in one pipeline.
- **Clean hand-offs** — the coder's `app/README.md` is the contract the marketer builds on.
- **Enforced gate** — `config.yaml` attaches `ask_on_os_tools` to the orchestrator,
  so every file write needs a human approval card. Because the policy lives in the
  spec, a future session can't skip it.

```
yt-demo/
├── config.yaml              # orchestrator (claude-sdk) — gated pipeline + approval gate
├── agents/
│   ├── coder/config.yaml    # Claude Code (claude-native)
│   └── marketer/config.yaml # OpenAI (openai-agents, gpt-4o) — text only
├── app/                     # ← built by the coder
└── marketing/               # ← written by the orchestrator (gated)
```

## Setup & run

```bash
cd yt-demo
export OPENAI_API_KEY=...     # for the marketer; do NOT commit it
unset OPENAI_BASE_URL         # so the marketer hits api.openai.com

omnigent run .
```

Then ask the orchestrator to **"build the project and make the marketing assets."**
It runs the `coder`, then the `marketer` for proposed directions, and **pauses for
you to approve** a title + angle before producing and persisting the finals.

**Prerequisites:** Omnigent installed, the `claude` CLI on PATH and logged in, and
`pip install openai-agents`.

## Running the Streamlit app (optional)

The chatbot is what the pipeline *builds* — it's not the focus of the video, but if
you want to try it. Auth uses Databricks OAuth (unified auth), so there are no
tokens to export — just log in once:

```bash
databricks auth login --host https://<workspace>.cloud.databricks.com
# optional: export OPUS_ENDPOINT=databricks-claude-opus-4-6

pip install -r app/requirements.txt
streamlit run app/app.py
```

If you're not logged in the app warns instead of crashing, so the pipeline runs
end-to-end even before you have a workspace.

## References

- [Introducing Omnigent: a meta-harness to combine, control, and share your agents](https://www.databricks.com/blog/introducing-omnigent-meta-harness-combine-control-and-share-your-agents) — Databricks blog
- [omnigent-ai/omnigent](https://github.com/omnigent-ai/omnigent/tree/main) — Omnigent source on GitHub
