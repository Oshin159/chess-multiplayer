# 🚀 Deployment Guide for Emotional Chess

This guide covers deploying your Emotional Chess multiplayer application to various platforms.

## 🎯 **Recommended Platforms**

### **1. Railway (Best for Python + WebSocket)**

Railway is perfect for your Flask + WebSocket application with persistent database.

#### **Deployment Steps:**

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy from GitHub**
   ```bash
   # Push your code to GitHub first
   git add .
   git commit -m "Add deployment configuration"
   git push origin main
   ```

3. **Connect Repository**
   - In Railway dashboard, click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your chess repository

4. **Configure Environment Variables**
   ```bash
   FLASK_DEBUG=False
   SECRET_KEY=your-secure-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   DATABASE_URL=sqlite:///chess_games.db
   ```

5. **Deploy**
   - Railway will automatically detect the Python app
   - It will install dependencies from `requirements.txt`
   - Your app will be available at `https://your-app.railway.app`

#### **Railway Features:**
- ✅ Persistent database (SQLite)
- ✅ WebSocket support
- ✅ Automatic HTTPS
- ✅ Environment variables
- ✅ Custom domains
- ✅ Auto-deploy from GitHub

---

### **2. Render (Alternative)**

Render is another good option for Python applications.

#### **Deployment Steps:**

1. **Create render.yaml**
   ```yaml
   services:
     - type: web
       name: emotional-chess
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: python run_server.py
       envVars:
         - key: FLASK_DEBUG
           value: False
         - key: SECRET_KEY
           generateValue: true
   ```

2. **Deploy to Render**
   - Connect your GitHub repository
   - Render will automatically deploy

---

### **3. Heroku (Classic Option)**

#### **Deployment Steps:**

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Login
   heroku login
   ```

2. **Create Heroku App**
   ```bash
   heroku create your-chess-app
   ```

3. **Configure Environment**
   ```bash
   heroku config:set FLASK_DEBUG=False
   heroku config:set SECRET_KEY=your-secret-key
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

---

## 🔧 **Production Configuration**

### **Environment Variables**

Create these environment variables in your deployment platform:

```bash
# Core settings
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
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://your-app.railway.app
```

### **Security Considerations**

1. **Generate Strong Keys**
   ```python
   import secrets
   print(secrets.token_urlsafe(32))  # Use this for SECRET_KEY
   print(secrets.token_urlsafe(32))   # Use this for JWT_SECRET_KEY
   ```

2. **Update CORS Origins**
   - Add your frontend domain to `ALLOWED_ORIGINS`
   - Remove localhost in production

3. **Database Security**
   - Consider using PostgreSQL for production
   - Regular backups
   - Connection limits

---

## 🌐 **Frontend Deployment (Netlify)**

Since your backend is Python, you'll need a separate frontend for Netlify.

### **Option 1: Static HTML Frontend**

Create a simple HTML frontend that connects to your Railway backend:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Emotional Chess</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
</head>
<body>
    <div id="app">
        <h1>🎭 Emotional Chess</h1>
        <div id="game-board"></div>
        <div id="controls">
            <input type="text" id="player-name" placeholder="Your name">
            <button onclick="joinGame()">Join Game</button>
        </div>
    </div>
    
    <script>
        // Connect to your Railway backend
        const socket = io('https://your-app.railway.app');
        
        function joinGame() {
            const playerName = document.getElementById('player-name').value;
            // Implement game logic here
        }
    </script>
</body>
</html>
```

### **Option 2: React/Vue Frontend**

Create a modern frontend that connects to your backend:

```bash
# Create React frontend
npx create-react-app chess-frontend
cd chess-frontend

# Install dependencies
npm install socket.io-client axios
```

---

## 📊 **Monitoring & Maintenance**

### **Health Checks**

Your app includes health check endpoints:
- `GET /api/health` - Basic health check
- `POST /api/admin/cleanup` - Clean up expired sessions

### **Database Management**

```bash
# Backup database
python migrate.py --action backup

# View statistics
python migrate.py --action stats

# Cleanup expired data
python migrate.py --action cleanup
```

### **Logs**

Monitor your application logs:
- Railway: Built-in logging dashboard
- Render: Logs tab in dashboard
- Heroku: `heroku logs --tail`

---

## 🚀 **Quick Start (Railway)**

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Add environment variables
   - Deploy!

3. **Test Your Deployment**
   ```bash
   curl https://your-app.railway.app/api/health
   ```

4. **Create Frontend (Optional)**
   - Deploy a simple HTML frontend to Netlify
   - Connect it to your Railway backend

---

## 🔗 **Useful Links**

- [Railway Documentation](https://docs.railway.app/)
- [Render Documentation](https://render.com/docs)
- [Heroku Python Guide](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Socket.IO Documentation](https://socket.io/docs/)

Your Emotional Chess application is now ready for production deployment! 🎉
