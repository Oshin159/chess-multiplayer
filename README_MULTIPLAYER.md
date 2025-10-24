# 🎭 Emotional Chess Multiplayer

A complete multiplayer implementation of Emotional Chess with real-time WebSocket support, REST API, and web interface.

## 🌟 Features

### Core Emotional Mechanics
- **❤️ Love**: Pieces form love relationships when close (≤3 squares)
- **😡 Anger**: Pieces get angry when allies are captured/threatened
- **😢 Sadness**: Pieces become sad when their lovers are captured

### Multiplayer Features
- **2-6 Players**: Support for 2 to 6 players per game
- **Real-time Updates**: WebSocket support for instant game updates
- **REST API**: Complete REST API for game management
- **Web Interface**: Beautiful HTML5 interface with real-time gameplay
- **Game Lobbies**: Create and join games with custom settings
- **Turn Management**: Automatic turn rotation and validation

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Activate virtual environment
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python run_server.py
```

The server will start at `http://localhost:5000`

### 3. Play the Game
- Open your browser to `http://localhost:5000`
- Create a new game or join an existing one
- Start playing with real-time emotional mechanics!

## 🎮 How to Play

### Creating a Game
1. Enter your name
2. Choose a game name
3. Select number of players (2-6)
4. Click "Create Game"
5. Share the Game ID with other players

### Joining a Game
1. Enter your name
2. Enter the Game ID
3. Click "Join Game"
4. Wait for the game to start

### Making Moves
- **Click to Move**: Click on a piece, then click where to move
- **Notation**: Enter moves in standard chess notation (e4, Nf3, O-O, etc.)
- **Emotions**: Watch as love, anger, and sadness affect the game!

## 🔧 API Reference

### REST Endpoints

#### Health Check
```http
GET /api/health
```

#### Create Game
```http
POST /api/games
Content-Type: application/json

{
  "name": "My Game",
  "max_players": 2
}
```

#### Join Game
```http
POST /api/games/{game_id}/join
Content-Type: application/json

{
  "name": "Player Name",
  "color": "white"  // optional
}
```

#### Start Game
```http
POST /api/games/{game_id}/start
```

#### Make Move
```http
POST /api/games/{game_id}/move
Content-Type: application/json

{
  "player_id": "player_id",
  "move": "e4"
}
```

#### Get Game State
```http
GET /api/games/{game_id}
```

### WebSocket Events

#### Client → Server
- `join_game_room`: Join a game room for updates
- `make_move`: Make a move via WebSocket
- `start_game`: Start a game
- `get_game_state`: Get current game state

#### Server → Client
- `connected`: Connection established
- `joined_room`: Successfully joined game room
- `move_made`: Move was made by any player
- `game_started`: Game has started
- `game_ended`: Game has finished
- `error`: Error occurred

## 🎯 Game Rules

### Emotional Mechanics

#### Love ❤️
- **Formation**: Pieces within 3 squares of opposite-color pieces
- **Effects**: Cannot capture or check each other
- **Dissolution**: Distance > 3, one enters check, or one is captured

#### Anger 😡
- **Trigger**: Friendly piece captured or threatened
- **Effects**: +1 movement range for 1 turn (except knights)
- **Duration**: 1 turn only

#### Sadness 😢
- **Trigger**: Lover is captured
- **Effects**: Cannot move for 1 turn (except kings)
- **Duration**: 1 turn only

### Multiplayer Rules
- **Turn Order**: White → Black → Red → Blue → Green → Yellow
- **Game Start**: Requires minimum 2 players
- **Game End**: Checkmate, stalemate, or all players leave
- **Disconnection**: Players can rejoin if they disconnect

## 🧪 Testing

### Run Unit Tests
```bash
# Test emotional mechanics
python -m pytest test_emotions.py -v

# Test API
python test_api.py -v
```

### Test API Manually
```bash
# Start server in one terminal
python run_server.py

# Run demo in another terminal
python demo_api.py
```

## 📁 Project Structure

```
chess/
├── emotional_board.py      # Core EmotionalBoard class
├── emfen.py                # Extended FEN serialization
├── evaluation.py           # Position evaluation
├── game_models.py          # Game state and player management
├── game_api.py             # Flask API with WebSocket
├── run_server.py           # Server runner
├── demo_api.py             # API usage demo
├── test_api.py             # API tests
├── templates/
│   └── index.html          # Web interface
├── requirements.txt         # Dependencies
└── README_MULTIPLAYER.md   # This file
```

## 🔌 Integration Examples

### Python Client
```python
from demo_api import EmotionalChessClient

client = EmotionalChessClient("http://localhost:5000")

# Create and join a game
game = client.create_game("My Game", 2)
player = client.join_game(game['game_id'], "Player 1")
client.start_game(game['game_id'])

# Make a move
result = client.make_move(game['game_id'], player['player_id'], "e4")
print(f"Move result: {result}")
```

### JavaScript Client
```javascript
const socket = io('http://localhost:5000');

// Join a game room
socket.emit('join_game_room', {
    game_id: 'your-game-id',
    player_id: 'your-player-id'
});

// Listen for moves
socket.on('move_made', (data) => {
    console.log(`${data.player_id} played ${data.move}`);
    updateBoard(data.game);
});

// Make a move
socket.emit('make_move', {
    game_id: 'your-game-id',
    player_id: 'your-player-id',
    move: 'e4'
});
```

## 🎨 Customization

### Adding New Emotions
1. Extend the `EmotionalBoard` class
2. Add emotion tracking arrays
3. Implement formation/dissolution logic
4. Update the emFEN format
5. Add evaluation bonuses

### Custom Game Rules
1. Modify `Game` class in `game_models.py`
2. Update turn order logic
3. Add custom win conditions
4. Implement special moves

### UI Customization
1. Edit `templates/index.html`
2. Modify CSS styles
3. Add new WebSocket events
4. Implement custom board themes

## 🚀 Deployment

### Production Setup
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 game_api:app
```

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "run_server.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🎉 Enjoy Playing!

Have fun exploring the emotional depths of chess! Remember:
- Love conquers all, but distance breaks hearts
- Anger gives strength, but only briefly
- Sadness freezes movement, but kings never give up

Happy gaming! 🎭♟️


