<div align="center">

```
███████╗██████╗ ███████╗███████╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗
██╔════╝██╔══██╗██╔════╝██╔════╝    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
█████╗  ██████╔╝█████╗  █████╗      ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   
██╔══╝  ██╔══██╗██╔══╝  ██╔══╝      ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   
██║     ██║  ██║███████╗███████╗    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   
╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   
```

**A free, open-source terminal coding agent — Claude Code-style, powered by [z.ai](https://z.ai)'s free GLM APIs.**

[Live site](https://freeagent-five.vercel.app) · [Report issue](https://github.com/vasilysahrai/freeagent/issues) · [MIT license](LICENSE)

</div>

---

`FreeAgent` gives you an interactive AI pair-programmer in your terminal that can read and edit your code, run shell commands, and ship projects to GitHub and Vercel — all driven by a free LLM backend so it doesn't cost a cent to use.

## Why this exists

Tools like Claude Code, Cursor, and Aider have reset the expectation for what a developer CLI should feel like. But most of them are paid or gated. `FreeAgent` brings the same loop — natural-language requests, streamed reasoning, tool-calling, automated shipping — on top of a genuinely free model tier from z.ai so anyone can try agentic coding without paying.

---

## Features

- **Interactive REPL** with slash commands (`/help`, `/clear`, `/model`, `/cwd`).
- **Tool-using agent loop** with OpenAI-style function calling.
- **File tools** — `read_file`, `write_file`, `edit_file`, `list_dir`, `grep`.
- **Shell tool** — arbitrary commands with captured output and exit codes.
- **GitHub integration** — create a public repo and push your workspace in one call (via the `gh` CLI).
- **Vercel integration** — deploy the current directory in one call (via the `vercel` CLI).
- **One-shot mode** — `freeagent -p "add a CI workflow"` for scripting.
- **Workspace sandboxing** — file tools refuse paths that escape the project root.
- **Rich terminal UI** — Claude Code-inspired panels, syntax highlighting, tool-call badges.
- **Bring-your-own-model** — swap between z.ai (free cloud), Ollama + Qwen3.6-35B-A3B (local, private), or any OpenAI-compatible API with one env var.

---

## Install

Requires Python ≥ 3.9.

```bash
pip install git+https://github.com/vasilysahrai/freeagent.git
```

Or clone and install in editable mode:

```bash
git clone https://github.com/vasilysahrai/freeagent.git
cd freeagent
pip install -e .
```

---

## Configure

FreeAgent ships with three provider presets. Pick whichever one you want — the CLI, tool loop, and prompts are identical across all three.

### Option A — z.ai (default, free cloud)

1. Grab a free API key at **[z.ai](https://z.ai)**.
2. Export it (or put it in a `.env` file in your project or `~/.freeagent/.env`):

```bash
export ZAI_API_KEY=your_key_here
```

That's it — run `freeagent` and you're on `glm-4.5-flash` for free.

### Option B — Ollama + Qwen3.6-35B-A3B (local, no key, no cost)

Prefer running models locally? FreeAgent talks to [Ollama](https://ollama.com)'s OpenAI-compatible endpoint out of the box, so you can drive it with **Qwen3.6-35B-A3B** (a Mixture-of-Experts model — 35B total parameters, only ~3B active per token, so it runs on a single workstation GPU or a beefy Mac).

```bash
# 1. install and start Ollama
brew install ollama            # or see https://ollama.com/download
ollama serve &

# 2. pull the Qwen3.6 MoE model
ollama pull qwen3.6:35b-a3b

# 3. point FreeAgent at it
export FREEAGENT_PROVIDER=ollama
freeagent
```

Want a different local model? Pull it with `ollama pull <name>` and set `FREEAGENT_MODEL=<name>`.

### Option C — any OpenAI-compatible API

```bash
export FREEAGENT_PROVIDER=openai
export OPENAI_API_KEY=sk-...
export FREEAGENT_MODEL=gpt-4o-mini   # optional, this is the default
freeagent
```

### Environment variables

| Variable              | Default                              | Notes                                                        |
| --------------------- | ------------------------------------ | ------------------------------------------------------------ |
| `FREEAGENT_PROVIDER`  | `zai`                                | One of `zai`, `ollama`, `openai`.                            |
| `FREEAGENT_MODEL`     | provider-specific                    | Any chat model id supported by the active provider.          |
| `FREEAGENT_BASE_URL`  | provider-specific                    | Override the OpenAI-compatible base URL.                     |
| `ZAI_API_KEY`         | —                                    | Key for `zai` provider.                                      |
| `OPENAI_API_KEY`      | —                                    | Key for `openai` provider.                                   |

Defaults per provider:

| Provider  | Base URL                          | Default model        |
| --------- | --------------------------------- | -------------------- |
| `zai`     | `https://api.z.ai/api/paas/v4`    | `glm-4.5-flash`      |
| `ollama`  | `http://localhost:11434/v1`       | `qwen3.6:35b-a3b`    |
| `openai`  | `https://api.openai.com/v1`       | `gpt-4o-mini`        |

For the GitHub and Vercel tools you'll also want the `gh` and `vercel` CLIs installed and authenticated.

---

## Use it

Start an interactive session in the directory you want the agent to work on:

```bash
cd path/to/project
freeagent
```

Then just talk to it:

```
› read pyproject.toml and add a lint target to the dev dependencies
› write a pytest that covers the login route, run it, and fix anything red
› ship this to a new public GitHub repo called quickstart-bot, then deploy to Vercel
```

Or run a single prompt and exit:

```bash
freeagent -p "summarise what this codebase does"
```

---

## How it works

```
┌──────────┐    messages     ┌──────────┐
│   you    │ ─────────────▶ │ FreeAgent│
└──────────┘                 │          │
      ▲                      │          │
      │   rendered output    │          │ ── tool_calls ──▶  [files] [bash] [grep] [gh] [vercel]
      │                      │          │ ◀── results ────
      │                      └────┬─────┘
      │                           │ chat
      │                           ▼
      │                    ┌─────────────┐
      └────────────────────│  z.ai GLM   │
                           └─────────────┘
```

Every turn the agent sends the conversation + a JSON schema for each tool to z.ai, receives either a natural-language reply or a set of tool calls, executes them locally, appends the results, and loops until the model is done.

---

## Project layout

```
freeagent/
├── freeagent/
│   ├── cli.py         # argparse + REPL
│   ├── agent.py       # tool-calling loop
│   ├── llm.py         # z.ai chat client
│   ├── config.py      # env/key loading
│   ├── ui.py          # rich terminal rendering
│   └── tools/         # read/write/edit/list/grep/bash/github/vercel
├── website/           # Vercel-deployed landing page
├── pyproject.toml
└── README.md
```

---

## Tech stack

- **Python 3.9+**
- **OpenAI Python SDK** — pointed at any OpenAI-compatible endpoint
- **Rich** — terminal rendering
- **prompt_toolkit** — input editing + history
- **Pluggable LLM backends** — z.ai GLM (default, free tier), Ollama (local, e.g. Qwen3.6-35B-A3B), or any OpenAI-compatible API
- **GitHub CLI** and **Vercel CLI** — shell-tool-powered integrations

---

## Skills demonstrated

Building this required:

- Designing an end-to-end **AI agent loop** with tool-calling, conversation state, and an extensible tool registry.
- Targeting an **OpenAI-compatible API** from a third-party provider (z.ai) and abstracting the client cleanly.
- Shipping a real, polished **Python CLI** — argparse, rich rendering, prompt_toolkit REPL, persistent history, slash commands.
- Writing **safe file operations** with workspace sandboxing and sensible size limits.
- Integrating with **real developer tooling** (`gh`, `vercel`, shell) from an LLM-driven control flow.
- Publishing an **open-source** project — MIT license, documentation, contributor-friendly structure, deployed docs site.

---

## Contributing

Issues and PRs welcome. If you add a tool, drop it in `freeagent/tools/` and register it in `freeagent/tools/registry.py`. Run `python -m compileall freeagent` to sanity-check.

---

## License

[MIT](LICENSE) — do whatever you want.
