#!/bin/bash

# 🚀 Emotional Chess Deployment Script
# This script helps deploy your chess application to various platforms

echo "🎭 Emotional Chess Deployment Helper"
echo "====================================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the chess project root directory"
    exit 1
fi

echo "📋 Available deployment options:"
echo "1. Railway (Recommended for Python + WebSocket)"
echo "2. Render"
echo "3. Heroku"
echo "4. Deploy frontend to Netlify"
echo ""

read -p "Choose deployment option (1-4): " choice

case $choice in
    1)
        echo "🚂 Deploying to Railway..."
        echo ""
        echo "Steps to deploy to Railway:"
        echo "1. Go to https://railway.app"
        echo "2. Sign up with GitHub"
        echo "3. Click 'New Project' → 'Deploy from GitHub repo'"
        echo "4. Select your chess repository"
        echo "5. Add these environment variables:"
        echo "   - FLASK_DEBUG=False"
        echo "   - SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
        echo "   - JWT_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
        echo "6. Deploy!"
        echo ""
        echo "Your app will be available at: https://your-app.railway.app"
        ;;
    2)
        echo "🎨 Deploying to Render..."
        echo ""
        echo "Steps to deploy to Render:"
        echo "1. Go to https://render.com"
        echo "2. Sign up with GitHub"
        echo "3. Click 'New' → 'Web Service'"
        echo "4. Connect your GitHub repository"
        echo "5. Use these settings:"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: python run_server.py"
        echo "6. Add environment variables and deploy!"
        ;;
    3)
        echo "🟣 Deploying to Heroku..."
        echo ""
        echo "Steps to deploy to Heroku:"
        echo "1. Install Heroku CLI: brew install heroku/brew/heroku"
        echo "2. Login: heroku login"
        echo "3. Create app: heroku create your-chess-app"
        echo "4. Set environment variables:"
        echo "   heroku config:set FLASK_DEBUG=False"
        echo "   heroku config:set SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
        echo "5. Deploy: git push heroku main"
        ;;
    4)
        echo "🌐 Deploying frontend to Netlify..."
        echo ""
        echo "Steps to deploy frontend to Netlify:"
        echo "1. Go to https://netlify.com"
        echo "2. Sign up with GitHub"
        echo "3. Click 'New site from Git'"
        echo "4. Select your repository"
        echo "5. Set build settings:"
        echo "   - Base directory: frontend"
        echo "   - Build command: (leave empty)"
        echo "   - Publish directory: frontend"
        echo "6. Update the BACKEND_URL in frontend/index.html"
        echo "7. Deploy!"
        ;;
    *)
        echo "❌ Invalid option. Please choose 1-4."
        exit 1
        ;;
esac

echo ""
echo "🔧 Next steps:"
echo "1. Update the BACKEND_URL in frontend/index.html with your deployed backend URL"
echo "2. Test your deployment with: curl https://your-app.railway.app/api/health"
echo "3. Deploy the frontend to Netlify for a complete solution"
echo ""
echo "📚 For detailed instructions, see DEPLOYMENT.md"
echo "🎉 Happy deploying!"
