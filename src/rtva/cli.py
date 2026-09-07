"""Run the agent worker: ``python -m rtva.cli``.

Reads LiveKit settings from the environment. With no credentials it runs in
dry-run mode against the in-process fake room so the entrypoint is always
launchable. Ctrl-C stops it cleanly.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import signal

from .config import ConfigError, LiveKitConfig
from .worker import AgentWorker


async def _run(max_runtime: float | None) -> int:
    try:
        config = LiveKitConfig.from_env()
    except ConfigError as exc:
        logging.error("config error: %s", exc)
        return 2

    worker = AgentWorker(config)

    loop = asyncio.get_running_loop()
    try:
        loop.add_signal_handler(signal.SIGINT, worker.stop)
    except (NotImplementedError, RuntimeError):  # Windows / no event loop signal support
        pass

    await worker.run(max_runtime=max_runtime)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rtva", description="Run the voice agent worker")
    parser.add_argument(
        "--max-runtime",
        type=float,
        default=None,
        help="stop automatically after N seconds (default: run until Ctrl-C)",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    return asyncio.run(_run(args.max_runtime))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
