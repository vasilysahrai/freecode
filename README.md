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

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/vasilysahrai/freeagent/main/install.ps1 | iex
```

Both installers detect Python, prefer `pipx`, and warn if the resulting
binary isn't on `PATH`.

---

## Pick a model

```sh
freeagent --list-models       # full catalog with free/paid/local tags
freeagent --list-providers
freeagent --list-keys         # which provider keys you have set
freeagent --deps              # gh / vercel / git availability
```

### Free (no per-token cost)

| Provider | Model | Notes |
| --- | --- | --- |
| **z.ai** | `glm-4.5-flash` | Free tier. Solid default. |
| **Groq** | `llama-3.3-70b-versatile` | Free, very fast, rate-limited. |
| **Groq** | `deepseek-r1-distill-llama-70b` | Free reasoning model. |
| **OpenRouter** | `deepseek/deepseek-r1:free` | Free `:free` route. |
| **Google Gemini** | `gemini-2.5-flash` | Free quota in AI Studio. |

### Local (zero cost, your hardware)

`ollama pull qwen2.5-coder:7b` — runs on most laptops with 16 GB RAM.

### Paid (frontier)

OpenAI `gpt-5` / `gpt-4o`, Anthropic `claude-opus-4-5` / `claude-sonnet-4-5`,
Google `gemini-2.5-pro`, xAI `grok-3`, Mistral `mistral-large-latest`,
z.ai `glm-4.6`.

---

## Configure

Set whichever key you actually plan to use, in your shell rc or in
`~/.freeagent/.env`:

```sh
export ZAI_API_KEY=...        # free        — https://z.ai
export GROQ_API_KEY=...       # free tier   — https://console.groq.com/keys
export OPENROUTER_API_KEY=... # free routes — https://openrouter.ai/keys
export GEMINI_API_KEY=...     # free quota  — https://aistudio.google.com/app/apikey
# Paid:
export OPENAI_API_KEY=...
export ANTHROPIC_API_KEY=...
```

Pick a provider/model — three equivalent ways:

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

---

## Use it

```sh
cd ~/your-project
freeagent
```

The REPL has a Claude Code-style status bar showing the active provider,
model, workspace, and permission mode. Type natural language and the agent
reads, edits, and runs.

```
›  add a dark-mode toggle to the React app and run the build
```

### Permissions

Destructive tools — `bash`, `write_file`, `edit_file`, `github_create_repo`,
`github_create_pr`, `vercel_deploy` — prompt for confirmation by default:

```
╭─ permission required ──────────────────────────╮
│ FreeAgent wants to run bash                    │
│   command=npm test                             │
╰────────────────────────────────────────────────╯
  [y] yes once · [a] always for this session · [n] no  >
```

To skip prompts entirely:

```sh
freeagent --dangerously-skip-permissions    # or --yolo
```

Or in the REPL:

```
›  /bypass on
```

The status bar turns red so you remember it's on.

### When your key runs out

If the API returns 401 / 429 / quota-exceeded mid-turn, FreeAgent shows the
error and asks for a new key inline. Paste it (input is hidden) and the
turn retries automatically. You can persist the new key:

```
›  /save-key      # writes to ~/.freeagent/.env
```

Other key commands:

```
›  /keys          # list which providers have keys configured
›  /key <value>   # replace the active provider's key for this session
```

### GitHub & Vercel

FreeAgent uses your local `gh` and `vercel` CLIs (so it inherits your
existing auth). Tools available to the agent:

- **GitHub:** `github_status`, `github_list_repos`, `github_create_repo`
  (defaults to **private**), `github_create_pr`
- **Vercel:** `vercel_status`, `vercel_list_projects`, `vercel_deploy`
  (preview or `prod=true`), `vercel_logs`

Quick checks from the REPL:

```
›  /gh            # gh auth status
›  /vercel        # vercel whoami
›  /deps          # see which CLIs are installed
```

### Slash commands

| | |
| --- | --- |
| `/help` | Show the command list. |
| `/models` / `/catalog` | List models for the current provider / everything. |
| `/provider <id>` | Switch provider live. |
| `/model <id>` | Switch model live. |
| `/key <value>` / `/save-key` / `/keys` | Manage API keys. |
| `/bypass on`/`off` (alias `/yolo`) | Skip permission prompts. |
| `/stream on`/`off` | Toggle token streaming. |
| `/verbose on`/`off` | Always print full tool output. |
| `/gh` / `/vercel` / `/deps` | Check external CLI status. |
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
├── cli.py        argparse + REPL + slash commands + bottom toolbar
├── agent.py      message loop, streaming, permission gate, key recovery
├── llm.py        OpenAI-compatible client with retries + typed errors
├── config.py     PROVIDERS + CATALOG (free/paid/local) + env helpers
├── ui.py         rich-based renderer with ⏺ markers + permission panel
└── tools/        files, shell, search, github, vercel
```

Every provider is one entry in `PROVIDERS`; every recommended model is one
row in `CATALOG`. Adding a new one is a few lines.

---

## License

MIT.
