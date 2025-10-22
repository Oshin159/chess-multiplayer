"""
Game Models for Emotional Chess Multiplayer

Defines game state, players, and game management classes with database persistence.
"""

import uuid
import time
import json
import chess
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from emotional_board import EmotionalBoard
from emfen import EmFEN
from database import DatabaseManager
from security import SecurityManager, sanitize_input, validate_move_notation, validate_player_name, validate_color


class GameStatus(Enum):
    """Game status enumeration."""
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    ABANDONED = "abandoned"


class PlayerStatus(Enum):
    """Player status enumeration."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    READY = "ready"
    THINKING = "thinking"


@dataclass
class Player:
    """Represents a player in the game."""
    id: str
    name: str
    color: str  # "white", "black", "red", "blue", etc.
    status: PlayerStatus = PlayerStatus.CONNECTED
    connected_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        """Convert player to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "status": self.status.value,
            "connected_at": self.connected_at,
            "last_activity": self.last_activity
        }


@dataclass
class Game:
    """Represents a multiplayer Emotional Chess game."""
    id: str
    name: str
    max_players: int = 2
    players: Dict[str, Player] = field(default_factory=dict)
    board: EmotionalBoard = field(default_factory=EmotionalBoard)
    status: GameStatus = GameStatus.WAITING
    current_turn: int = 0  # Index into turn_order
    turn_order: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    winner: Optional[str] = None
    move_history: List[Dict] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize game after creation."""
        if not self.turn_order:
            # Default turn order for 2 players
            if self.max_players == 2:
                self.turn_order = ["white", "black"]
            else:
                # For more players, use colors
                colors = ["white", "black", "red", "blue", "green", "yellow"]
                self.turn_order = colors[:self.max_players]
    
    def add_player(self, player: Player) -> bool:
        """Add a player to the game."""
        if len(self.players) >= self.max_players:
            return False
        
        if player.color in [p.color for p in self.players.values()]:
            return False
        
        self.players[player.id] = player
        return True
    
    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the game."""
        if player_id in self.players:
            del self.players[player_id]
            return True
        return False
    
    def get_current_player(self) -> Optional[Player]:
        """Get the current player whose turn it is."""
        if not self.turn_order or self.current_turn >= len(self.turn_order):
            return None
        
        current_color = self.turn_order[self.current_turn]
        for player in self.players.values():
            if player.color == current_color:
                return player
        return None
    
    def next_turn(self) -> bool:
        """Move to the next turn."""
        if not self.turn_order:
            return False
        
        self.current_turn = (self.current_turn + 1) % len(self.turn_order)
        return True
    
    def can_start(self) -> bool:
        """Check if the game can start."""
        return len(self.players) >= 2
    
    def start_game(self) -> bool:
        """Start the game."""
        if not self.can_start():
            return False
        
        self.status = GameStatus.IN_PROGRESS
        self.started_at = time.time()
        self.current_turn = 0
        return True
    
    def make_move(self, player_id: str, move_notation: str) -> Dict:
        """Make a move in the game."""
        if self.status != GameStatus.IN_PROGRESS:
            return {"success": False, "error": "Game not in progress"}
        
        if player_id not in self.players:
            return {"success": False, "error": "Player not in game"}
        
        player = self.players[player_id]
        current_player = self.get_current_player()
        
        if current_player and player.id != current_player.id:
            return {"success": False, "error": "Not your turn"}
        
        try:
            # Try to parse as coordinate notation first (e.g., "e2e4")
            if len(move_notation) == 4 and move_notation[0].islower() and move_notation[1].isdigit() and move_notation[2].islower() and move_notation[3].isdigit():
                from_square = chess.parse_square(move_notation[:2])
                to_square = chess.parse_square(move_notation[2:])
                move = chess.Move(from_square, to_square)
            else:
                # Parse as SAN notation
                move = self.board.parse_san(move_notation)
            
            # Check if the move is legal before pushing it
            legal_moves = self.board.generate_legal_moves()
            if move not in legal_moves:
                return {"success": False, "error": "Illegal move"}
            
            self.board.push(move)
            
            # Record the move
            move_record = {
                "player_id": player_id,
                "player_name": player.name,
                "move": move_notation,
                "timestamp": time.time(),
                "emotions": self.board.emotion_summary()
            }
            self.move_history.append(move_record)
            
            # Check for game end conditions
            if self.board.is_checkmate():
                self.status = GameStatus.FINISHED
                self.finished_at = time.time()
                self.winner = player_id
                return {
                    "success": True,
                    "move": move_notation,
                    "game_over": True,
                    "winner": player.name,
                    "reason": "checkmate"
                }
            elif self.board.is_stalemate():
                self.status = GameStatus.FINISHED
                self.finished_at = time.time()
                return {
                    "success": True,
                    "move": move_notation,
                    "game_over": True,
                    "winner": None,
                    "reason": "stalemate"
                }
            
            # Move to next turn
            self.next_turn()
            
            return {
                "success": True,
                "move": move_notation,
                "next_player": self.get_current_player().name if self.get_current_player() else None,
                "emotions": self.board.emotion_summary()
            }
            
        except Exception as e:
            return {"success": False, "error": f"Invalid move: {str(e)}"}
    
    def get_game_state(self) -> Dict:
        """Get the current game state."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "max_players": self.max_players,
            "players": [p.to_dict() for p in self.players.values()],
            "current_turn": self.current_turn,
            "turn_order": self.turn_order,
            "current_player": self.get_current_player().name if self.get_current_player() else None,
            "board_fen": self.board.fen(),
            "emfen": self.board.to_emfen(),
            "emotions": self.board.emotion_summary(),
            "move_count": len(self.move_history),
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "winner": self.winner
        }
    
    def to_dict(self) -> Dict:
        """Convert game to dictionary for JSON serialization."""
        return self.get_game_state()


class GameManager:
    """Manages multiple games and players with database persistence."""
    
    def __init__(self, db_path: str = "chess_games.db"):
        """Initialize the game manager."""
        self.games: Dict[str, Game] = {}
        self.player_sessions: Dict[str, str] = {}  # player_id -> game_id
        self.db_manager = DatabaseManager(db_path)
        self.security_manager = SecurityManager()
        self._load_games_from_db()
    
    def _load_games_from_db(self):
        """Load all games from the database into memory."""
        try:
            db_games = self.db_manager.load_all_games()
            for game_data in db_games:
                # Reconstruct Game object from database data
                game = self._reconstruct_game_from_db(game_data)
                if game:
                    self.games[game.id] = game
                    
                    # Reconstruct player sessions
                    players = self.db_manager.load_players_for_game(game.id)
                    for player_data in players:
                        self.player_sessions[player_data['id']] = game.id
        except Exception as e:
            print(f"Error loading games from database: {e}")
    
    def _reconstruct_game_from_db(self, game_data: Dict) -> Optional[Game]:
        """Reconstruct a Game object from database data."""
        try:
            # Create EmotionalBoard from FEN
            board = EmotionalBoard()
            if game_data.get('board_fen'):
                board.set_fen(game_data['board_fen'])
            
            # Create Game object
            game = Game(
                id=game_data['id'],
                name=game_data['name'],
                max_players=game_data['max_players'],
                board=board,
                status=GameStatus(game_data['status']),
                current_turn=game_data['current_turn'],
                turn_order=game_data.get('turn_order', []),
                created_at=game_data['created_at'],
                started_at=game_data.get('started_at'),
                finished_at=game_data.get('finished_at'),
                winner=game_data.get('winner')
            )
            
            # Load players
            players_data = self.db_manager.load_players_for_game(game.id)
            for player_data in players_data:
                player = Player(
                    id=player_data['id'],
                    name=player_data['name'],
                    color=player_data['color'],
                    status=PlayerStatus(player_data['status']),
                    connected_at=player_data['connected_at'],
                    last_activity=player_data['last_activity']
                )
                game.players[player.id] = player
            
            # Load move history
            moves_data = self.db_manager.load_moves_for_game(game.id)
            for move_data in moves_data:
                move_record = {
                    "player_id": move_data['player_id'],
                    "move": move_data['move_notation'],
                    "timestamp": move_data['timestamp'],
                    "emotions": move_data['emotions']
                }
                game.move_history.append(move_record)
            
            return game
        except Exception as e:
            print(f"Error reconstructing game: {e}")
            return None
    
    def create_game(self, name: str, max_players: int = 2) -> str:
        """Create a new game."""
        # Sanitize input
        name = sanitize_input({"name": name})["name"]
        
        # Validate input
        if not name or len(name.strip()) == 0:
            raise ValueError("Game name cannot be empty")
        
        if max_players < 2 or max_players > 6:
            raise ValueError("Max players must be between 2 and 6")
        
        game_id = str(uuid.uuid4())
        game = Game(
            id=game_id,
            name=name.strip(),
            max_players=max_players
        )
        
        # Save to database
        game_data = game.get_game_state()
        if not self.db_manager.save_game(game_data):
            raise Exception("Failed to save game to database")
        
        self.games[game_id] = game
        return game_id
    
    def get_game(self, game_id: str) -> Optional[Game]:
        """Get a game by ID."""
        return self.games.get(game_id)
    
    def join_game(self, game_id: str, player_name: str, preferred_color: str = None) -> Dict:
        """Join a game as a player."""
        # Sanitize and validate input
        player_name = sanitize_input({"name": player_name})["name"]
        
        if not validate_player_name(player_name):
            return {"success": False, "error": "Invalid player name"}
        
        if preferred_color and not validate_color(preferred_color):
            return {"success": False, "error": "Invalid color"}
        
        game = self.get_game(game_id)
        if not game:
            return {"success": False, "error": "Game not found"}
        
        if game.status != GameStatus.WAITING:
            return {"success": False, "error": "Game not accepting new players"}
        
        if len(game.players) >= game.max_players:
            return {"success": False, "error": "Game is full"}
        
        # Generate player ID
        player_id = str(uuid.uuid4())
        
        # Determine color
        if preferred_color and preferred_color not in [p.color for p in game.players.values()]:
            color = preferred_color
        else:
            # Assign first available color
            used_colors = {p.color for p in game.players.values()}
            available_colors = [c for c in game.turn_order if c not in used_colors]
            if available_colors:
                color = available_colors[0]
            else:
                return {"success": False, "error": "No available colors"}
        
        # Create player
        player = Player(
            id=player_id,
            name=player_name,
            color=color
        )
        
        # Add to game
        if game.add_player(player):
            # Save player to database
            player_data = {
                "id": player_id,
                "game_id": game_id,
                "name": player_name,
                "color": color,
                "status": player.status.value,
                "connected_at": player.connected_at,
                "last_activity": player.last_activity
            }
            
            if not self.db_manager.save_player(player_data):
                # Rollback player addition if database save fails
                game.remove_player(player_id)
                return {"success": False, "error": "Failed to save player to database"}
            
            # Update game in database
            game_data = game.get_game_state()
            if not self.db_manager.save_game(game_data):
                print("Warning: Failed to update game in database")
            
            self.player_sessions[player_id] = game_id
            
            # Generate session token
            session_token = self.security_manager.generate_session_token(player_id, game_id)
            
            return {
                "success": True,
                "player_id": player_id,
                "game_id": game_id,
                "color": color,
                "session_token": session_token,
                "game_state": game.get_game_state()
            }
        else:
            return {"success": False, "error": "Failed to join game"}
    
    def leave_game(self, player_id: str) -> bool:
        """Leave a game."""
        if player_id not in self.player_sessions:
            return False
        
        game_id = self.player_sessions[player_id]
        game = self.get_game(game_id)
        
        if game:
            game.remove_player(player_id)
            del self.player_sessions[player_id]
            
            # If no players left, mark game as abandoned
            if not game.players:
                game.status = GameStatus.ABANDONED
                game.finished_at = time.time()
            
            return True
        
        return False
    
    def start_game(self, game_id: str) -> bool:
        """Start a game."""
        game = self.get_game(game_id)
        if game:
            return game.start_game()
        return False
    
    def make_move(self, player_id: str, move_notation: str) -> Dict:
        """Make a move in a game."""
        # Validate move notation
        if not validate_move_notation(move_notation):
            return {"success": False, "error": "Invalid move notation"}
        
        if player_id not in self.player_sessions:
            return {"success": False, "error": "Player not in any game"}
        
        game_id = self.player_sessions[player_id]
        game = self.get_game(game_id)
        
        if not game:
            return {"success": False, "error": "Game not found"}
        
        # Make the move
        result = game.make_move(player_id, move_notation)
        
        # If move was successful, save to database
        if result.get("success"):
            # Save move to database
            emotions = game.board.emotion_summary()
            emotions_json = json.dumps(emotions) if isinstance(emotions, dict) else str(emotions)
            
            move_data = {
                "id": str(uuid.uuid4()),
                "game_id": game_id,
                "player_id": player_id,
                "move_notation": move_notation,
                "board_fen_after": game.board.fen(),
                "emfen_after": game.board.to_emfen(),
                "emotions": emotions_json,
                "timestamp": time.time()
            }
            
            if not self.db_manager.save_move(move_data):
                print("Warning: Failed to save move to database")
            
            # Update game state in database
            game_data = game.get_game_state()
            if not self.db_manager.save_game(game_data):
                print("Warning: Failed to update game in database")
        
        return result
    
    def get_player_game(self, player_id: str) -> Optional[Game]:
        """Get the game a player is in."""
        if player_id not in self.player_sessions:
            return None
        
        game_id = self.player_sessions[player_id]
        return self.get_game(game_id)
    
    def list_games(self) -> List[Dict]:
        """List all games."""
        return [game.to_dict() for game in self.games.values()]
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """Validate a session token and return session data."""
        return self.security_manager.validate_session_token(session_token)
    
    def cleanup_abandoned_games(self, max_age_hours: int = 24):
        """Clean up abandoned games older than max_age_hours."""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        games_to_remove = []
        for game_id, game in self.games.items():
            if (game.status == GameStatus.ABANDONED and 
                game.finished_at and 
                current_time - game.finished_at > max_age_seconds):
                games_to_remove.append(game_id)
        
        for game_id in games_to_remove:
            # Remove from database
            self.db_manager.delete_game(game_id)
            # Remove from memory
            del self.games[game_id]
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        return self.db_manager.cleanup_expired_sessions()
    
    def get_session_security_manager(self):
        """Get the security manager instance."""
        return self.security_manager
