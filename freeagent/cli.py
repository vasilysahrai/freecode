"""Command-line entry point."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from . import __version__, ui
from .agent import Agent
from .config import CATALOG, PROVIDERS, Config, models_for


def _history_path() -> Path:
    home = Path.home() / ".freeagent"
    home.mkdir(parents=True, exist_ok=True)
    return home / "history"


def _print_models(provider_id: str) -> None:
    rows = [(m.provider, m.model, m.tier, m.notes) for m in models_for(provider_id)]
    if not rows:
        ui.info(f"no models registered for {provider_id} (still works — pass any model id).")
        return
    ui.models_table(rows, title=f"Models for {PROVIDERS[provider_id].label}")


def _print_catalog() -> None:
    rows = [(m.provider, m.model, m.tier, m.notes) for m in CATALOG]
    ui.models_table(rows, title="Full FreeAgent catalog")


def _switch_provider(agent: Agent, prov_id: str) -> None:
    prov_id = prov_id.strip().lower()
    if prov_id not in PROVIDERS:
        ui.error(f"unknown provider {prov_id!r}. Choices: {', '.join(PROVIDERS)}.")
        return
    p = PROVIDERS[prov_id]
    agent.config.provider = prov_id
    agent.config.base_url = p.base_url
    agent.config.model = p.default_model
    if p.env_key:
        agent.config.api_key = os.getenv(p.env_key, "")
    elif not p.needs_key:
        agent.config.api_key = "local-no-key"
    try:
        agent.reload_client()
        ui.info(f"now using {p.label} · {agent.config.model}")
    except Exception as e:  # noqa: BLE001
        ui.error(str(e))


def _switch_model(agent: Agent, model_id: str) -> None:
    agent.config.model = model_id.strip()
    ui.info(f"model → {agent.config.model}")


def _set_key(agent: Agent, value: str) -> None:
    agent.config.api_key = value.strip()
    try:
        agent.reload_client()
        ui.info("api key set for this session.")
    except Exception as e:  # noqa: BLE001
        ui.error(str(e))


def _toggle_stream(agent: Agent, value: str) -> None:
    v = value.strip().lower()
    if v in ("on", "true", "1", "yes"):
        agent.config.stream = True
    elif v in ("off", "false", "0", "no"):
        agent.config.stream = False
    else:
        ui.error("usage: /stream on|off")
        return
    ui.info(f"streaming {'on' if agent.config.stream else 'off'}")


def _handle_slash(cmd: str, agent: Agent) -> bool:
    cmd = cmd.strip()
    if not cmd.startswith("/"):
        return False

    head, _, rest = cmd.partition(" ")
    rest = rest.strip()

    if head in ("/exit", "/quit"):
        raise EOFError
    if head == "/help":
        ui.help_table()
        return True
    if head == "/clear":
        agent.reset()
        ui.info("conversation cleared.")
        return True
    if head == "/cwd":
        ui.info(f"workspace: {agent.config.workspace}")
        return True
    if head == "/model":
        if not rest:
            ui.info(
                f"provider: {agent.config.provider}  ·  "
                f"model: {agent.config.model}  ·  "
                f"base: {agent.config.base_url}"
            )
        else:
            _switch_model(agent, rest)
        return True
    if head == "/provider":
        if not rest:
            ui.info(f"provider: {agent.config.provider} ({PROVIDERS[agent.config.provider].label})")
            ui.info("choices: " + ", ".join(PROVIDERS))
        else:
            _switch_provider(agent, rest)
        return True
    if head == "/key":
        if not rest:
            ui.error("usage: /key <value>")
        else:
            _set_key(agent, rest)
        return True
    if head == "/models":
        _print_models(agent.config.provider)
        return True
    if head == "/catalog":
        _print_catalog()
        return True
    if head == "/stream":
        if not rest:
            ui.info(f"streaming {'on' if agent.config.stream else 'off'}")
        else:
            _toggle_stream(agent, rest)
        return True

    ui.error(f"unknown command: {head} — type /help")
    return True


def _repl(agent: Agent) -> None:
    ui.banner()
    p = PROVIDERS[agent.config.provider]
    ui.info(
        f"{p.label} · {agent.config.model}  ·  workspace {agent.config.workspace}  "
        "·  /help for commands, ctrl-d to exit"
    )
    ui.rule()

    session: PromptSession = PromptSession(history=FileHistory(str(_history_path())))
    while True:
        try:
            line = session.prompt("› ")
        except (EOFError, KeyboardInterrupt):
            ui.info("bye.")
            return
        line = line.strip()
        if not line:
            continue
        if line.startswith("/"):
            try:
                if _handle_slash(line, agent):
                    continue
            except EOFError:
                ui.info("bye.")
                return
        try:
            agent.turn(line)
        except KeyboardInterrupt:
            ui.info("(interrupted)")
        except Exception as e:  # noqa: BLE001
            ui.error(str(e))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="freeagent",
        description="FreeAgent — an open-source terminal coding agent.",
    )
    parser.add_argument("-p", "--prompt", help="Run a single prompt and exit.")
    parser.add_argument("-C", "--cwd", help="Workspace dir (default: cwd).")
    parser.add_argument("--provider", help="Provider id (zai, groq, openrouter, ollama, openai, …).")
    parser.add_argument("--model", help="Model id.")
    parser.add_argument("--no-stream", action="store_true", help="Disable token streaming.")
    parser.add_argument("--list-models", action="store_true", help="List the model catalog and exit.")
    parser.add_argument("--list-providers", action="store_true", help="List providers and exit.")
    parser.add_argument("--version", action="version", version=f"freeagent {__version__}")
    args = parser.parse_args(argv)

    if args.list_providers:
        for p in PROVIDERS.values():
            print(f"{p.id:11}  {p.tier:6}  {p.label}  —  {p.description}")
        return 0
    if args.list_models:
        for m in CATALOG:
            print(f"{m.tier:6}  {m.provider:11}  {m.model:42}  {m.notes}")
        return 0

    try:
        config = Config.load(
            workspace=Path(args.cwd) if args.cwd else None,
            provider=args.provider,
            model=args.model,
        )
        if args.no_stream:
            config.stream = False
        agent = Agent(config)
    except Exception as e:  # noqa: BLE001
        ui.error(str(e))
        return 1

    if args.prompt:
        agent.turn(args.prompt)
    else:
        _repl(agent)
    return 0


if __name__ == "__main__":
    sys.exit(main())
