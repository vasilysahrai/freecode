"""Terminal rendering — Claude Code-ish: status toolbar, ⏺ tool markers,
permission panel, inline key prompt."""

from __future__ import annotations

import getpass
import sys
from typing import Iterable

from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


console = Console()


# ── one-shot prints ──────────────────────────────────────────────────────
def banner(provider_label: str, model: str, workspace, bypass: bool) -> None:
    head = Text()
    head.append("FreeAgent  ", style="bold")
    head.append(provider_label, style="bold")
    head.append("  ·  ", style="dim")
    head.append(model)
    sub = Text(str(workspace), style="dim")
    body = Group(head, sub)
    console.print(
        Panel(
            body,
            border_style="yellow" if bypass else "white",
            padding=(0, 2),
            title=("[bold red]BYPASS PERMISSIONS[/bold red]" if bypass else None),
        )
    )


def assistant(text: str) -> None:
    if not text.strip():
        return
    console.print(Markdown(text))


# ── streaming tokens ─────────────────────────────────────────────────────
def assistant_open() -> None:
    console.print("⏺ ", end="", style="bold green", highlight=False, markup=False)


def stream_token(t: str) -> None:
    console.print(t, end="", soft_wrap=True, highlight=False, markup=False)


def assistant_close() -> None:
    console.print("")  # newline


# ── tool calls ───────────────────────────────────────────────────────────
def tool_call(name: str, args_preview: str) -> None:
    h = Text()
    h.append("⏺ ", style="cyan")
    h.append(name, style="bold")
    if args_preview:
        h.append(f"({args_preview})", style="dim")
    console.print(h)


def tool_result(name: str, body: str, ok: bool, summary: str | None = None,
                 max_lines: int = 12, verbose: bool = False) -> None:
    """Compact result line + optional dim panel for large/error output."""
    line = Text()
    line.append("  ⎿ ", style="dim")
    if not ok:
        line.append("error", style="bold red")
        line.append(": ", style="dim")
        first = body.strip().splitlines()[0] if body.strip() else "(no output)"
        if len(first) > 120:
            first = first[:120] + "…"
        line.append(first)
        console.print(line)
        return

    if summary:
        line.append(summary, style="dim")
    else:
        n = len(body.splitlines()) if body else 0
        line.append(f"{n} line{'s' if n != 1 else ''}", style="dim")
    console.print(line)

    if verbose and body.strip():
        lines = body.splitlines()
        truncated = False
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            truncated = True
        content = "\n".join(lines)
        if truncated:
            content += f"\n… ({len(body.splitlines()) - max_lines} more lines)"
        console.print(
            Panel(
                content,
                border_style="grey39",
                padding=(0, 1),
                title=f"[dim]{name}[/dim]",
            )
        )


# ── small helpers ────────────────────────────────────────────────────────
def info(text: str) -> None:
    console.print(f"[dim]{text}[/dim]")


def warn(text: str) -> None:
    console.print(f"[yellow]! {text}[/yellow]")


def error(text: str) -> None:
    console.print(f"[bold red]error[/bold red] {text}")


def rule() -> None:
    console.rule(style="grey23")


# ── permission prompt ────────────────────────────────────────────────────
def permission_panel(name: str, args_preview: str) -> None:
    body = Text()
    body.append("FreeAgent wants to run ", style="dim")
    body.append(name, style="bold yellow")
    if args_preview:
        body.append("\n  ", style="dim")
        body.append(args_preview, style="cyan")
    console.print(
        Panel(
            body,
            border_style="yellow",
            title="[bold]permission required[/bold]",
            padding=(0, 1),
        )
    )


def request_permission(name: str, args_preview: str) -> str:
    """Returns 'allow_once' | 'allow_session' | 'deny'."""
    permission_panel(name, args_preview)
    while True:
        try:
            ans = input(
                "  [y] yes once · [a] always for this session · [n] no  > "
            ).strip().lower()
        except (EOFError, KeyboardInterrupt):
            console.print("")
            return "deny"
        if ans in ("y", "yes", ""):
            return "allow_once"
        if ans in ("a", "always"):
            return "allow_session"
        if ans in ("n", "no"):
            return "deny"
        warn("answer y, a, or n")


