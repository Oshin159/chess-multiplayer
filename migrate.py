#!/usr/bin/env python3
"""
Database migration script for Emotional Chess Multiplayer

Handles database initialization, migrations, and cleanup.
"""

import os
import sys
import argparse
from database import DatabaseManager
from security import SecurityManager


def init_database(db_path: str = "chess_games.db"):
    """Initialize the database with required tables."""
    print(f"Initializing database at: {db_path}")
    
    try:
        db_manager = DatabaseManager(db_path)
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def backup_database(db_path: str = "chess_games.db"):
    """Create a backup of the database."""
    import shutil
    import time
    
    timestamp = int(time.time())
    backup_path = f"{db_path}.backup.{timestamp}"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Database backup failed: {e}")
        return None


def restore_database(backup_path: str, db_path: str = "chess_games.db"):
    """Restore database from backup."""
    import shutil
    
    try:
        shutil.copy2(backup_path, db_path)
        print(f"✅ Database restored from: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Database restore failed: {e}")
        return False


def cleanup_database(db_path: str = "chess_games.db"):
    """Clean up expired sessions and abandoned games."""
    try:
        db_manager = DatabaseManager(db_path)
        
        # Clean up expired sessions
        expired_sessions = db_manager.cleanup_expired_sessions()
        print(f"✅ Cleaned up {expired_sessions} expired sessions")
        
        return True
    except Exception as e:
        print(f"❌ Database cleanup failed: {e}")
        return False


def show_database_stats(db_path: str = "chess_games.db"):
    """Show database statistics."""
    try:
        db_manager = DatabaseManager(db_path)
        
        # Get game count
        games = db_manager.load_all_games()
        print(f"📊 Database Statistics:")
        print(f"   Total games: {len(games)}")
        
        # Count by status
        status_counts = {}
        for game in games:
            status = game.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"   Games by status:")
        for status, count in status_counts.items():
            print(f"     {status}: {count}")
        
        # Get total players
        total_players = 0
        for game in games:
            players = db_manager.load_players_for_game(game['id'])
            total_players += len(players)
        
        print(f"   Total players: {total_players}")
        
        # Get total moves
        total_moves = 0
        for game in games:
            moves = db_manager.load_moves_for_game(game['id'])
            total_moves += len(moves)
        
        print(f"   Total moves: {total_moves}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to get database stats: {e}")
        return False


def reset_database(db_path: str = "chess_games.db"):
    """Reset the database (WARNING: This will delete all data)."""
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"✅ Removed existing database: {db_path}")
        
        # Reinitialize
        return init_database(db_path)
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        return False


def main():
    """Main migration script."""
    parser = argparse.ArgumentParser(description="Emotional Chess Database Migration")
    parser.add_argument("--db-path", default="chess_games.db", help="Database file path")
    parser.add_argument("--action", required=True, 
                      choices=["init", "backup", "restore", "cleanup", "stats", "reset"],
                      help="Action to perform")
    parser.add_argument("--backup-path", help="Backup file path for restore action")
    
    args = parser.parse_args()
    
    print("🎭 Emotional Chess Database Migration")
    print("=" * 40)
    
    if args.action == "init":
        success = init_database(args.db_path)
    elif args.action == "backup":
        success = backup_database(args.db_path)
    elif args.action == "restore":
        if not args.backup_path:
            print("❌ --backup-path required for restore action")
            sys.exit(1)
        success = restore_database(args.backup_path, args.db_path)
    elif args.action == "cleanup":
        success = cleanup_database(args.db_path)
    elif args.action == "stats":
        success = show_database_stats(args.db_path)
    elif args.action == "reset":
        print("⚠️  WARNING: This will delete all data!")
        confirm = input("Are you sure? Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            success = reset_database(args.db_path)
        else:
            print("❌ Reset cancelled")
            success = False
    else:
        print(f"❌ Unknown action: {args.action}")
        success = False
    
    if success:
        print("✅ Operation completed successfully")
        sys.exit(0)
    else:
        print("❌ Operation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
