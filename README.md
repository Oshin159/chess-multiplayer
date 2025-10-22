# Emotional Chess Multiplayer 🎭❤️😡😢

A multiplayer chess system with emotional mechanics, real-time gameplay, and secure session management. Built on top of `python-chess` with Flask, WebSocket support, and modern deployment options.

## 🌟 Features

### **Core Chess Mechanics**
- **Love ❤️**: Between opposite sides, prevents capture/check
- **Anger 😡**: Within same side, grants +1 movement range  
- **Sad 😢**: Love-side reaction, freezes movement

### **Multiplayer Features**
- **Real-time Gameplay**: WebSocket-based multiplayer chess
- **Session Security**: JWT token authentication and CSRF protection
- **Database Persistence**: SQLite with automatic game recovery
- **Game Discovery**: Browse and join existing games
- **Turn-based Validation**: Secure move validation and turn management

### **Deployment Ready**
- **Railway**: Backend deployment with persistent database
- **Netlify**: Frontend deployment with automatic HTTPS
- **Production Security**: Rate limiting, input validation, session management

## 🚀 Quick Start

### **Local Development**

```bash
# Clone the repository
git clone <your-repo-url>
cd chess

# Install dependencies
pip install -r requirements.txt

# Initialize database
python migrate.py --action init

# Start the server
python run_server.py
```

Visit `http://localhost:5001` to play!

### **Production Deployment**

#### **Option 1: Railway + Netlify (Recommended)**

