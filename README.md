<div align="center">

```
███████╗██████╗ ███████╗███████╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗
██╔════╝██╔══██╗██╔════╝██╔════╝    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
█████╗  ██████╔╝█████╗  █████╗      ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   
██╔══╝  ██╔══██╗██╔══╝  ██╔══╝      ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   
██║     ██║  ██║███████╗███████╗    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   
╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   
```

**A free, open-source terminal coding agent — Claude Code-style, with swappable LLM backends: free cloud (z.ai GLM), local (Ollama + Qwen3.6-35B-A3B), or any OpenAI-compatible API.**

[Live site](https://freeagent-five.vercel.app) · [Report issue](https://github.com/vasilysahrai/freeagent/issues) · [MIT license](LICENSE)

</div>

---

`FreeAgent` gives you an interactive AI pair-programmer in your terminal that can read and edit your code, run shell commands, and ship projects to GitHub and Vercel. You pick the brain: a genuinely free cloud model, a private local model running entirely on your own hardware, or any OpenAI-compatible API you already pay for. Same CLI, same tools, same prompt style — flip one environment variable.

## Why this exists

Tools like Claude Code, Cursor, and Aider have reset the expectation for what a developer CLI should feel like. But most of them are paid, gated, or locked to a single vendor. FreeAgent's goal is the opposite:

- **Free by default.** Point it at z.ai's free `glm-4.5-flash` tier and agentic coding costs you nothing.
- **Private when you want it.** Point it at Ollama and a capable open model like **Qwen3.6-35B-A3B** — your code, the conversation, and every tool call stay on your machine. No data leaves the laptop.
- **Frontier when you need it.** Point it at OpenAI, Anthropic-through-OpenAI-compat, Groq, Together, Fireworks, vLLM, or any other service that speaks the OpenAI chat-completions dialect.

The agent loop, the tool schemas, the REPL — none of that changes. Only the model on the other end does.

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

## Choosing a backend

All three providers plug into the same agent loop. Here's how to think about which one to use:

| Backend                     | Cost          | Privacy                 | Strongest at                           | Needs                                |
| --------------------------- | ------------- | ----------------------- | -------------------------------------- | ------------------------------------ |
| **z.ai GLM-4.5**            | Free          | Cloud (z.ai sees it)    | Fast everyday coding, try-it-in-30s    | Free z.ai account                    |
| **Ollama + Qwen3.6-35B-A3B**| $0 inference  | 100% local              | Private code, offline work, long sessions | Ollama + a capable GPU or Apple Silicon |
| **OpenAI / any compatible** | Pay per call  | Depends on vendor       | Frontier reasoning, tricky refactors   | Your own API key                     |

### About Qwen3.6-35B-A3B

Qwen3.6-35B-A3B is a **Mixture-of-Experts (MoE)** model from Alibaba's Qwen team. The name decodes as:

- **35B** — total parameters in the checkpoint.
- **A3B** — **A**ctive **3B**, i.e. only ~3 billion parameters fire on any given token.

In practice this means it's a frontier-class open model that runs with roughly the inference cost and latency of a 3B dense model, while carrying the knowledge capacity of a 35B one. It's particularly well-suited to FreeAgent because:

- **Strong tool-calling.** Qwen3 was trained with OpenAI-style function calling in mind, so the `tool_calls` field just works.
- **Long context.** Plenty of room for the running conversation, tool results, and large file reads.
- **Local = private.** The model weights live on your disk, Ollama runs the inference, FreeAgent talks to it over `localhost`. Nothing — not your code, not your prompts, not the tool results — ever leaves your machine.

**Hardware rule of thumb:** the MoE active-param count is what matters for throughput, but you still have to fit the full 35B in memory. In 4-bit quantization that's roughly **~22 GB** of VRAM/unified memory. An RTX 4090 (24 GB), an A6000, or an M-series Mac with 32 GB+ unified memory will run it comfortably. Smaller setup? Pick a smaller model — see the tip at the end of the Ollama section below.

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

z.ai hosts GLM-4.5, a strong general-purpose model, behind an OpenAI-compatible endpoint. The `glm-4.5-flash` tier is free at the time of writing — no credit card, no trial limit — which is why it's FreeAgent's default.

1. Grab a free API key at **[z.ai](https://z.ai)**.
2. Export it (or put it in a `.env` file in your project or `~/.freeagent/.env`):

```bash
export ZAI_API_KEY=your_key_here
```

3. Run `freeagent`. That's it.

You can swap the specific z.ai model with `FREEAGENT_MODEL=glm-4.5` (or any other model id z.ai exposes).

### Option B — Ollama + Qwen3.6-35B-A3B (local, no key, no cost, fully private)

This option runs the entire model on your own hardware. FreeAgent connects to [Ollama](https://ollama.com)'s built-in OpenAI-compatible server at `http://localhost:11434/v1`. No API keys, no sign-ups, no network calls to anyone but `localhost`.

```bash
# 1. install Ollama (Mac, Linux, and Windows installers available)
brew install ollama            # or see https://ollama.com/download

# 2. start the local server (leave this running in another terminal,
#    or add `brew services start ollama` on macOS)
ollama serve &

# 3. pull the Qwen3.6 MoE model — this is a one-time download of the weights
ollama pull qwen3.6:35b-a3b

# 4. tell FreeAgent which provider to talk to
export FREEAGENT_PROVIDER=ollama

# 5. use it exactly like before
freeagent
```

**What's happening under the hood.** Ollama exposes the Qwen3.6 model as a local OpenAI-compatible endpoint. FreeAgent doesn't know or care that the model is local — the OpenAI Python SDK just points at `localhost:11434/v1` instead of `api.z.ai`, and the same `chat.completions.create(...)` call with the same `tools` schema drives the same agent loop.

**Not enough VRAM for 35B?** Pull a smaller model and tell FreeAgent to use it:

```bash
# examples — pick one that fits your machine
ollama pull llama3.1:8b-instruct
ollama pull qwen2.5-coder:7b
ollama pull mistral-nemo:12b

export FREEAGENT_PROVIDER=ollama
export FREEAGENT_MODEL=qwen2.5-coder:7b
freeagent
```

Any Ollama model that supports tool-calling will work with the full FreeAgent agent loop, including `github_create_repo` and `vercel_deploy`.

### Option C — OpenAI, or any other OpenAI-compatible API

Because the OpenAI Python SDK is the transport layer, FreeAgent can drive any service that exposes the same chat-completions shape — OpenAI itself, Groq, Together, Fireworks, vLLM, LiteLLM, a locally-hosted proxy, you name it.

For OpenAI specifically:

```bash
export FREEAGENT_PROVIDER=openai
export OPENAI_API_KEY=sk-...
export FREEAGENT_MODEL=gpt-4o-mini   # optional, this is the default
freeagent
```

For something else, override the base URL and model explicitly:

```bash
export FREEAGENT_PROVIDER=openai               # just reuses the OPENAI_API_KEY slot
export OPENAI_API_KEY=your-other-vendor-key
export FREEAGENT_BASE_URL=https://api.groq.com/openai/v1
export FREEAGENT_MODEL=llama-3.1-70b-versatile
freeagent
```

If a vendor's endpoint doesn't match OpenAI's chat-completions dialect exactly, you may need to pick a different model that does — most big inference platforms support it today.

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
      ▲                      │          │── tool_calls ──▶ [files] [bash] [grep] [gh] [vercel]
      │    rendered output   │          │◀── results ────
      │                      └────┬─────┘
      │                           │ chat (OpenAI-compatible)
      │                           ▼
      │             ┌────────────────────────────┐
      └─────────────│   LLM backend (your pick)  │
                    │                            │
                    │  • z.ai   → GLM-4.5-flash  │
                    │  • ollama → qwen3.6 / …    │
                    │  • openai → gpt-4o-mini    │
                    │  • …any OpenAI-compat API  │
                    └────────────────────────────┘
```

Every turn FreeAgent sends the running conversation plus a JSON schema for each tool to whichever backend you've configured. The model replies with either natural language (and we stop) or a set of tool calls. FreeAgent executes those tools locally — reading/writing files inside the workspace, running shell commands, shelling out to `gh` or `vercel` — appends the results back into the conversation, and loops until the model is done.

The backend abstraction is dead simple: every provider is an entry in a `PROVIDERS` preset dict in `freeagent/config.py` (`base_url`, `default_model`, which env var holds the API key, whether a key is required). The OpenAI Python SDK handles the rest. Adding a new provider is one dict entry; no changes to the agent, tool registry, or prompts needed.

---

## Project layout

```
freeagent/
├── freeagent/
│   ├── cli.py         # argparse + REPL
│   ├── agent.py       # tool-calling loop
│   ├── llm.py         # OpenAI-compatible chat client (any backend)
│   ├── config.py      # provider presets + env/key loading
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
- Building a **pluggable provider layer** on top of the OpenAI Python SDK — one preset dict drives z.ai (free cloud), Ollama (local, including frontier MoE models like Qwen3.6-35B-A3B), and OpenAI-compatible vendors without touching the agent or tools.
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
