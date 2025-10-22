# Emotional Chess - Security & Persistence Guide

This document explains the security and state management features implemented in the Emotional Chess multiplayer application.

## 🔐 Security Features

### Session Management
- **JWT Tokens**: All player sessions use secure JWT tokens with expiration
- **Session Validation**: Every protected endpoint validates session tokens
- **Token Refresh**: Players can refresh their session tokens before expiration
- **Automatic Cleanup**: Expired sessions are automatically cleaned up

### Authentication & Authorization
- **Player Authentication**: Players must join games with valid session tokens
- **Game Access Control**: Players can only access games they're part of
- **Move Authorization**: Only the current player can make moves
- **CSRF Protection**: Cross-site request forgery protection for state-changing operations

### Input Validation & Sanitization
- **Move Validation**: Chess move notation is validated before processing
- **Player Name Validation**: Player names are sanitized and validated
- **Color Validation**: Player colors are validated against allowed values
- **Input Sanitization**: All user inputs are sanitized to prevent injection attacks

### Rate Limiting
- **API Rate Limits**: Endpoints have configurable rate limits
- **Move Rate Limiting**: Players are limited in how many moves they can make per minute
- **Game Creation Limits**: Limits on how many games can be created per time period

## 💾 State Persistence

### Database Storage
- **SQLite Database**: All game state is persisted to SQLite database
- **Automatic Recovery**: Games are automatically restored from database on server restart
- **Transaction Safety**: Database operations use transactions for consistency
- **Indexed Queries**: Database is optimized with proper indexes

### Data Models
- **Games**: Complete game state including board, players, and status
- **Players**: Player information with connection tracking
- **Moves**: Complete move history with timestamps and emotions
- **Sessions**: Player session tokens with expiration tracking

### Backup & Recovery
- **Database Backups**: Automated backup functionality
- **Migration Scripts**: Database initialization and migration tools
- **Cleanup Tools**: Automated cleanup of expired data

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python migrate.py --action init
```

### 3. Start Server
```bash
python run_server.py
```

## 📊 Database Management

### Initialize Database
```bash
python migrate.py --action init --db-path chess_games.db
```

### Backup Database
```bash
python migrate.py --action backup --db-path chess_games.db
```

### Restore Database
```bash
python migrate.py --action restore --backup-path chess_games.db.backup.1234567890 --db-path chess_games.db
```

### View Statistics
```bash
python migrate.py --action stats --db-path chess_games.db
```

### Cleanup Expired Data
```bash
python migrate.py --action cleanup --db-path chess_games.db
```

### Reset Database (⚠️ DANGER)
```bash
python migrate.py --action reset --db-path chess_games.db
```

## 🔧 API Security

### Protected Endpoints
All game-modifying endpoints require valid session tokens:

```bash
# Headers required for protected endpoints
Authorization: Bearer <session_token>
X-CSRF-Token: <csrf_token>
```

### Session Token Format
```json
{
  "player_id": "uuid",
  "game_id": "uuid", 
  "iat": 1234567890,
  "exp": 1234567890,
  "type": "session"
}
```

### Example API Usage

#### 1. Create Game
```bash
curl -X POST http://localhost:5000/api/games \
  -H "Content-Type: application/json" \
  -d '{"name": "My Game", "max_players": 2}'
```

#### 2. Join Game
```bash
curl -X POST http://localhost:5000/api/games/{game_id}/join \
  -H "Content-Type: application/json" \
  -d '{"name": "Player1", "color": "white"}'
```

#### 3. Make Move (Protected)
```bash
curl -X POST http://localhost:5000/api/games/{game_id}/move \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <session_token>" \
  -H "X-CSRF-Token: <csrf_token>" \
  -d '{"move": "e4"}'
```

#### 4. Validate Session
```bash
curl -X POST http://localhost:5000/api/session/validate \
  -H "Content-Type: application/json" \
  -d '{"session_token": "<token>"}'
```

#### 5. Refresh Session
```bash
curl -X POST http://localhost:5000/api/session/refresh \
  -H "Authorization: Bearer <session_token>"
```

## 🛡️ Security Configuration

### Security Settings
```python
class SecurityConfig:
    max_players_per_game = 6
    max_games_per_player = 5
    max_moves_per_game = 1000
    session_timeout_minutes = 30
    rate_limit_requests_per_minute = 60
    max_player_name_length = 50
    allowed_origins = ['http://localhost:3000', 'http://localhost:5000']
    require_https = False  # Set to True in production
    enable_csrf_protection = True
    enable_rate_limiting = True
    enable_input_sanitization = True
```

### JWT Configuration
```python
# Token expiry: 24 hours
# Algorithm: HS256
# Secret key: Auto-generated secure key
```

## 🔍 Monitoring & Maintenance

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Admin Cleanup
```bash
curl -X POST http://localhost:5000/api/admin/cleanup
```

### Database Statistics
```bash
python migrate.py --action stats
```

## 🚨 Security Best Practices

### Production Deployment
1. **Change Secret Key**: Use a strong, unique secret key
2. **Enable HTTPS**: Set `require_https = True`
3. **Configure CORS**: Set proper allowed origins
4. **Database Security**: Use database authentication
5. **Regular Backups**: Schedule regular database backups
6. **Monitor Logs**: Monitor for suspicious activity

### Session Management
1. **Token Expiry**: Sessions expire after 24 hours
2. **Secure Storage**: Store tokens securely on client side
3. **Token Refresh**: Refresh tokens before expiration
4. **Logout**: Properly invalidate tokens on logout

### Input Validation
1. **All Inputs**: Validate and sanitize all user inputs
2. **Move Validation**: Validate chess move notation
3. **Name Validation**: Validate player names
4. **Rate Limiting**: Implement appropriate rate limits

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database file exists
ls -la chess_games.db

# Initialize if missing
python migrate.py --action init
```

#### Session Token Issues
```bash
# Validate token
curl -X POST http://localhost:5000/api/session/validate \
  -d '{"session_token": "your_token"}'

# Refresh token
curl -X POST http://localhost:5000/api/session/refresh \
  -H "Authorization: Bearer your_token"
```

#### Permission Denied
- Check session token is valid
- Verify player is in the correct game
- Ensure CSRF token is provided for state-changing operations

### Logs and Debugging
- Check server logs for error messages
- Use database statistics to monitor state
- Validate session tokens when debugging authentication issues

## 📈 Performance Considerations

### Database Optimization
- Indexes on frequently queried columns
- Regular cleanup of expired sessions
- Connection pooling for high-traffic scenarios

### Memory Management
- Games loaded on-demand from database
- Automatic cleanup of abandoned games
- Efficient session token validation

### Scalability
- Stateless server design
- Database-backed persistence
- Horizontal scaling support (with shared database)

This security and persistence system provides a robust foundation for the Emotional Chess multiplayer application while maintaining simplicity and ease of use.
