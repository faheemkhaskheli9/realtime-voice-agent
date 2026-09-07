"""Agent worker: connect to a room, log lifecycle events, run until stopped.

Deliberate termination (knowledge-base pattern "Stateful agentic run
lifecycle"): the worker never loops unbounded — it runs until ``stop()`` is
called, an optional ``max_runtime`` elapses, or ``connect()`` fails, and it
always disconnects cleanly on the way out.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field

from .config import LiveKitConfig
from .room import (
    EVENT_CONNECTED,
    EVENT_DISCONNECTED,
    EVENT_PARTICIPANT_JOINED,
    EVENT_PARTICIPANT_LEFT,
    RoomClient,
    build_room_client,
)

logger = logging.getLogger("rtva.worker")


@dataclass
class AgentWorker:
    config: LiveKitConfig
    room: RoomClient = field(default=None)  # type: ignore[assignment]
    _stop: asyncio.Event = field(default_factory=asyncio.Event, repr=False)
    events: list[tuple[str, dict]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.room is None:
            self.room = build_room_client(self.config)
        self.room.on_event(self._record_event)

    # --- lifecycle logging --------------------------------------------

    def _record_event(self, event: str, data: dict) -> None:
        self.events.append((event, data))
        if event == EVENT_CONNECTED:
            logger.info("connected to room %s", data.get("room"))
        elif event == EVENT_DISCONNECTED:
            logger.info("disconnected from room %s", data.get("room"))
        elif event == EVENT_PARTICIPANT_JOINED:
            logger.info("participant joined: %s", data.get("identity"))
        elif event == EVENT_PARTICIPANT_LEFT:
            logger.info("participant left: %s", data.get("identity"))

    # --- run loop ----------------------------------------------------

    def stop(self) -> None:
        self._stop.set()

    async def run(self, max_runtime: float | None = None) -> None:
        mode = "connect" if self.config.is_configured else "dry-run"
        logger.info("starting agent worker (%s mode) as %r", mode, self.config.agent_identity)
        await self.room.connect()
        try:
            waiter = asyncio.create_task(self._stop.wait())
            done, pending = await asyncio.wait({waiter}, timeout=max_runtime)
            for task in pending:
                task.cancel()
        finally:
            await self.room.disconnect()
            logger.info("agent worker stopped")

    async def run_until_idle(self) -> None:
        """Connect, drain any already-queued events, disconnect. Used by smoke tests."""

        await self.run(max_runtime=0.01)
