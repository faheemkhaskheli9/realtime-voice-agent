import asyncio

import pytest

from rtva.config import LiveKitConfig
from rtva.room import (
    EVENT_CONNECTED,
    EVENT_DISCONNECTED,
    EVENT_PARTICIPANT_JOINED,
    FakeRoomClient,
    build_room_client,
)
from rtva.worker import AgentWorker


def _dry_run_config():
    return LiveKitConfig.from_env(env={})


def test_build_room_client_returns_fake_in_dry_run():
    assert isinstance(build_room_client(_dry_run_config()), FakeRoomClient)


def test_worker_logs_connect_and_disconnect_lifecycle():
    worker = AgentWorker(_dry_run_config())
    asyncio.run(worker.run(max_runtime=0.01))
    names = [e for e, _ in worker.events]
    assert names[0] == EVENT_CONNECTED
    assert names[-1] == EVENT_DISCONNECTED


def test_worker_records_participant_join(caplog):
    config = _dry_run_config()
    room = FakeRoomClient(config)
    worker = AgentWorker(config, room=room)

    async def scenario():
        task = asyncio.create_task(worker.run())
        await asyncio.sleep(0)
        room.simulate_participant_join("test-client")
        assert room.participants == ["test-client"]
        worker.stop()
        await task

    with caplog.at_level("INFO"):
        asyncio.run(scenario())

    assert (EVENT_PARTICIPANT_JOINED, {"identity": "test-client"}) in worker.events
    assert "participant joined: test-client" in caplog.text


def test_worker_stop_makes_run_return():
    worker = AgentWorker(_dry_run_config())

    async def scenario():
        task = asyncio.create_task(worker.run())
        worker.stop()
        await asyncio.wait_for(task, timeout=1.0)

    asyncio.run(scenario())
    assert worker.room.connected is False


def test_max_runtime_terminates_without_stop():
    worker = AgentWorker(_dry_run_config())
    asyncio.run(asyncio.wait_for(worker.run(max_runtime=0.05), timeout=1.0))
    assert worker.room.connected is False
