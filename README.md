# FreeAgent

An open-source terminal coding agent. One CLI, swappable models — free (z.ai
GLM-4.5-flash, Groq, OpenRouter `:free` routes, local Ollama) or paid frontier
(GPT-5, Claude Opus 4.5, Gemini 2.5 Pro). It reads and edits your code, runs
commands, and ships projects to GitHub and Vercel.

MIT licensed. Built by [Vasily Sahrai](https://github.com/vasilysahrai).

---

## Install

### macOS & Linux

```sh
curl -fsSL https://raw.githubusercontent.com/vasilysahrai/freeagent/main/install.sh | bash
```

Or with pipx:

```sh
pipx install git+https://github.com/vasilysahrai/freeagent.git
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/vasilysahrai/freeagent/main/install.ps1 | iex
```

Or with pipx:

```powershell
pipx install "git+https://github.com/vasilysahrai/freeagent.git"
```

Both installers detect Python, prefer `pipx`, fall back to `pip --user`, and
warn if the resulting binary isn't on `PATH`.

---

## Pick a model

```sh
freeagent --list-models       # full catalog with free/paid/local tags
freeagent --list-providers
```

### Free (no per-token cost)

| Provider | Model | Notes |
| --- | --- | --- |
| **z.ai** | `glm-4.5-flash` | Free tier. Solid default. |
| **Groq** | `llama-3.3-70b-versatile` | Free tier, very fast, rate-limited. |
| **Groq** | `deepseek-r1-distill-llama-70b` | Free reasoning model. |
| **OpenRouter** | `deepseek/deepseek-r1:free` | Free `:free` route. |
| **OpenRouter** | `meta-llama/llama-3.3-70b-instruct:free` | Free route. |
| **Google Gemini** | `gemini-2.5-flash` | Free quota in AI Studio. |

### Local (zero cost, your hardware)

| Model | Disk | Notes |
| --- | --- | --- |
| `qwen2.5-coder:7b` | ~5 GB | Most laptops with 16 GB RAM. |
| `qwen2.5-coder:32b` | ~20 GB | 32 GB+ unified memory or a 24 GB GPU. |
| `llama3.1:8b` | ~5 GB | Solid generalist. |

### Paid (frontier)

| Provider | Model |
| --- | --- |
| OpenAI | `gpt-4o-mini`, `gpt-4o`, `gpt-5` |
| Anthropic | `claude-sonnet-4-5`, `claude-opus-4-5` |
| Google | `gemini-2.5-pro` |
| xAI | `grok-3` |
| Mistral | `mistral-large-latest` |
| z.ai | `glm-4.6` |

---

## Configure

Set whichever key you actually plan to use. Keep it in your shell rc, or in
`~/.freeagent/.env` / `./.env`:

```sh
export ZAI_API_KEY=...        # free GLM-4.5-flash · https://z.ai
export GROQ_API_KEY=...        # free tier        · https://console.groq.com/keys
export OPENROUTER_API_KEY=...  # free routes      · https://openrouter.ai/keys
export GEMINI_API_KEY=...      # free quota       · https://aistudio.google.com/app/apikey
export OPENAI_API_KEY=...      # paid             · https://platform.openai.com/api-keys
export ANTHROPIC_API_KEY=...   # paid             · https://console.anthropic.com
```

Then pick a provider/model — three equivalent ways:

```sh
# 1) per-invocation flags
freeagent --provider groq --model llama-3.3-70b-versatile

# 2) env vars
export FREEAGENT_PROVIDER=groq
export FREEAGENT_MODEL=llama-3.3-70b-versatile
freeagent

# 3) live, inside the REPL
›  /provider groq
›  /model llama-3.3-70b-versatile
```

For Ollama, no key is needed:

```sh
ollama pull qwen2.5-coder:7b
freeagent --provider ollama --model qwen2.5-coder:7b
```

---

## Use it

```sh
cd ~/your-project
freeagent
```

A REPL opens. Type natural language; the agent reads files, edits them, and
runs commands.

```
›  add a dark-mode toggle to the React app and run the build
```

Slash commands:

| | |
| --- | --- |
| `/help` | Show this list. |
| `/models` | List models for the current provider. |
| `/catalog` | List the entire built-in catalog. |
| `/provider <id>` | Switch provider live. |
| `/model <id>` | Switch model live. |
| `/key <value>` | Replace the API key for this session. |
| `/stream on`/`off` | Toggle token streaming. |
| `/clear` | Reset the conversation. |
| `/cwd` | Print the workspace dir. |
| `/exit` | Quit (ctrl-d also works). |

One-shot:

```sh
freeagent -p "write a tiny FastAPI app and deploy it to Vercel"
```

---

## What's inside

```
freeagent/
├── cli.py        argparse + REPL + slash commands
├── agent.py      message loop, streaming, tool dispatch
├── llm.py        OpenAI-compatible client with retries
├── config.py     PROVIDERS + CATALOG (free vs paid vs local)
├── ui.py         rich-based renderer
└── tools/        read_file · write_file · edit_file · list_dir
                  grep · bash · github_create_repo · vercel_deploy
```

The agent loop is straight OpenAI tool-calling. Every provider is one entry in
`PROVIDERS`; every recommended model is one row in `CATALOG`. Adding a new one
is a few lines.

---

## License

MIT.
