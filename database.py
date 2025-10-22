"""
Database models and management for Emotional Chess Multiplayer

Provides SQLite-based persistence for games, players, and sessions.
"""

import sqlite3
import json
import time
import uuid
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import os


@dataclass
class DatabaseGame:
    """Database representation of a game."""
    id: str
    name: str
    max_players: int
    status: str
    current_turn: int
    turn_order: str  # JSON string
    board_fen: str
    emfen: str
    created_at: float
    started_at: Optional[float]
    finished_at: Optional[float]
    winner: Optional[str]


@dataclass
class DatabasePlayer:
    """Database representation of a player."""
    id: str
    game_id: str
    name: str
    color: str
    status: str
    connected_at: float
    last_activity: float


@dataclass
class DatabaseMove:
    """Database representation of a move."""
    id: str
    game_id: str
    player_id: str
    move_notation: str
    board_fen_after: str
    emfen_after: str
    emotions: str  # JSON string
    timestamp: float


@dataclass
class DatabaseSession:
    """Database representation of a player session."""
    player_id: str
    game_id: str
    session_token: str
    created_at: float
    last_activity: float
    expires_at: float


class DatabaseManager:
    """Manages database operations for the chess application."""
    
    def __init__(self, db_path: str = "chess_games.db"):
        """Initialize the database manager."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create games table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    max_players INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    current_turn INTEGER NOT NULL,
                    turn_order TEXT NOT NULL,
                    board_fen TEXT NOT NULL,
                    emfen TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    started_at REAL,
                    finished_at REAL,
                    winner TEXT
                )
            """)
            
            # Create players table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id TEXT PRIMARY KEY,
                    game_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    color TEXT NOT NULL,
                    status TEXT NOT NULL,
                    connected_at REAL NOT NULL,
                    last_activity REAL NOT NULL,
                    FOREIGN KEY (game_id) REFERENCES games (id) ON DELETE CASCADE
                )
            """)
            
            # Create moves table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS moves (
                    id TEXT PRIMARY KEY,
                    game_id TEXT NOT NULL,
                    player_id TEXT NOT NULL,
                    move_notation TEXT NOT NULL,
                    board_fen_after TEXT NOT NULL,
                    emfen_after TEXT NOT NULL,
                    emotions TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY (game_id) REFERENCES games (id) ON DELETE CASCADE,
                    FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE
                )
            """)
            
            # Create sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    player_id TEXT PRIMARY KEY,
                    game_id TEXT NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    created_at REAL NOT NULL,
                    last_activity REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    FOREIGN KEY (game_id) REFERENCES games (id) ON DELETE CASCADE,
                    FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_game_id ON players (game_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_moves_game_id ON moves (game_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions (session_token)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions (expires_at)")
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Get a database connection with proper error handling."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    # Game operations
    def save_game(self, game_data: Dict) -> bool:
        """Save a game to the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Convert turn_order list to JSON string
                turn_order_json = json.dumps(game_data.get('turn_order', []))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO games 
                    (id, name, max_players, status, current_turn, turn_order, 
                     board_fen, emfen, created_at, started_at, finished_at, winner)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    game_data['id'],
                    game_data['name'],
                    game_data['max_players'],
                    game_data['status'],
                    game_data['current_turn'],
                    turn_order_json,
                    game_data['board_fen'],
                    game_data['emfen'],
                    game_data['created_at'],
                    game_data.get('started_at'),
                    game_data.get('finished_at'),
                    game_data.get('winner')
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, game_id: str) -> Optional[Dict]:
        """Load a game from the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM games WHERE id = ?", (game_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                # Convert row to dictionary
                game_data = dict(row)
                game_data['turn_order'] = json.loads(game_data['turn_order'])
                return game_data
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    def load_all_games(self) -> List[Dict]:
        """Load all games from the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM games ORDER BY created_at DESC")
                rows = cursor.fetchall()
                
                games = []
                for row in rows:
                    game_data = dict(row)
                    game_data['turn_order'] = json.loads(game_data['turn_order'])
                    games.append(game_data)
                
                return games
        except Exception as e:
            print(f"Error loading games: {e}")
            return []
    
    def delete_game(self, game_id: str) -> bool:
        """Delete a game and all related data."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM games WHERE id = ?", (game_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting game: {e}")
            return False
    
    # Player operations
    def save_player(self, player_data: Dict) -> bool:
        """Save a player to the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO players 
                    (id, game_id, name, color, status, connected_at, last_activity)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    player_data['id'],
                    player_data['game_id'],
                    player_data['name'],
                    player_data['color'],
                    player_data['status'],
                    player_data['connected_at'],
                    player_data['last_activity']
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving player: {e}")
            return False
    
    def load_players_for_game(self, game_id: str) -> List[Dict]:
        """Load all players for a specific game."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM players WHERE game_id = ?", (game_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error loading players: {e}")
            return []
    
    def delete_player(self, player_id: str) -> bool:
        """Delete a player from the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting player: {e}")
            return False
    
    # Move operations
    def save_move(self, move_data: Dict) -> bool:
        """Save a move to the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO moves 
                    (id, game_id, player_id, move_notation, board_fen_after, 
                     emfen_after, emotions, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    move_data['id'],
                    move_data['game_id'],
                    move_data['player_id'],
                    move_data['move_notation'],
                    move_data['board_fen_after'],
                    move_data['emfen_after'],
                    move_data['emotions'],
                    move_data['timestamp']
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving move: {e}")
            return False
    
    def load_moves_for_game(self, game_id: str) -> List[Dict]:
        """Load all moves for a specific game."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM moves 
                    WHERE game_id = ? 
                    ORDER BY timestamp ASC
                """, (game_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error loading moves: {e}")
            return []
    
    # Session operations
    def create_session(self, player_id: str, game_id: str, session_token: str, 
                      expires_in_hours: int = 24) -> bool:
        """Create a new session."""
        try:
            current_time = time.time()
            expires_at = current_time + (expires_in_hours * 3600)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO sessions 
                    (player_id, game_id, session_token, created_at, last_activity, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (player_id, game_id, session_token, current_time, current_time, expires_at))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating session: {e}")
            return False
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """Validate a session token and return session data."""
        try:
            current_time = time.time()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM sessions 
                    WHERE session_token = ? AND expires_at > ?
                """, (session_token, current_time))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                # Update last activity
                cursor.execute("""
                    UPDATE sessions 
                    SET last_activity = ? 
                    WHERE session_token = ?
                """, (current_time, session_token))
                conn.commit()
                
                return dict(row)
        except Exception as e:
            print(f"Error validating session: {e}")
            return None
    
    def delete_session(self, session_token: str) -> bool:
        """Delete a session."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of cleaned sessions."""
        try:
            current_time = time.time()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sessions WHERE expires_at <= ?", (current_time,))
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count
        except Exception as e:
            print(f"Error cleaning up sessions: {e}")
            return 0
    
    def get_player_session(self, player_id: str) -> Optional[Dict]:
        """Get session data for a player."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sessions WHERE player_id = ?", (player_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"Error getting player session: {e}")
            return None
