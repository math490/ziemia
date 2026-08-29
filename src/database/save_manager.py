"""Save game management using SQLite and JSON."""

import sqlite3
import json
import os
from typing import Dict, Any, Optional


class SaveManager:
    """Manages game saves using SQLite database and JSON serialization."""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize save manager.
        
        Args:
            data_dir: Directory to store save files
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, "ziemia_saves.db")
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create saves table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    player_data TEXT NOT NULL,
                    world_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create inventory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    save_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    FOREIGN KEY(save_id) REFERENCES saves(id)
                )
            """)
            
            conn.commit()

    def save_game(self, name: str, player_data: Dict[str, Any], world_data: Dict[str, Any]):
        """
        Save a game.
        
        Args:
            name: Save name
            player_data: Player state dictionary
            world_data: World state dictionary
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            player_json = json.dumps(player_data)
            world_json = json.dumps(world_data)
            
            try:
                cursor.execute("""
                    INSERT INTO saves (name, player_data, world_data)
                    VALUES (?, ?, ?)
                """, (name, player_json, world_json))
            except sqlite3.IntegrityError:
                # Update existing save
                cursor.execute("""
                    UPDATE saves SET player_data = ?, world_data = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ?
                """, (player_json, world_json, name))
            
            conn.commit()

    def load_game(self, name: str) -> Optional[tuple]:
        """
        Load a game.
        
        Args:
            name: Save name
            
        Returns:
            Tuple of (player_data, world_data) or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT player_data, world_data FROM saves WHERE name = ?
            """, (name,))
            
            result = cursor.fetchone()
            if result:
                player_data = json.loads(result[0])
                world_data = json.loads(result[1])
                return player_data, world_data
            return None

    def list_saves(self) -> list:
        """
        List all saved games.
        
        Returns:
            List of save names
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM saves ORDER BY updated_at DESC")
            return [row[0] for row in cursor.fetchall()]

    def delete_save(self, name: str):
        """
        Delete a saved game.
        
        Args:
            name: Save name
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM saves WHERE name = ?", (name,))
            conn.commit()
