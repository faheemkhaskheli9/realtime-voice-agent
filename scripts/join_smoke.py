"""Manual connectivity smoke test against a real LiveKit server.

Requires LIVEKIT_URL / LIVEKIT_API_KEY / LIVEKIT_API_SECRET in the environment
and the `livekit` package installed. Connects a client, waits briefly, prints
the participant list (which should include the agent worker if it is running),
then disconnects.

    python scripts/join_smoke.py --identity test-client
"""

from __future__ import annotations

import argparse
import asyncio
import sys

# ruff: noqa: E402
sys.path.insert(0, "src")

from rtva.config import ConfigError, LiveKitConfig  # noqa: E402
from rtva.room import build_room_client  # noqa: E402


async def _main(identity: str, seconds: float) -> int:
    try:
        config = LiveKitConfig.from_env().require_configured()
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    config = LiveKitConfig(
        url=config.url,
        api_key=config.api_key,
        api_secret=config.api_secret,
        room_name=config.room_name,
        agent_identity=identity,
    )
    client = build_room_client(config)
    await client.connect()
    print(f"connected to {config.room_name!r} as {identity!r}")
    await asyncio.sleep(seconds)
    print("participants:", client.participants)
    await client.disconnect()
    print("disconnected")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--identity", default="test-client")
    parser.add_argument("--seconds", type=float, default=3.0)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(_main(args.identity, args.seconds)))
