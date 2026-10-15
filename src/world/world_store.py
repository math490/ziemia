from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SavedWorld:
    world_id: int
    name: str
    seed: int
    width: int
    height: int
    created_at: str


class WorldStore:
    def __init__(self, database_path: str | Path | None = None) -> None:
        if database_path is None:
            project_root = Path(__file__).resolve().parents[2]
            database_path = project_root / "src" / "saves" / "worlds.db"
            legacy_database_path = project_root / "worlds.db"
            if legacy_database_path.exists() and not database_path.exists():
                database_path.parent.mkdir(parents=True, exist_ok=True)
                legacy_database_path.replace(database_path)
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _initialize_database(self) -> None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS worlds (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        seed INTEGER NOT NULL,
                        width INTEGER NOT NULL,
                        height INTEGER NOT NULL,
                        tiles TEXT NOT NULL,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

    def list_worlds(self) -> list[SavedWorld]:
        with closing(sqlite3.connect(self.database_path)) as connection:
            rows = connection.execute(
                "SELECT id, name, seed, width, height, created_at FROM worlds ORDER BY id DESC"
            ).fetchall()
        return [SavedWorld(*row) for row in rows]

    def save_world(self, name: str, seed: int, tiles: list[list[int]]) -> int:
        world_name = name.strip()
        if not world_name:
            raise ValueError("O mundo precisa ter um nome.")
        if not tiles or not tiles[0]:
            raise ValueError("O mapa não pode estar vazio.")

        height = len(tiles)
        width = len(tiles[0])
        serialized_tiles = json.dumps(tiles, separators=(",", ":"))
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                cursor = connection.execute(
                    "INSERT INTO worlds (name, seed, width, height, tiles) VALUES (?, ?, ?, ?, ?)",
                    (world_name, seed, width, height, serialized_tiles),
                )
                return int(cursor.lastrowid)

    def load_world(self, world_id: int) -> tuple[SavedWorld, list[list[int]]] | None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            row = connection.execute(
                "SELECT id, name, seed, width, height, created_at, tiles FROM worlds WHERE id = ?",
                (world_id,),
            ).fetchone()
        if row is None:
            return None

        saved_world = SavedWorld(*row[:6])
        tiles = json.loads(row[6])
        return saved_world, tiles

    def delete_world(self, world_id: int) -> bool:
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                cursor = connection.execute("DELETE FROM worlds WHERE id = ?", (world_id,))
                return cursor.rowcount > 0