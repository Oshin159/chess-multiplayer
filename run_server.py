#!/usr/bin/env python3
"""
Server runner for Emotional Chess Multiplayer

Starts the Flask-SocketIO server for multiplayer Emotional Chess games.
"""

import os
import sys
from game_api import app, socketio

def main():
    """Run the Emotional Chess multiplayer server."""
    print("🎭 Starting Emotional Chess Multiplayer Server...")
    print("=" * 50)
    
    # Get port from environment variable (for production deployment)
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"Server will be available at: http://{host}:{port}")
    print("WebSocket support enabled for real-time gameplay")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Add route for serving the main page
    @app.route('/')
    def index():
        """Serve the main game page."""
        try:
            with open('templates/index.html', 'r') as f:
                return f.read()
        except FileNotFoundError:
            return """
            <html>
                <head><title>Emotional Chess</title></head>
                <body>
                    <h1>🎭 Emotional Chess Multiplayer</h1>
                    <p>Server is running! The game interface should be available.</p>
                    <p>Make sure templates/index.html exists.</p>
                </body>
            </html>
            """, 200
    
    # Run the server
    try:
        socketio.run(
            app, 
            debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true', 
            host=host, 
            port=port,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

