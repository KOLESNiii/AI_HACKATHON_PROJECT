"""Local SQLite transactions for scene identities and recoverable provider requests."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from .selection_models import RegistryState


class Registry:
    def __init__(self, data_dir: Path, *, namespace: str = "") -> None:
        self.namespace = namespace
        data_dir.mkdir(parents=True, exist_ok=True)
        self.path = data_dir / "registry.sqlite3"
        with self._connect() as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise ValueError(f"unsupported registry version {version}")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS scenes "
                "(scene_id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS requests (key TEXT PRIMARY KEY, payload TEXT NOT NULL)"
            )
            connection.execute("PRAGMA user_version = 1")

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=5)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def load(self, scene_id: str) -> RegistryState:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM scenes WHERE scene_id = ?", (scene_id,)
            ).fetchone()
        return RegistryState.model_validate_json(row[0]) if row else RegistryState()

    def update(self, scene_id: str, mutate: Callable[[RegistryState], None]) -> RegistryState:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT payload FROM scenes WHERE scene_id = ?", (scene_id,)
            ).fetchone()
            state = RegistryState.model_validate_json(row[0]) if row else RegistryState()
            mutate(state)
            state.revision += 1
            # Revalidate the persisted snapshot after domain mutation, before commit.
            state = RegistryState.model_validate(state.model_dump())
            connection.execute(
                "INSERT INTO scenes VALUES (?, ?) ON CONFLICT(scene_id) "
                "DO UPDATE SET payload=excluded.payload",
                (scene_id, state.model_dump_json()),
            )
        return state

    def reserve_request(self, key: str) -> tuple[bool, dict[str, Any]]:
        """Only the winner submits; a crash before recording its handle is explicit uncertainty."""
        key = json.dumps([self.namespace, key])
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT payload FROM requests WHERE key = ?", (key,)
            ).fetchone()
            if row:
                return False, json.loads(row[0])
            pending = {"status": "reserved"}
            connection.execute("INSERT INTO requests VALUES (?, ?)", (key, json.dumps(pending)))
        return True, pending

    def save_request(self, key: str, payload: dict[str, Any]) -> None:
        key = json.dumps([self.namespace, key])
        with self._connect() as connection:
            connection.execute(
                "UPDATE requests SET payload = ? WHERE key = ?",
                (
                    json.dumps(payload),
                    key,
                ),
            )

    def release_reservation(self, key: str) -> None:
        """Only a known pre-submit failure is safe to release; never remove a saved handle."""
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM requests WHERE key = ? AND payload = ?",
                (json.dumps([self.namespace, key]), json.dumps({"status": "reserved"})),
            )
