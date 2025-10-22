#!/usr/bin/env python3
"""
Demo script for Emotional Chess Multiplayer API

Shows how to use the API to create games, join players, and make moves.
"""

import requests
import json
import time
from typing import Dict, List


class EmotionalChessClient:
    """Client for interacting with the Emotional Chess API."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """Initialize the client."""
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict:
        """Check if the server is running."""
        response = self.session.get(f"{self.base_url}/api/health")
        return response.json()
    
    def create_game(self, name: str, max_players: int = 2) -> Dict:
        """Create a new game."""
        response = self.session.post(
            f"{self.base_url}/api/games",
            json={"name": name, "max_players": max_players}
        )
        return response.json()
    
    def join_game(self, game_id: str, player_name: str, preferred_color: str = None) -> Dict:
        """Join a game."""
        data = {"name": player_name}
        if preferred_color:
            data["color"] = preferred_color
        
        response = self.session.post(
            f"{self.base_url}/api/games/{game_id}/join",
            json=data
        )
        return response.json()
    
    def start_game(self, game_id: str) -> Dict:
        """Start a game."""
        response = self.session.post(f"{self.base_url}/api/games/{game_id}/start")
        return response.json()
    
    def make_move(self, game_id: str, player_id: str, move: str) -> Dict:
        """Make a move in a game."""
        response = self.session.post(
            f"{self.base_url}/api/games/{game_id}/move",
            json={"player_id": player_id, "move": move}
        )
        return response.json()
    
    def get_game(self, game_id: str) -> Dict:
        """Get game information."""
        response = self.session.get(f"{self.base_url}/api/games/{game_id}")
        return response.json()
    
    def list_games(self) -> Dict:
        """List all games."""
        response = self.session.get(f"{self.base_url}/api/games")
        return response.json()


def demo_two_player_game():
    """Demonstrate a two-player game."""
    print("🎭 Emotional Chess Multiplayer Demo")
    print("=" * 50)
    
    # Initialize client
    client = EmotionalChessClient()
    
    # Check server health
    print("1. Checking server health...")
    health = client.health_check()
    print(f"   Server status: {health['status']}")
    print(f"   Active games: {health['active_games']}")
    print()
    
    # Create a game
    print("2. Creating a new game...")
    create_result = client.create_game("Demo Game", 2)
    if not create_result['success']:
        print(f"   Error: {create_result['error']}")
        return
    
    game_id = create_result['game_id']
    print(f"   Game ID: {game_id}")
    print(f"   Game name: {create_result['game']['name']}")
    print()
    
    # Join two players
    print("3. Joining players...")
    
    # Player 1 (White)
    join1_result = client.join_game(game_id, "Alice", "white")
    if not join1_result['success']:
        print(f"   Error joining Alice: {join1_result['error']}")
        return
    
    alice_id = join1_result['player_id']
    print(f"   Alice joined as {join1_result['color']} (ID: {alice_id})")
    
    # Player 2 (Black)
    join2_result = client.join_game(game_id, "Bob", "black")
    if not join2_result['success']:
        print(f"   Error joining Bob: {join2_result['error']}")
        return
    
    bob_id = join2_result['player_id']
    print(f"   Bob joined as {join2_result['color']} (ID: {bob_id})")
    print()
    
    # Start the game
    print("4. Starting the game...")
    start_result = client.start_game(game_id)
    if not start_result['success']:
        print(f"   Error starting game: {start_result['error']}")
        return
    
    print("   Game started!")
    print(f"   Current player: {start_result['game']['current_player']}")
    print()
    
    # Make some moves
    print("5. Making moves...")
    moves = [
        ("Alice", alice_id, "e4"),
        ("Bob", bob_id, "e5"),
        ("Alice", alice_id, "Nf3"),
        ("Bob", bob_id, "Nc6"),
        ("Alice", alice_id, "Bb5"),
    ]
    
    for player_name, player_id, move in moves:
        print(f"   {player_name} plays {move}...")
        move_result = client.make_move(game_id, player_id, move)
        
        if move_result['success']:
            print(f"   ✅ Move successful!")
            if 'emotions' in move_result:
                emotions = move_result['emotions']
                print(f"   💝 Love pairs: {emotions['love_pairs']}")
                print(f"   😡 Angry pieces: {emotions['angry']}")
                print(f"   😢 Sad pieces: {emotions['sad']}")
            
            if move_result.get('game_over'):
                print(f"   🏆 Game over! Winner: {move_result.get('winner', 'Draw')}")
                break
            else:
                print(f"   Next player: {move_result.get('next_player', 'Unknown')}")
        else:
            print(f"   ❌ Move failed: {move_result['error']}")
        
        print()
        time.sleep(1)  # Pause between moves
    
    # Show final game state
    print("6. Final game state...")
    game_state = client.get_game(game_id)
    if game_state['success']:
        game = game_state['game']
        print(f"   Game status: {game['status']}")
        print(f"   Move count: {game['move_count']}")
        if game['winner']:
            print(f"   Winner: {game['winner']}")
        print(f"   Emotions: {game['emotions']}")
    
    print("\n🎉 Demo completed!")


def demo_multiplayer_game():
    """Demonstrate a multiplayer game with more than 2 players."""
    print("🎭 Multiplayer Emotional Chess Demo (4 Players)")
    print("=" * 50)
    
    client = EmotionalChessClient()
    
    # Create a 4-player game
    print("1. Creating a 4-player game...")
    create_result = client.create_game("Multiplayer Demo", 4)
    if not create_result['success']:
        print(f"   Error: {create_result['error']}")
        return
    
    game_id = create_result['game_id']
    print(f"   Game ID: {game_id}")
    print()
    
    # Join 4 players
    players = [
        ("Alice", "white"),
        ("Bob", "black"),
        ("Charlie", "red"),
        ("Diana", "blue")
    ]
    
    player_ids = {}
    print("2. Joining players...")
    for name, color in players:
        join_result = client.join_game(game_id, name, color)
        if join_result['success']:
            player_ids[name] = join_result['player_id']
            print(f"   {name} joined as {color}")
        else:
            print(f"   Error joining {name}: {join_result['error']}")
    
    print()
    
    # Start the game
    print("3. Starting the game...")
    start_result = client.start_game(game_id)
    if start_result['success']:
        print("   Game started!")
        print(f"   Turn order: {start_result['game']['turn_order']}")
        print(f"   Current player: {start_result['game']['current_player']}")
    else:
        print(f"   Error: {start_result['error']}")
    
    print("\n🎉 Multiplayer demo completed!")


if __name__ == "__main__":
    print("Choose demo type:")
    print("1. Two-player game")
    print("2. Multiplayer game (4 players)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        demo_two_player_game()
    elif choice == "2":
        demo_multiplayer_game()
    else:
        print("Invalid choice. Running two-player demo...")
        demo_two_player_game()

