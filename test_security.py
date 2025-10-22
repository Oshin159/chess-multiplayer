#!/usr/bin/env python3
"""
Test script for Emotional Chess security and persistence features

Demonstrates session management, database persistence, and security features.
"""

import requests
import json
import time
from game_models import GameManager
from database import DatabaseManager
from security import SecurityManager


def test_database_persistence():
    """Test database persistence functionality."""
    print("🧪 Testing Database Persistence")
    print("-" * 40)
    
    # Initialize database
    db_manager = DatabaseManager("test_chess.db")
    
    # Test game creation and persistence
    game_manager = GameManager("test_chess.db")
    
    try:
        # Create a game
        game_id = game_manager.create_game("Test Game", 2)
        print(f"✅ Created game: {game_id}")
        
        # Join game
        result = game_manager.join_game(game_id, "Player1", "white")
        if result["success"]:
            print(f"✅ Player joined: {result['player_id']}")
            session_token = result["session_token"]
            print(f"✅ Session token generated: {session_token[:20]}...")
        else:
            print(f"❌ Failed to join game: {result['error']}")
            return False
        
        # Join second player
        result2 = game_manager.join_game(game_id, "Player2", "black")
        if result2["success"]:
            print(f"✅ Second player joined: {result2['player_id']}")
        else:
            print(f"❌ Failed to join second player: {result2['error']}")
            return False
        
        # Start game
        if game_manager.start_game(game_id):
            print("✅ Game started")
        else:
            print("❌ Failed to start game")
            return False
        
        # Make a move
        move_result = game_manager.make_move(result["player_id"], "e4")
        if move_result["success"]:
            print(f"✅ Move made: {move_result['move']}")
        else:
            print(f"❌ Move failed: {move_result['error']}")
            return False
        
        # Test database persistence
        print("\n📊 Database Statistics:")
        games = db_manager.load_all_games()
        print(f"   Total games in database: {len(games)}")
        
        for game in games:
            players = db_manager.load_players_for_game(game['id'])
            moves = db_manager.load_moves_for_game(game['id'])
            print(f"   Game {game['id'][:8]}... - Players: {len(players)}, Moves: {len(moves)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_security_features():
    """Test security features."""
    print("\n🔐 Testing Security Features")
    print("-" * 40)
    
    security_manager = SecurityManager()
    
    try:
        # Test JWT token generation
        player_id = "test_player_123"
        game_id = "test_game_456"
        
        token = security_manager.generate_session_token(player_id, game_id)
        print(f"✅ Generated session token: {token[:20]}...")
        
        # Test token validation
        session_data = security_manager.validate_session_token(token)
        if session_data:
            print(f"✅ Token validation successful")
            print(f"   Player ID: {session_data['player_id']}")
            print(f"   Game ID: {session_data['game_id']}")
        else:
            print("❌ Token validation failed")
            return False
        
        # Test input validation
        from security import validate_player_name, validate_color, validate_move_notation
        
        # Valid inputs
        if validate_player_name("Alice"):
            print("✅ Valid player name accepted")
        else:
            print("❌ Valid player name rejected")
            return False
        
        if validate_color("white"):
            print("✅ Valid color accepted")
        else:
            print("❌ Valid color rejected")
            return False
        
        if validate_move_notation("e4"):
            print("✅ Valid move notation accepted")
        else:
            print("❌ Valid move notation rejected")
            return False
        
        # Invalid inputs
        if not validate_player_name(""):
            print("✅ Empty player name rejected")
        else:
            print("❌ Empty player name accepted")
            return False
        
        if not validate_color("purple"):
            print("✅ Invalid color rejected")
        else:
            print("❌ Invalid color accepted")
            return False
        
        if not validate_move_notation("invalid"):
            print("✅ Invalid move notation rejected")
        else:
            print("❌ Invalid move notation accepted")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        return False


def test_api_security():
    """Test API security features."""
    print("\n🌐 Testing API Security")
    print("-" * 40)
    
    base_url = "http://localhost:5001"
    
    try:
        # Test health check
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check successful: {health_data['status']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test game creation
        game_data = {"name": "Security Test Game", "max_players": 2}
        response = requests.post(f"{base_url}/api/games", json=game_data)
        
        if response.status_code == 200:
            game_info = response.json()
            game_id = game_info["game_id"]
            print(f"✅ Game created: {game_id}")
        else:
            print(f"❌ Game creation failed: {response.status_code}")
            return False
        
        # Test joining game
        join_data = {"name": "TestPlayer", "color": "white"}
        response = requests.post(f"{base_url}/api/games/{game_id}/join", json=join_data)
        
        if response.status_code == 200:
            join_info = response.json()
            session_token = join_info["session_token"]
            print(f"✅ Player joined with session token: {session_token[:20]}...")
        else:
            print(f"❌ Join game failed: {response.status_code}")
            return False
        
        # Test session validation
        session_data = {"session_token": session_token}
        response = requests.post(f"{base_url}/api/session/validate", json=session_data)
        
        if response.status_code == 200:
            validation_result = response.json()
            if validation_result["valid"]:
                print("✅ Session validation successful")
            else:
                print("❌ Session validation failed")
                return False
        else:
            print(f"❌ Session validation request failed: {response.status_code}")
            return False
        
        # Test protected endpoint without token (should fail)
        move_data = {"move": "e4"}
        response = requests.post(f"{base_url}/api/games/{game_id}/move", json=move_data)
        
        if response.status_code == 401:
            print("✅ Protected endpoint correctly rejected request without token")
        else:
            print(f"❌ Protected endpoint should have rejected request: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start server with: python run_server.py")
        return False
    except Exception as e:
        print(f"❌ API security test failed: {e}")
        return False


def cleanup_test_data():
    """Clean up test data."""
    print("\n🧹 Cleaning up test data")
    print("-" * 40)
    
    import os
    
    test_files = ["test_chess.db", "test_chess.db-journal"]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"✅ Removed {file}")
        else:
            print(f"ℹ️  {file} not found")


def main():
    """Run all security and persistence tests."""
    print("🎭 Emotional Chess Security & Persistence Test Suite")
    print("=" * 60)
    
    tests = [
        ("Database Persistence", test_database_persistence),
        ("Security Features", test_security_features),
        ("API Security", test_api_security)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test")
        if test_func():
            print(f"✅ {test_name} test passed")
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Security and persistence features are working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    cleanup_test_data()
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
