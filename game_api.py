"""
Flask API for Emotional Chess Multiplayer

Provides REST API and WebSocket endpoints for multiplayer Emotional Chess games.
"""

from flask import Flask, request, jsonify, g
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import time
from typing import Dict, List
from game_models import GameManager, GameStatus, PlayerStatus
from security import require_session, require_csrf, validate_game_access, rate_limit, SecurityConfig


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'emotional_chess_secret_key'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize game manager with database
game_manager = GameManager()

# Initialize security configuration
security_config = SecurityConfig()


# REST API Routes

@app.route('/api/games', methods=['GET'])
def list_games():
    """List all available games."""
    games = game_manager.list_games()
    return jsonify({
        "success": True,
        "games": games,
        "count": len(games)
    })


@app.route('/api/games', methods=['POST'])
@rate_limit(max_requests=10, window_minutes=5)
def create_game():
    """Create a new game."""
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No JSON data provided"}), 400
    
    name = data.get('name', 'Emotional Chess Game')
    max_players = data.get('max_players', 2)
    
    try:
        game_id = game_manager.create_game(name, max_players)
        game = game_manager.get_game(game_id)
        
        return jsonify({
            "success": True,
            "game_id": game_id,
            "game": game.get_game_state()
        })
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": "Failed to create game"}), 500


@app.route('/api/games/<game_id>', methods=['GET'])
def get_game(game_id):
    """Get a specific game."""
    game = game_manager.get_game(game_id)
    
    if not game:
        return jsonify({"success": False, "error": "Game not found"}), 404
    
    return jsonify({
        "success": True,
        "game": game.get_game_state()
    })


@app.route('/api/games/<game_id>/join', methods=['POST'])
def join_game(game_id):
    """Join a game."""
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No JSON data provided"}), 400
    
    player_name = data.get('name')
    preferred_color = data.get('color')
    
    if not player_name:
        return jsonify({"success": False, "error": "Player name required"}), 400
    
    result = game_manager.join_game(game_id, player_name, preferred_color)
    
    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), 400


@app.route('/api/games/<game_id>/start', methods=['POST'])
def start_game(game_id):
    """Start a game."""
    game = game_manager.get_game(game_id)
    
    if not game:
        return jsonify({"success": False, "error": "Game not found"}), 404
    
    if game.status != GameStatus.WAITING:
        return jsonify({"success": False, "error": "Game cannot be started"}), 400
    
    if game.start_game():
        # Notify all players via WebSocket
        socketio.emit('game_started', {
            "game": game.get_game_state()
        }, room=game_id)
        
        return jsonify({
            "success": True,
            "message": "Game started",
            "game": game.get_game_state()
        })
    else:
        return jsonify({"success": False, "error": "Cannot start game"}), 400


@app.route('/api/games/<game_id>/move', methods=['POST'])
@require_session
@require_csrf
@validate_game_access
@rate_limit(max_requests=30, window_minutes=1)
def make_move(game_id):
    """Make a move in a game."""
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No JSON data provided"}), 400
    
    move = data.get('move')
    
    if not move:
        return jsonify({"success": False, "error": "Move required"}), 400
    
    # Get player_id from session
    player_id = g.player_id
    
    game = game_manager.get_game(game_id)
    
    if not game:
        return jsonify({"success": False, "error": "Game not found"}), 404
    
    result = game_manager.make_move(player_id, move)
    
    if result["success"]:
        # Notify all players via WebSocket
        socketio.emit('move_made', {
            "player_id": player_id,
            "move": move,
            "game": game.get_game_state(),
            "emotions": game.board.emotion_summary()
        }, room=game_id)
        
        # If game is over, notify players
        if result.get("game_over"):
            socketio.emit('game_ended', {
                "game": game.get_game_state(),
                "winner": result.get("winner"),
                "reason": result.get("reason")
            }, room=game_id)
    
    return jsonify(result)


@app.route('/api/players/<player_id>/game', methods=['GET'])
def get_player_game(player_id):
    """Get the game a player is in."""
    game = game_manager.get_player_game(player_id)
    
    if not game:
        return jsonify({"success": False, "error": "Player not in any game"}), 404
    
    return jsonify({
        "success": True,
        "game": game.get_game_state()
    })


@app.route('/api/players/<player_id>/leave', methods=['POST'])
def leave_game(player_id):
    """Leave a game."""
    if game_manager.leave_game(player_id):
        return jsonify({"success": True, "message": "Left game"})
    else:
        return jsonify({"success": False, "error": "Player not in any game"}), 404