**Backend (Railway):**
1. Push code to GitHub
2. Connect to [Railway](https://railway.app)
3. Deploy with environment variables
4. Get your backend URL

**Frontend (Netlify):**
1. Update `BACKEND_URL` in `frontend/index.html`
2. Deploy to [Netlify](https://netlify.com)
3. Get your frontend URL

#### **Option 2: All-in-One Railway**

Deploy both backend and frontend to Railway with automatic HTTPS.

## 📦 Installation

```bash
# Install all dependencies
pip install -r requirements.txt

# For development
pip install -r requirements.txt
```

## Quick Start

```python
import chess
from emotional_board import EmotionalBoard

# Create emotional chess board
board = EmotionalBoard()

# Make moves (emotions form automatically)
board.push_san("e4")
board.push_san("e5")

# Check emotional states
print(board.emotion_summary())
# Output: {'love_pairs': 0, 'angry': 0, 'sad': 0}

# Get emFEN (extended FEN with emotions)
emfen = board.to_emfen()
print(emfen)
# Output: rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1

# Load from emFEN
board2 = EmotionalBoard(emfen)
```

## Emotional Mechanics

### ❤️ Love (Between Opposite Sides)

**Formation:**
- Pieces within Chebyshev distance ≤ 3
- Neither in check
- Neither already in love
- Queens cannot form love
- Kings can only love opposite-color pieces (not Kings)

**Effects:**
- Lovers cannot capture each other
- Lovers ignore each other's attack zones
- Love ends if distance > 3, either enters check, or one is captured

```python
# Check if piece is in love
if board.in_love(chess.E2):
    print("This piece is in love!")

# Get love partner
partner = board.love_partner[chess.E2]
if partner:
    print(f"Loving piece at {chess.square_name(partner)}")
```

### 😡 Anger (Within Same Side)

**Trigger:**
- When friendly piece is threatened or captured
- All allied pieces within distance ≤ 3 become angry

**Effects:**
- +1 movement range for 1 turn
- Knights unaffected
- Cannot stack

```python
# Check if piece is angry
if board.is_angry(chess.E4):
    print("This piece is angry and has extended movement!")

# Anger lasts 1 turn
board.angry_turns[chess.E4] = 1
```

### 😢 Sad (Love-Side Reaction)

**Trigger:**
- When a piece's lover is captured
- Surviving lover becomes sad

**Effects:**
- Cannot move for 1 turn
- Kings cannot become sad
- Can move only to resolve check

```python
# Check if piece is sad
if board.is_sad(chess.G2):
    print("This piece is sad and cannot move!")

# Sadness lasts 1 turn
board.sad_turns[chess.G2] = 1
```

## Advanced Usage

### emFEN (Emotional FEN)

Extended FEN format that includes emotional states:

```
<base_fen> | L: a2-b5,c4-d7 | A: e4,f7 | S: g2
```

```python
from emfen import EmFEN

# Encode board to emFEN
emfen = EmFEN.encode(board)

# Decode emFEN to board
EmFEN.decode(emfen, board)

# Validate emFEN
if EmFEN.validate(emfen):
    print("Valid emFEN!")
```

### Position Evaluation

```python
from evaluation import EmotionalEvaluator

# Create evaluator
evaluator = EmotionalEvaluator(board)

# Get total evaluation
score = evaluator.evaluate_position()
print(f"Position score: {score}")

# Get detailed breakdown
details = evaluator.get_detailed_evaluation()
print(f"Material: {details['material']}")
print(f"Love bonus: {details['love_bonus']}")
print(f"Anger bonus: {details['anger_bonus']}")
print(f"Sad penalty: {details['sad_penalty']}")

# Get emotion impact per side
impact = evaluator.get_emotion_impact()
print(f"White emotions: {impact['white']}")
print(f"Black emotions: {impact['black']}")
```

### Move Generation

```python
# Get legal moves considering emotions
legal_moves = board.generate_legal_moves()

# Filter moves for specific piece
e4_moves = board.generate_legal_moves(chess.BB_SQUARES[chess.E4])

# Check if move is legal (considers emotions)
move = chess.Move(chess.E2, chess.E4)
if move in legal_moves:
    print("Move is legal!")
```

## Configuration

```python
# Emotional constants
LOVE_DISTANCE = 3      # Max distance for love formation
LOVE_BONUS = 30        # Evaluation bonus for love
ANGER_BONUS = 10       # Evaluation bonus for anger
SAD_PENALTY = 25       # Evaluation penalty for sadness
```

## Testing

Run the comprehensive test suite:

```bash
pytest test_emotions.py -v
```

Tests cover:
- Love formation and dissolution
- Anger triggers and effects
- Sadness mechanics
- emFEN serialization
- Position evaluation
- Move generation with emotions

## Example Game

```python
# Start new game
board = EmotionalBoard()

# Make opening moves
board.push_san("e4")
board.push_san("e5")
board.push_san("Nf3")
board.push_san("Nc6")

# Update emotional states
board.update_love_states()

# Check emotions
summary = board.emotion_summary()
print(f"Love pairs: {summary['love_pairs']}")
print(f"Angry pieces: {summary['angry']}")
print(f"Sad pieces: {summary['sad']}")

# Get position evaluation
evaluator = EmotionalEvaluator(board)
score = evaluator.evaluate_position()
print(f"Position score: {score}")

# Save game state
emfen = board.to_emfen()
print(f"Game state: {emfen}")
```

## Architecture

- **EmotionalBoard**: Main class extending `chess.Board`
- **EmFEN**: Serialization/deserialization of emotional states
- **EmotionalEvaluator**: Position evaluation with emotional bonuses
- **Test Suite**: Comprehensive unit tests for all mechanics

## Contributing

The system is designed to be modular and extensible. New emotional mechanics can be added by:

1. Adding new state tracking arrays
2. Implementing formation/trigger logic
3. Updating move generation
4. Adding evaluation bonuses/penalties
5. Extending emFEN format

## 🚀 Production Deployment

### **Railway Deployment (Backend)**

Railway is perfect for your Python Flask + WebSocket application with persistent database.

#### **Step 1: Prepare Your Code**

```bash
# Ensure all files are committed
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

#### **Step 2: Deploy to Railway**

1. **Go to [Railway](https://railway.app)**
2. **Sign up with GitHub**
3. **Click "New Project" → "Deploy from GitHub repo"**
4. **Select your chess repository**
5. **Railway will automatically detect Python and install dependencies**

#### **Step 3: Configure Environment Variables**

In Railway dashboard, add these environment variables:

```bash
FLASK_DEBUG=False
SECRET_KEY=your-secure-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///chess_games.db
HOST=0.0.0.0
PORT=5001
```

**Generate secure keys:**
```python
import secrets
print(secrets.token_urlsafe(32))  # Use for SECRET_KEY
print(secrets.token_urlsafe(32))   # Use for JWT_SECRET_KEY
```

#### **Step 4: Test Your Deployment**

```bash
# Test health endpoint
curl https://your-app.railway.app/api/health

# Expected response:
{
  "success": true,
  "status": "healthy",
  "database_connected": true,
  "active_games": 0,
  "active_players": 0
}
```

#### **Railway Features:**
- ✅ **Persistent Database**: SQLite with automatic backups
- ✅ **WebSocket Support**: Real-time multiplayer
- ✅ **Automatic HTTPS**: Secure connections
- ✅ **Environment Variables**: Easy configuration
- ✅ **Custom Domains**: Professional URLs
- ✅ **Auto-deploy**: GitHub integration

---

### **Netlify Deployment (Frontend)**

Netlify provides fast, secure hosting for your frontend with automatic HTTPS.

#### **Step 1: Update Backend URL**

Edit `frontend/index.html`:
```javascript
// Update this line with your Railway backend URL
const BACKEND_URL = 'https://your-app.railway.app';
```

#### **Step 2: Deploy to Netlify**

1. **Go to [Netlify](https://netlify.com)**
2. **Sign up with GitHub**
3. **Click "New site from Git"**
4. **Select your repository**
5. **Configure build settings:**
   - **Base directory:** `frontend`
   - **Build command:** (leave empty)
   - **Publish directory:** `frontend`

#### **Step 3: Configure Redirects**

Netlify will automatically use your `netlify.toml` configuration for API redirects.

#### **Step 4: Test Your Frontend**

Visit your Netlify URL and test:
- ✅ Game creation
- ✅ Player joining
- ✅ Real-time moves
- ✅ WebSocket connection

#### **Netlify Features:**
- ✅ **Automatic HTTPS**: Secure by default
- ✅ **Global CDN**: Fast worldwide
- ✅ **Custom Domains**: Professional URLs
- ✅ **Form Handling**: Contact forms
- ✅ **Branch Deploys**: Preview deployments

---

### **Alternative: All-in-One Railway**

Deploy both backend and frontend to Railway:

#### **Step 1: Update Railway Configuration**

Add to your `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python run_server.py",
    "healthcheckPath": "/api/health"
  }
}
```

#### **Step 2: Serve Frontend from Flask**

Your `run_server.py` already serves the frontend at the root path.

#### **Step 3: Deploy**

Railway will serve both your API and frontend from the same URL.

---

## 🔧 Environment Configuration

### **Required Environment Variables**

```bash
# Core Settings
FLASK_DEBUG=False
SECRET_KEY=your-secure-secret-key-here
HOST=0.0.0.0
PORT=5001