# ── inline API-key prompt ────────────────────────────────────────────────
def prompt_for_new_key(provider_label: str, env_key: str, signup: str) -> str | None:
    """Ask the user for a fresh API key when the current one fails. Returns the
    new key, or None if the user bails."""
    console.print(
        Panel(
            Text.from_markup(
                f"[bold]API key issue with {provider_label}[/bold]\n"
                f"Likely 401, quota, or rate limit.\n\n"
                f"Paste a new key for [bold]{env_key}[/bold] (or press Enter to abort).\n"
                f"Get one: {signup}"
            ),
            border_style="red",
            padding=(0, 1),
        )
    )
    try:
        new = getpass.getpass("  new key (hidden) > ").strip()
    except (EOFError, KeyboardInterrupt):
        console.print("")
        return None
    return new or None


def ask_save_key() -> bool:
    try:
        ans = input("  save this key to ~/.freeagent/.env? [y/N] > ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        console.print("")
        return False
    return ans in ("y", "yes")


# ── tables ───────────────────────────────────────────────────────────────
def help_table() -> None:
    rows = [
        ("/help",            "show this help"),
        ("/models",          "list models for the current provider"),
        ("/catalog",         "list every model FreeAgent knows about"),
        ("/provider <id>",   "switch provider live"),
        ("/model <id>",      "switch model live"),
        ("/key <value>",     "replace the API key for this session"),
        ("/save-key",        "persist the current key to ~/.freeagent/.env"),
        ("/keys",            "list which providers have keys configured"),
        ("/bypass on|off",   "skip per-tool permission prompts (alias /yolo)"),
        ("/stream on|off",   "toggle token streaming"),
        ("/verbose on|off",  "always print full tool output"),
        ("/gh",              "show GitHub CLI status (auth + user)"),
        ("/vercel",          "show Vercel CLI status (auth + team)"),
        ("/clear",           "reset the conversation"),
        ("/cwd",             "print the working directory"),
        ("/exit",            "leave the session (ctrl-d also works)"),
    ]
    table = Table(show_header=False, border_style="grey23", box=None)
    table.add_column("cmd", style="bold")
    table.add_column("desc", style="dim")
    for c, d in rows:
        table.add_row(c, d)
    console.print(table)


def models_table(rows: list[tuple[str, str, str, str]], title: str) -> None:
    """rows: (provider, model, tier, notes)"""
    table = Table(title=title, border_style="grey23")
    table.add_column("provider", style="bold")
    table.add_column("model")
    table.add_column("tier")
    table.add_column("notes", style="dim")
    for provider, model, tier, notes in rows:
        tier_style = {"free": "green", "local": "cyan", "paid": "yellow"}.get(tier, "")
        table.add_row(provider, model, f"[{tier_style}]{tier}[/{tier_style}]", notes)
    console.print(table)


def keys_table(rows: list[tuple[str, str, bool, str]]) -> None:
    """rows: (provider_id, env_key_or_dash, has_key, signup)"""
    table = Table(title="API keys detected", border_style="grey23")
    table.add_column("provider", style="bold")
    table.add_column("env var")
    table.add_column("status")
    table.add_column("signup", style="dim")
    for pid, env_key, has, signup in rows:
        status = "[green]✓ set[/green]" if has else "[red]– missing[/red]"
        table.add_row(pid, env_key, status, signup)
    console.print(table)


def deps_status(rows: list[tuple[str, bool, str]]) -> None:
    """rows: (label, ok, detail)"""
    table = Table(title="External CLI status", border_style="grey23", show_header=False)
    table.add_column("dep", style="bold")
    table.add_column("ok")
    table.add_column("detail", style="dim")
    for label, ok, detail in rows:
        mark = "[green]✓[/green]" if ok else "[red]✗[/red]"
        table.add_row(label, mark, detail)
    console.print(table)
