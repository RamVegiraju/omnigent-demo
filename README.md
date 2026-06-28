# yt-demo — a two-harness Omnigent meta-harness

A small prototype showing **two agent harnesses working together** under one
Omnigent orchestrator, with an **enforced human-in-the-loop approval gate**
before any deliverable is written. **Text only — no image generation.**

1. **`coder`** — **Claude Code** (`claude-native`) builds a simple **Streamlit
   chatbot** whose inference runs on **Opus 4.6 via Databricks Foundation
   Models**, plus a project README.
2. **`marketer`** — an **OpenAI agent** (`openai-agents`, model `gpt-4o`) reads
   that README and **authors marketing text** — first proposed directions, then,
   after a human approves, the final **YouTube description** and a **repo
   summary / explainer page**. It **returns text in its reply and writes nothing
   to disk.**

The orchestrator (a `claude-sdk` brain) runs a **gated pipeline**. It writes no
code and no marketing copy itself — it sequences the sub-agents, surfaces the
marketer's proposed directions for **human approval**, then persists the
approved GPT-authored text:

1. Dispatch the `coder`; wait for `app/` + `app/README.md`.
2. **Propose** — dispatch the `marketer` in `PROPOSE` mode; it returns 4-5 title
   options + an angle for the repo summary page (text).
3. **🛑 Human approval** — the orchestrator presents the options and ends its
   turn; **you** pick/edit a title + confirm the angle before anything is produced.
4. **Produce** — dispatch the `marketer` in `PRODUCE` mode with your approved
   choice; it returns the final YouTube description + repo summary page (text).
5. **Persist** — the orchestrator writes `marketing/youtube_description.md` +
   `marketing/repo_summary.md` from the marketer's reply.

> **What this shows off (Omnigent benefits).**
> - **Multi-harness orchestration** — a `claude-sdk` brain drives a
>   `claude-native` coder *and* an `openai-agents` marketer in one pipeline.
> - **Clean sub-agent hand-offs** — the coder's `app/README.md` is the contract
>   the marketer builds on.
> - **Enforced human-in-the-loop** — see below.

> **Enforced gate (not just convention).** The orchestrator carries an
> `ask_on_os_tools` guardrail policy, so **every file/shell op it makes requires
> a human approval card**. In this pipeline the orchestrator's only os ops are
> *persisting the two deliverables* (step 5) — so a person **must** approve
> before the final copy is written. Because the policy lives in `config.yaml`,
> **a future session cannot skip it.** The marketer only *proposes* and *authors*
> text, so it stays ungated and frictionless.

> **Why the orchestrator persists instead of the marketer:** keeping the
> marketer **text-only** (it returns its work in its reply) keeps the
> `openai-agents` harness on a single, reliable tool call (reading the README)
> and routes all writes through the `claude-sdk` orchestrator — where the
> enforced approval gate lands. All creative content is still GPT-authored.

```
yt-demo/
├── config.yaml                 # orchestrator (claude-sdk) — gated pipeline + ask_on_os_tools gate
├── agents/
│   ├── coder/config.yaml       # Claude Code (claude-native)
│   └── marketer/config.yaml    # OpenAI (openai-agents, gpt-4o) — text only, propose/produce
├── app/                        # ← created by the coder at run time
│   ├── app.py                  #    Streamlit chat UI
│   ├── requirements.txt
│   └── README.md               #    read by the marketer
└── marketing/                  # ← written by the ORCHESTRATOR at run time (gated)
    ├── youtube_description.md   #    GPT-authored by the marketer, persisted by the orchestrator
    └── repo_summary.md          #    GPT-authored by the marketer, persisted by the orchestrator
```

## Prerequisites

- Omnigent installed (`omni`/`omnigent` on PATH).
- The **`claude` CLI** on PATH and logged in (the `coder` runs the real Claude
  Code CLI — you can watch it in the UI's Subagents panel).
- Python deps: `pip install openai-agents` (the `marketer` harness).

## Environment variables

| Variable | Used by | Notes |
|---|---|---|
| `OPENAI_API_KEY` | marketer | Your OpenAI key. **Leave `OPENAI_BASE_URL` unset** so the marketer hits api.openai.com. |
| `DATABRICKS_HOST` | the built chatbot | e.g. `https://<workspace>.cloud.databricks.com` |
| `DATABRICKS_TOKEN` | the built chatbot | Databricks PAT / SP token |
| `OPUS_ENDPOINT` | the built chatbot | Defaults to `databricks-claude-opus-4-6`; set if your serving endpoint name differs |

> The chatbot is wired to these vars but is built to **warn, not crash**, if the
> Databricks ones are unset — so the pipeline runs end-to-end even before you
> have a workspace. Fill them in (and confirm the exact Opus 4.6 endpoint name
> in your workspace) when you're ready to actually chat.

## Run it

```bash
cd yt-demo
export OPENAI_API_KEY=...        # your (rotated) OpenAI key; do NOT commit it
unset OPENAI_BASE_URL            # ensure the marketer hits OpenAI, not a gateway
# optional, for live chatbot inference:
export DATABRICKS_HOST=https://<workspace>.cloud.databricks.com
export DATABRICKS_TOKEN=...

omnigent run .
```

Then ask the orchestrator to **"build the project and make the marketing
assets."** It dispatches the `coder`, then the `marketer` for **proposed
directions**, and **pauses for you to approve** a title + angle. After you
choose, it produces the finals and — **approving the gate cards** — persists
them. When it finishes you'll have:

- `app/` — the Streamlit chatbot (`streamlit run app/app.py`)
- `marketing/youtube_description.md` — title + description (GPT-authored)
- `marketing/repo_summary.md` — the repo explainer page (GPT-authored)

## Notes

- **Enforced approval gate:** `config.yaml` attaches `ask_on_os_tools` to the
  orchestrator, so persisting each deliverable requires a human approval card.
- **Why `gpt-4o` is pinned on the marketer:** two reasons. (1) The
  `openai-agents` harness treats an *unpinned* model as a Databricks model and
  would route to the Databricks gateway; a non-`databricks-` id keeps it on real
  OpenAI. (2) `gpt-4o` is a **non-reasoning** model, so it avoids the
  reasoning-item `function_call` 400 that crashes the harness across tool-call
  turns (the marketer's one tool call is reading the README).
- **The marketer is text-only:** it proposes and authors copy in its reply; the
  orchestrator persists those bytes. Creative content is 100% GPT.
- **Opus 4.6 is the app's runtime model**, not a harness model — the Streamlit
  app calls the Databricks Foundation Model serving endpoint directly via the
  OpenAI-compatible API.
- No secrets are committed: every credential is read from the environment.