# Security
JWT_SECRET_KEY=your-jwt-secret-key-here
SESSION_TIMEOUT_HOURS=24
RATE_LIMIT_ENABLED=True

# Database
DATABASE_URL=sqlite:///chess_games.db

# CORS (update with your frontend domain)
ALLOWED_ORIGINS=https://your-app.netlify.app,https://your-app.railway.app
```

### **Security Best Practices**

1. **Generate Strong Keys:**
   ```python
   import secrets
   # Use these for SECRET_KEY and JWT_SECRET_KEY
   print(secrets.token_urlsafe(32))
   ```

2. **Update CORS Origins:**
   - Add your frontend domain to `ALLOWED_ORIGINS`
   - Remove localhost in production

3. **Database Security:**
   - Regular backups
   - Connection limits
   - Consider PostgreSQL for high-traffic

---

## 📊 Monitoring & Maintenance

### **Health Checks**

Your app includes built-in monitoring:

```bash
# Basic health check
curl https://your-app.railway.app/api/health

# Database statistics
python migrate.py --action stats

# Cleanup expired sessions
python migrate.py --action cleanup
```

### **Database Management**

```bash
# Backup database
python migrate.py --action backup

# View statistics
python migrate.py --action stats

# Cleanup expired data
python migrate.py --action cleanup