# WebSocket Events

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to Emotional Chess server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print(f"Client disconnected: {request.sid}")


@socketio.on('join_game_room')
def handle_join_game_room(data):
    """Join a game room for real-time updates."""
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    
    if not game_id or not player_id:
        emit('error', {'message': 'Game ID and player ID required'})
        return
    
    game = game_manager.get_game(game_id)
    if not game:
        emit('error', {'message': 'Game not found'})
        return
    
    if player_id not in game.players:
        emit('error', {'message': 'Player not in game'})
        return
    
    join_room(game_id)
    emit('joined_room', {
        'game_id': game_id,
        'message': 'Joined game room'
    })


@socketio.on('leave_game_room')
def handle_leave_game_room(data):
    """Leave a game room."""
    game_id = data.get('game_id')
    
    if game_id:
        leave_room(game_id)
        emit('left_room', {
            'game_id': game_id,
            'message': 'Left game room'
        })


@socketio.on('get_game_state')
def handle_get_game_state(data):
    """Get current game state."""
    game_id = data.get('game_id')
    
    if not game_id:
        emit('error', {'message': 'Game ID required'})
        return
    
    game = game_manager.get_game(game_id)
    if not game:
        emit('error', {'message': 'Game not found'})
        return
    
    emit('game_state', game.get_game_state())


@socketio.on('make_move')
def handle_make_move(data):
    """Make a move via WebSocket."""
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    move = data.get('move')
    
    if not all([game_id, player_id, move]):
        emit('error', {'message': 'Game ID, player ID, and move required'})
        return
    
    game = game_manager.get_game(game_id)
    if not game:
        emit('error', {'message': 'Game not found'})
        return
    
    result = game.make_move(player_id, move)
    
    if result["success"]:
        # Broadcast move to all players in the room
        socketio.emit('move_made', {
            "player_id": player_id,
            "move": move,
            "game": game.get_game_state(),
            "emotions": game.board.emotion_summary()
        }, room=game_id)
        
        # If game is over, notify players
        if result.get("game_over"):
            socketio.emit('game_ended', {
                "game": game.get_game_state(),
                "winner": result.get("winner"),
                "reason": result.get("reason")
            }, room=game_id)
    else:
        emit('move_error', result)


@socketio.on('start_game')
def handle_start_game(data):
    """Start a game via WebSocket."""
    game_id = data.get('game_id')
    
    if not game_id:
        emit('error', {'message': 'Game ID required'})
        return
    
    game = game_manager.get_game(game_id)
    if not game:
        emit('error', {'message': 'Game not found'})
        return
    
    if game.start_game():
        socketio.emit('game_started', {
            "game": game.get_game_state()
        }, room=game_id)
    else:
        emit('error', {'message': 'Cannot start game'})


# Error handlers

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"success": False, "error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"success": False, "error": "Internal server error"}), 500


# Health check endpoint

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "success": True,
        "status": "healthy",
        "timestamp": time.time(),
        "active_games": len(game_manager.games),
        "active_players": len(game_manager.player_sessions),
        "database_connected": True
    })


@app.route('/api/session/validate', methods=['POST'])
def validate_session():
    """Validate a session token."""
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No JSON data provided"}), 400
    
    session_token = data.get('session_token')
    
    if not session_token:
        return jsonify({"success": False, "error": "Session token required"}), 400
    
    session_data = game_manager.validate_session(session_token)
    
    if session_data:
        return jsonify({
            "success": True,
            "valid": True,
            "player_id": session_data.get('player_id'),
            "game_id": session_data.get('game_id'),
            "expires_at": session_data.get('exp')
        })
    else:
        return jsonify({
            "success": True,
            "valid": False
        })


@app.route('/api/session/refresh', methods=['POST'])
@require_session
def refresh_session():
    """Refresh a session token."""
    # Generate new session token
    new_token = game_manager.get_session_security_manager().generate_session_token(
        g.player_id, g.game_id
    )
    
    return jsonify({
        "success": True,
        "session_token": new_token,
        "expires_in_hours": 24
    })


@app.route('/api/admin/cleanup', methods=['POST'])
def admin_cleanup():
    """Admin endpoint to clean up expired sessions and abandoned games."""
    try:
        # Clean up expired sessions
        expired_sessions = game_manager.cleanup_expired_sessions()
        
        # Clean up abandoned games
        game_manager.cleanup_abandoned_games()
        
        return jsonify({
            "success": True,
            "expired_sessions_cleaned": expired_sessions,
            "message": "Cleanup completed"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Cleanup failed: {str(e)}"
        }), 500


if __name__ == '__main__':
    # Run the server
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)

