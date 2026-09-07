"""LiveKit connection configuration.

Loaded from the environment (``.env`` in local dev). Two modes:

* **connect mode** — ``url`` + ``api_key`` + ``api_secret`` all present; the
  worker uses the real LiveKit client.
* **dry-run mode** — credentials absent; the worker runs against an in-process
  fake so the pipeline is demoable/testable with no server.

Rule 7 (portfolio robustness): a *partially* configured environment (e.g. a
URL but no secret) is a hard error, not a silent fall-through to dry-run —
that almost always means a misconfigured deployment.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

_ENV_URL = "LIVEKIT_URL"
_ENV_KEY = "LIVEKIT_API_KEY"
_ENV_SECRET = "LIVEKIT_API_SECRET"


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class LiveKitConfig:
    url: str | None
    api_key: str | None
    api_secret: str | None
    room_name: str = "voice-agent-dev"
    agent_identity: str = "agent-worker"

    @property
    def is_configured(self) -> bool:
        return bool(self.url and self.api_key and self.api_secret)

    def require_configured(self) -> "LiveKitConfig":
        if not self.is_configured:
            raise ConfigError(
                "LiveKit credentials are incomplete; set "
                f"{_ENV_URL}, {_ENV_KEY}, {_ENV_SECRET}"
            )
        return self

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "LiveKitConfig":
        src = os.environ if env is None else env
        url = src.get(_ENV_URL) or None
        key = src.get(_ENV_KEY) or None
        secret = src.get(_ENV_SECRET) or None

        provided = [p for p in (url, key, secret) if p]
        if provided and len(provided) != 3:
            raise ConfigError(
                "partial LiveKit configuration: set all of "
                f"{_ENV_URL}, {_ENV_KEY}, {_ENV_SECRET} or none of them"
            )

        return cls(
            url=url,
            api_key=key,
            api_secret=secret,
            room_name=src.get("LIVEKIT_ROOM", "voice-agent-dev"),
            agent_identity=src.get("LIVEKIT_AGENT_IDENTITY", "agent-worker"),
        )
