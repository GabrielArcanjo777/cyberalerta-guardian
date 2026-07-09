"""Deterministic test environment.

Tests must never depend on the developer's local `.env` (which points storage at
sqlite and the channel provider at Evolution for real local runs). Setting these
before any app import makes the whole suite run in-memory, isolated, with the
default `mock` adapter and no database file created on disk.
"""

import os

os.environ["CYBERALERTA_DISABLE_DOTENV"] = "1"
os.environ["STORAGE_BACKEND"] = "memory"
os.environ.setdefault("APP_ENV", "test")
