# 🚂 Railway Deployment Guide for Emotional Chess

This guide shows you how to deploy your Emotional Chess multiplayer application to Railway with both backend and frontend.

## 📋 **Railway Configuration**

### **1. Current Railway Configuration**

Your `railway.json` is already configured for Railway deployment:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python run_server.py",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### **2. How Railway Serves Your Frontend**

Railway will automatically serve your frontend because:

- ✅ **`run_server.py`** serves the frontend at the root path (`/`)
- ✅ **Static files** are served from the `frontend/` directory
- ✅ **API endpoints** are available at `/api/*`
- ✅ **WebSocket support** is enabled for real-time gameplay

## 🚀 **Deployment Steps**

### **Step 1: Prepare Your Repository**

```bash
# Ensure all files are committed
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### **Step 2: Deploy to Railway**

1. **Go to [Railway.app](https://railway.app)**
2. **Sign up/Login with GitHub**
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your chess repository**
6. **Railway will automatically detect Python and deploy**

### **Step 3: Configure Environment Variables**

In Railway dashboard, add these environment variables:

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

# CORS (update with your Railway domain)
ALLOWED_ORIGINS=https://your-app.railway.app
```

### **Step 4: Generate Secure Keys**

```python
import secrets
print("SECRET_KEY=" + secrets.token_urlsafe(32))
print("JWT_SECRET_KEY=" + secrets.token_urlsafe(32))
```

## 🔧 **Railway-Specific Configuration**

### **1. Automatic Frontend Serving**

Railway will serve your application at:
- **Frontend**: `https://your-app.railway.app/` (main page)
- **API**: `https://your-app.railway.app/api/*` (REST endpoints)
- **WebSocket**: `https://your-app.railway.app/socket.io/` (real-time)

### **2. Database Persistence**

Railway provides persistent storage for your SQLite database:
- ✅ **Automatic persistence** between deployments
- ✅ **No configuration needed** - just works
- ✅ **Survives restarts** and scaling events

### **3. Environment Variables**

Railway automatically provides:
- ✅ **`PORT`** - Railway assigns the port
- ✅ **`HOST`** - Set to `0.0.0.0` for Railway
- ✅ **Persistent storage** for SQLite database

## 📊 **Railway Features You Get**

### **Automatic Features:**
- ✅ **HTTPS**: Automatic SSL certificates
- ✅ **Custom Domains**: Add your own domain
- ✅ **Auto-deploy**: Deploys on every GitHub push
- ✅ **Logs**: Real-time application logs
- ✅ **Metrics**: CPU, memory, and network usage
- ✅ **Scaling**: Automatic scaling based on traffic

### **Database Features:**
- ✅ **SQLite Persistence**: Database survives restarts
- ✅ **Automatic Backups**: Railway handles backups
- ✅ **No Configuration**: Works out of the box

### **WebSocket Support:**
- ✅ **Real-time Communication**: WebSocket support enabled
- ✅ **Multiplayer Sync**: Live game updates
- ✅ **Session Management**: JWT token authentication

## 🎯 **Deployment Checklist**

### **Before Deployment:**
- [ ] **Code pushed to GitHub** ✅
- [ ] **Environment variables ready** ✅
- [ ] **Railway configuration complete** ✅
- [ ] **Database schema ready** ✅

### **After Deployment:**
- [ ] **Health check passes**: `curl https://your-app.railway.app/api/health`
- [ ] **Frontend loads**: Visit `https://your-app.railway.app/`
- [ ] **WebSocket works**: Real-time connection established
- [ ] **Database connected**: Games persist between sessions
- [ ] **HTTPS enabled**: Secure connections working

## 🔍 **Testing Your Deployment**

### **1. Health Check**
```bash
curl https://your-app.railway.app/api/health
```

Expected response:
```json
{
  "success": true,
  "status": "healthy",
  "database_connected": true,
  "active_games": 0,
  "active_players": 0
}
```

### **2. Frontend Test**
1. **Visit**: `https://your-app.railway.app/`
2. **Check**: Chess pieces are visible
3. **Test**: Game rules section works
4. **Verify**: WebSocket connection established

### **3. Multiplayer Test**
1. **Create game** in one browser
2. **Join game** in another browser
3. **Make moves** and verify real-time sync
4. **Check emotions** are tracked correctly

## 🛠️ **Railway Dashboard Features**

### **Monitoring:**
- **Deployments**: See build history and status
- **Logs**: Real-time application logs
- **Metrics**: Performance monitoring
- **Variables**: Environment variable management

### **Configuration:**
- **Domains**: Add custom domains
- **Environment**: Manage environment variables
- **Settings**: Configure restart policies
- **Scaling**: Set resource limits

## 🚨 **Troubleshooting**

### **Common Issues:**

**Build Fails:**
- Check Railway logs for error messages
- Verify all dependencies in `requirements.txt`
- Ensure Python version compatibility

**Frontend Not Loading:**
- Verify `run_server.py` serves frontend correctly
- Check if static files are being served
- Look for CORS issues in browser console

**Database Issues:**
- Railway automatically handles SQLite persistence
- Check if database file is being created
- Verify environment variables are set

**WebSocket Issues:**
- Railway supports WebSockets out of the box
- Check Socket.IO configuration
- Verify CORS settings

## 📈 **Performance Optimization**

### **Railway Optimizations:**
- ✅ **Automatic scaling** based on traffic
- ✅ **CDN integration** for static assets
- ✅ **Database optimization** with SQLite
- ✅ **Memory management** for Python apps

### **Application Optimizations:**
- ✅ **Connection pooling** for database
- ✅ **Session cleanup** for expired tokens
- ✅ **Rate limiting** for API protection
- ✅ **Input validation** for security

## 🎉 **Your Deployed Application**

After successful deployment, your Emotional Chess game will be available at:

- **URL**: `https://your-app.railway.app`
- **Features**: Full multiplayer chess with emotions
- **Database**: Persistent SQLite storage
- **WebSocket**: Real-time multiplayer sync
- **Security**: JWT authentication and CSRF protection

## 🔗 **Next Steps**

1. **Test your deployment** thoroughly
2. **Share the URL** with friends to test multiplayer
3. **Monitor performance** in Railway dashboard
4. **Add custom domain** if desired
5. **Set up monitoring** and alerts

Your Emotional Chess multiplayer game is now live on Railway! 🎉
