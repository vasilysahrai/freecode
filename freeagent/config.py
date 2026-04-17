"""Runtime configuration — provider presets, API keys, model choice, workspace paths."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROVIDERS: dict[str, dict] = {
    "zai": {
        "base_url": "https://api.z.ai/api/paas/v4",
        "default_model": "glm-4.5-flash",
        "env_key": "ZAI_API_KEY",
        "needs_key": True,
        "signup": "https://z.ai",
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "default_model": "qwen3.6:35b-a3b",
        "env_key": None,
        "needs_key": False,
        "signup": "https://ollama.com/download",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "env_key": "OPENAI_API_KEY",
        "needs_key": True,
        "signup": "https://platform.openai.com/api-keys",
    },
}

DEFAULT_PROVIDER = "zai"


@dataclass
class Config:
    provider: str
    api_key: str
    base_url: str
    model: str
    workspace: Path

    @classmethod
    def load(cls, workspace: Path | None = None) -> "Config":
        load_dotenv(dotenv_path=Path.cwd() / ".env", override=False)
        load_dotenv(dotenv_path=Path.home() / ".freeagent" / ".env", override=False)

        provider = os.getenv("FREEAGENT_PROVIDER", DEFAULT_PROVIDER).lower().strip()
        if provider not in PROVIDERS:
            raise RuntimeError(
                f"Unknown provider '{provider}'. Supported: {', '.join(PROVIDERS)}."
            )
        preset = PROVIDERS[provider]

        base_url = (
            os.getenv("FREEAGENT_BASE_URL")
            or os.getenv("ZAI_BASE_URL")
            or preset["base_url"]
        )
        model = os.getenv("FREEAGENT_MODEL", preset["default_model"])

        api_key = ""
        if preset["env_key"]:
            api_key = os.getenv(preset["env_key"], "")
        if not api_key:
            api_key = os.getenv("ZAI_API_KEY") or os.getenv("Z_API_KEY") or ""
        if not api_key and not preset["needs_key"]:
            api_key = "local-no-key"

        ws = (workspace or Path.cwd()).resolve()
        return cls(
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            model=model,
            workspace=ws,
        )

    def require_key(self) -> None:
        preset = PROVIDERS.get(self.provider, {})
        if not preset.get("needs_key", True):
            return
        if self.api_key and self.api_key != "local-no-key":
            return
        env_key = preset.get("env_key") or "ZAI_API_KEY"
        signup = preset.get("signup", "")
        raise RuntimeError(
            f"No API key found for provider '{self.provider}'. "
            f"Set {env_key} in your environment or in a .env file."
            + (f" Sign up at {signup}." if signup else "")
        )