# Reset database (⚠️ DANGER)
python migrate.py --action reset
```

### **Logs & Debugging**

- **Railway**: Built-in logging dashboard
- **Netlify**: Function logs in dashboard
- **Local**: Check console output

---

## 🎮 Multiplayer Features

### **Game Flow**

1. **Player Setup**
   - Enter name
   - Create game or join existing

2. **Game Lobby**
   - See all players
   - Wait for enough players
   - Start when ready

3. **Gameplay**
   - Turn-based moves
   - Real-time synchronization
   - Live emotion tracking

4. **Game End**
   - Winner announcement
   - Statistics
   - Play again option

### **Security Features**

- ✅ **JWT Session Tokens**: Secure authentication
- ✅ **CSRF Protection**: Cross-site request forgery prevention
- ✅ **Input Validation**: All inputs sanitized and validated
- ✅ **Rate Limiting**: Protection against abuse
- ✅ **Turn Validation**: Only current player can move

### **Real-time Features**

- ✅ **WebSocket Connection**: Live updates
- ✅ **Game State Sync**: All players see moves instantly
- ✅ **Player Management**: Join/leave notifications
- ✅ **Emotion Tracking**: Live emotional state updates

---

## 🛠️ Development

### **Local Development**

```bash
# Start development server
python run_server.py

# Run tests
python test_security.py

# Database management
python migrate.py --action init
python migrate.py --action stats
```

### **API Endpoints**

```bash
# Health check
GET /api/health

# Game management
POST /api/games
GET /api/games
GET /api/games/{game_id}

# Player actions
POST /api/games/{game_id}/join
POST /api/games/{game_id}/start
POST /api/games/{game_id}/move

# Session management
POST /api/session/validate
POST /api/session/refresh
```

### **WebSocket Events**

```javascript
// Client-side WebSocket usage
const socket = io('https://your-app.railway.app');

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('move_made', (data) => {
    console.log('Move made:', data.move);
    updateGameState(data.game);
});

socket.emit('join_game_room', {
    game_id: 'your-game-id',
    player_id: 'your-player-id'
});
```

---

## 📁 Project Structure

```
chess/
├── frontend/                 # Netlify deployment
│   ├── index.html          # Main game interface
│   └── netlify.toml        # Netlify configuration
├── database.py              # SQLite database management
├── security.py              # JWT tokens and validation
├── game_models.py           # Game logic and persistence
├── game_api.py              # Flask API endpoints
├── run_server.py            # Production server
├── migrate.py               # Database management
├── deploy.sh                # Deployment helper
├── requirements.txt         # Python dependencies
├── railway.json             # Railway configuration
├── Procfile                 # Heroku configuration
└── DEPLOYMENT.md            # Detailed deployment guide
```

---

## 🎯 Deployment Checklist

### **Before Deployment**
- [ ] Code pushed to GitHub
- [ ] Environment variables configured
- [ ] Backend URL updated in frontend
- [ ] Database initialized
- [ ] Security keys generated

### **After Deployment**
- [ ] Health check passes
- [ ] Frontend loads correctly
- [ ] WebSocket connection works
- [ ] Game creation/joining works
- [ ] Moves sync in real-time
- [ ] HTTPS enabled

### **Production Checklist**
- [ ] Strong secret keys
- [ ] CORS origins configured
- [ ] Rate limiting enabled
- [ ] Database backups scheduled
- [ ] Monitoring set up
- [ ] Custom domain configured

---

## 🆘 Troubleshooting

### **Common Issues**

**Backend not starting:**
```bash
# Check logs
railway logs

# Verify environment variables
railway variables
```

**Frontend not connecting:**
```bash
# Check CORS settings
# Verify BACKEND_URL in frontend/index.html
# Test API directly: curl https://your-app.railway.app/api/health
```

**Database issues:**
```bash
# Initialize database
python migrate.py --action init

# Check database stats
python migrate.py --action stats
```

### **Support**

- **Railway**: [Railway Documentation](https://docs.railway.app/)
- **Netlify**: [Netlify Documentation](https://docs.netlify.com/)
- **Project Issues**: Create GitHub issue

---

## License

This project extends the `python-chess` library and follows the same licensing terms.
