import pytest

from rtva.config import ConfigError, LiveKitConfig


def test_no_credentials_is_dry_run():
    cfg = LiveKitConfig.from_env(env={})
    assert cfg.is_configured is False


def test_full_credentials_is_configured():
    cfg = LiveKitConfig.from_env(
        env={
            "LIVEKIT_URL": "wss://example",
            "LIVEKIT_API_KEY": "key",
            "LIVEKIT_API_SECRET": "secret",
        }
    )
    assert cfg.is_configured is True
    assert cfg.require_configured() is cfg


def test_partial_credentials_is_hard_error():
    with pytest.raises(ConfigError):
        LiveKitConfig.from_env(env={"LIVEKIT_URL": "wss://example"})


def test_require_configured_raises_in_dry_run():
    with pytest.raises(ConfigError):
        LiveKitConfig.from_env(env={}).require_configured()


def test_room_and_identity_overridable():
    cfg = LiveKitConfig.from_env(
        env={"LIVEKIT_ROOM": "r1", "LIVEKIT_AGENT_IDENTITY": "bot-7"}
    )
    assert cfg.room_name == "r1"
    assert cfg.agent_identity == "bot-7"
