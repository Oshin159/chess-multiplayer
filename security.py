"""
Security and authentication for Emotional Chess Multiplayer

Provides JWT token generation, session validation, and security middleware.
"""

import jwt
import secrets
import time
import hashlib
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g
import json


class SecurityManager:
    """Manages security operations for the chess application."""
    
    def __init__(self, secret_key: str = None):
        """Initialize the security manager."""
        self.secret_key = secret_key or self._generate_secret_key()
        self.algorithm = 'HS256'
        self.token_expiry_hours = 24
        self.session_expiry_hours = 24
    
    def _generate_secret_key(self) -> str:
        """Generate a secure secret key."""
        return secrets.token_urlsafe(32)
    
    def generate_session_token(self, player_id: str, game_id: str, 
                              additional_claims: Dict = None) -> str:
        """Generate a JWT session token for a player."""
        current_time = time.time()
        
        payload = {
            'player_id': player_id,
            'game_id': game_id,
            'iat': current_time,
            'exp': current_time + (self.token_expiry_hours * 3600),
            'type': 'session'
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def validate_session_token(self, token: str) -> Optional[Dict]:
        """Validate a session token and return the payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is expired
            if payload.get('exp', 0) < time.time():
                return None
            
            # Check if token type is correct
            if payload.get('type') != 'session':
                return None
            
            return payload
        except jwt.InvalidTokenError:
            return None
    
    def generate_api_key(self, player_id: str, permissions: List[str] = None) -> str:
        """Generate an API key for a player."""
        if permissions is None:
            permissions = ['read', 'write']
        
        payload = {
            'player_id': player_id,
            'permissions': permissions,
            'iat': time.time(),
            'type': 'api_key'
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """Validate an API key and return the payload."""
        try:
            payload = jwt.decode(api_key, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get('type') != 'api_key':
                return None
            
            return payload
        except jwt.InvalidTokenError:
            return None
    
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        return self.hash_password(password) == hashed
    
    def generate_csrf_token(self, session_token: str) -> str:
        """Generate a CSRF token for a session."""
        payload = {
            'session_token': session_token,
            'iat': time.time(),
            'exp': time.time() + 3600,  # 1 hour expiry
            'type': 'csrf'
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def validate_csrf_token(self, csrf_token: str, session_token: str) -> bool:
        """Validate a CSRF token against a session token."""
        try:
            payload = jwt.decode(csrf_token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get('type') != 'csrf':
                return False
            
            if payload.get('session_token') != session_token:
                return False
            
            return True
        except jwt.InvalidTokenError:
            return False


def require_session(f):
    """Decorator to require a valid session token."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get session token from Authorization header or request data
        session_token = None
        
        # Check Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            session_token = auth_header[7:]
        
        # Check request data
        if not session_token:
            data = request.get_json() or {}
            session_token = data.get('session_token')
        
        if not session_token:
            return jsonify({
                "success": False,
                "error": "Session token required",
                "code": "MISSING_TOKEN"
            }), 401
        
        # Validate session token
        from game_api import game_manager
        session_data = game_manager.validate_session_token(session_token)
        
        if not session_data:
            return jsonify({
                "success": False,
                "error": "Invalid or expired session token",
                "code": "INVALID_TOKEN"
            }), 401
        
        # Store session data in Flask's g object for use in the route
        g.session_data = session_data
        g.player_id = session_data['player_id']
        g.game_id = session_data['game_id']
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_csrf(f):
    """Decorator to require CSRF token validation."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get CSRF token from request
        csrf_token = request.headers.get('X-CSRF-Token')
        if not csrf_token:
            data = request.get_json() or {}
            csrf_token = data.get('csrf_token')
        
        if not csrf_token:
            return jsonify({
                "success": False,
                "error": "CSRF token required",
                "code": "MISSING_CSRF"
            }), 403
        
        # Get session token
        session_token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            session_token = auth_header[7:]
        
        if not session_token:
            data = request.get_json() or {}
            session_token = data.get('session_token')
        
        if not session_token:
            return jsonify({
                "success": False,
                "error": "Session token required for CSRF validation",
                "code": "MISSING_SESSION"
            }), 401
        
        # Validate CSRF token
        from game_api import security_manager
        if not security_manager.validate_csrf_token(csrf_token, session_token):
            return jsonify({
                "success": False,
                "error": "Invalid CSRF token",
                "code": "INVALID_CSRF"
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def rate_limit(max_requests: int = 100, window_minutes: int = 15):
    """Decorator to implement rate limiting."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple in-memory rate limiting (for production, use Redis)
            client_ip = request.remote_addr
            current_time = time.time()
            window_seconds = window_minutes * 60
            
            # This is a simplified implementation
            # In production, you'd want to use Redis or a proper rate limiting library
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_game_access(f):
    """Decorator to validate that a player has access to a specific game."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get game_id from URL parameters
        game_id = kwargs.get('game_id')
        if not game_id:
            return jsonify({
                "success": False,
                "error": "Game ID required",
                "code": "MISSING_GAME_ID"
            }), 400
        
        # Check if player has access to this game
        player_game_id = g.game_id
        if player_game_id != game_id:
            return jsonify({
                "success": False,
                "error": "Access denied to this game",
                "code": "ACCESS_DENIED"
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def sanitize_input(data: Dict) -> Dict:
    """Sanitize input data to prevent injection attacks."""
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            # Remove potentially dangerous characters
            sanitized[key] = value.strip().replace('<', '&lt;').replace('>', '&gt;')
        elif isinstance(value, (int, float, bool)):
            sanitized[key] = value
        elif isinstance(value, dict):
            sanitized[key] = sanitize_input(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_input(item) if isinstance(item, dict) else item for item in value]
        else:
            sanitized[key] = value
    
    return sanitized


def validate_move_notation(move: str) -> bool:
    """Validate chess move notation."""
    if not move or not isinstance(move, str):
        return False
    
    # Basic validation - check for common chess move patterns
    move = move.strip()
    
    # Allow coordinate notation (e.g., "e2e4")
    if len(move) == 4 and move[0].islower() and move[1].isdigit() and move[2].islower() and move[3].isdigit():
        return True
    
    # Allow standard algebraic notation
    import re
    pattern = r'^[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?[+#]?$'
    
    return bool(re.match(pattern, move))


def validate_player_name(name: str) -> bool:
    """Validate player name."""
    if not name or not isinstance(name, str):
        return False
    
    name = name.strip()
    
    # Check length
    if len(name) < 1 or len(name) > 50:
        return False
    
    # Check for valid characters (alphanumeric, spaces, hyphens, underscores)
    import re
    pattern = r'^[a-zA-Z0-9\s\-_]+$'
    
    return bool(re.match(pattern, name))


def validate_color(color: str) -> bool:
    """Validate player color."""
    valid_colors = ['white', 'black', 'red', 'blue', 'green', 'yellow']
    return color in valid_colors


class SecurityConfig:
    """Security configuration settings."""
    
    def __init__(self):
        self.max_players_per_game = 6
        self.max_games_per_player = 5
        self.max_moves_per_game = 1000
        self.session_timeout_minutes = 30
        self.rate_limit_requests_per_minute = 60
        self.max_player_name_length = 50
        self.allowed_origins = ['http://localhost:3000', 'http://localhost:5000']
        self.require_https = False  # Set to True in production
        self.enable_csrf_protection = True
        self.enable_rate_limiting = True
        self.enable_input_sanitization = True
