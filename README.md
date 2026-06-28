# yt-demo — a two-harness Omnigent meta-harness

A small demo of **two agent harnesses working together** under one Omnigent
orchestrator:

1. **`coder`** — **Claude Code** (`claude-native`) builds a simple **Streamlit
   chatbot** whose inference runs on **Opus 4.6 via Databricks Foundation
   Models**, plus a project README.
2. **`marketer`** — an **OpenAI agent** (`openai-agents`, model `gpt-5.5`) reads
   that README and produces a **YouTube thumbnail** (real PNG via OpenAI image
   generation) and a **video description**.

The orchestrator (a `claude-sdk` brain) runs the two steps in sequence: the
marketer waits for the coder's README, then promotes it.

```
yt-demo/
├── config.yaml                 # orchestrator (claude-sdk) — runs the pipeline
├── agents/
│   ├── coder/config.yaml       # Claude Code (claude-native)
│   └── marketer/config.yaml    # OpenAI (openai-agents, gpt-5.5)
├── tools/
│   └── thumbnail.py            # generate_thumbnail() — OpenAI image gen tool
├── app/                        # ← created by the coder at run time
└── marketing/                  # ← created by the marketer at run time
```

## Prerequisites

- Omnigent installed (`omni`/`omnigent` on PATH).
- The **`claude` CLI** on PATH and logged in (the `coder` runs the real Claude
  Code CLI — you can watch it in the UI's Subagents panel).
- Python deps for the thumbnail tool: `pip install openai` (the `marketer`
  harness needs the OpenAI Agents SDK too — `pip install openai-agents`).

## Environment variables

| Variable | Used by | Notes |
|---|---|---|
| `OPENAI_API_KEY` | marketer + thumbnail tool | Your OpenAI key. **Leave `OPENAI_BASE_URL` unset** so the marketer + image gen hit api.openai.com. |
| `DATABRICKS_HOST` | the built chatbot | e.g. `https://<workspace>.cloud.databricks.com` |
| `DATABRICKS_TOKEN` | the built chatbot | Databricks PAT / SP token |
| `OPUS_ENDPOINT` | the built chatbot | Defaults to `databricks-claude-opus-4-6`; set if your serving endpoint name differs |

> The chatbot is wired to these vars but is built to **warn, not crash**, if the
> Databricks ones are unset — so the pipeline runs end-to-end even before you
> have a workspace. Fill them in (and confirm the exact Opus 4.6 endpoint name
> in your workspace) when you're ready to actually chat.

## Run it

Run **from inside this directory** (so the thumbnail function tool resolves on
`sys.path[0]`):

```bash
cd yt-demo
export OPENAI_API_KEY=...        # your (rotated) OpenAI key; do NOT commit it
unset OPENAI_BASE_URL            # ensure marketer/image-gen hit OpenAI, not a gateway
# optional, for live chatbot inference:
export DATABRICKS_HOST=https://<workspace>.cloud.databricks.com
export DATABRICKS_TOKEN=...

omnigent run .
```

Then ask the orchestrator to **"build the project and make the YouTube
assets."** It will dispatch the `coder`, wait for it, then dispatch the
`marketer`. When it finishes you'll have:

- `app/` — the Streamlit chatbot (`streamlit run app/app.py`)
- `marketing/youtube_description.md` — title + description
- `marketing/thumbnail.png` — the generated thumbnail

## Notes

- **Why `gpt-5.5` is pinned on the marketer:** the `openai-agents` harness
  treats an unpinned model as a Databricks model and would route to the
  Databricks gateway. Pinning a non-`databricks-` id keeps the marketer on real
  OpenAI.
- **Opus 4.6 is the app's runtime model**, not a harness model — the Streamlit
  app calls the Databricks Foundation Model serving endpoint directly via the
  OpenAI-compatible API.
- No secrets are committed: every credential is read from the environment.
