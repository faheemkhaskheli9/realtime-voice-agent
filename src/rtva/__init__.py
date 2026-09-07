"""Real-Time Voice AI Agent — Phase 1 package.

Phase 1: bootstrap a LiveKit room session with a Python agent worker and log
its connect/disconnect lifecycle. The transport (LiveKit) sits behind a
:class:`~rtva.room.RoomClient` protocol so the worker logic runs and is tested
without a live server; the real client is wired in when credentials are set.
"""

__version__ = "0.1.0"
