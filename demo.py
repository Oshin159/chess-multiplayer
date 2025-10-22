#!/usr/bin/env python3
"""
Emotional Chess Demo

Demonstrates the emotional chess system with a simple game scenario.
"""

import chess
from emotional_board import EmotionalBoard
from evaluation import EmotionalEvaluator


def main():
    """Run emotional chess demo."""
    print("🎭 Emotional Chess Demo")
    print("=" * 50)
    
    # Create emotional board
    board = EmotionalBoard()
    print(f"Starting position: {board.fen()}")
    
    # Show initial emotions
    print(f"\nInitial emotions: {board.emotion_summary()}")
    
    # Make some moves
    print("\n📝 Making moves...")
    moves = ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5"]
    
    for i, move_san in enumerate(moves):
        if i % 2 == 0:
            print(f"White plays {move_san}")
        else:
            print(f"Black plays {move_san}")
        
        board.push_san(move_san)
        
        # Show emotions after each move
        emotions = board.emotion_summary()
        print(f"  Emotions: {emotions}")
        
        # Show emFEN
        emfen = board.to_emfen()
        print(f"  emFEN: {emfen}")
        print()
    
    # Demonstrate love formation
    print("❤️ Love Formation Demo")
    print("-" * 30)
    
    # Set up pieces close enough for love
    board.love_partner[chess.E2] = chess.E7
    board.love_partner[chess.E7] = chess.E2
    
    print(f"E2 and E7 are now in love!")
    print(f"E2 in love: {board.in_love(chess.E2)}")
    print(f"E7 in love: {board.in_love(chess.E7)}")
    
    # Show love prevents capture
    legal_moves = board.generate_legal_moves(chess.BB_SQUARES[chess.E2])
    capture_move = chess.Move(chess.E2, chess.E7)
    print(f"Can E2 capture E7? {capture_move in legal_moves}")
    
    # Demonstrate anger
    print("\n😡 Anger Demo")
    print("-" * 30)
    
    board.angry_turns[chess.E4] = 1
    print(f"E4 is angry: {board.is_angry(chess.E4)}")
    print(f"E4 has extended movement range!")
    
    # Demonstrate sadness
    print("\n😢 Sadness Demo")
    print("-" * 30)
    
    board.sad_turns[chess.G2] = 1
    print(f"G2 is sad: {board.is_sad(chess.G2)}")
    print(f"G2 cannot move (unless in check)")
    
    # Show final emotions
    print(f"\nFinal emotions: {board.emotion_summary()}")
    
    # Position evaluation
    print("\n📊 Position Evaluation")
    print("-" * 30)
    
    evaluator = EmotionalEvaluator(board)
    score = evaluator.evaluate_position()
    print(f"Total score: {score}")
    
    details = evaluator.get_detailed_evaluation()
    print(f"Material: {details['material']}")
    print(f"Love bonus: {details['love_bonus']}")
    print(f"Anger bonus: {details['anger_bonus']}")
    print(f"Sad penalty: {details['sad_penalty']}")
    
    # Emotion impact per side
    impact = evaluator.get_emotion_impact()
    print(f"\nWhite emotions: {impact['white']}")
    print(f"Black emotions: {impact['black']}")
    
    # Save and load game
    print("\n💾 Save/Load Demo")
    print("-" * 30)
    
    # Save current state
    emfen = board.to_emfen()
    print(f"Saved emFEN: {emfen}")
    
    # Load into new board using from_emfen method
    new_board = EmotionalBoard()
    new_board.from_emfen(emfen)
    print(f"Loaded emotions: {new_board.emotion_summary()}")
    
    # Verify love relationship
    print(f"E2 still in love: {new_board.in_love(chess.E2)}")
    print(f"E7 still in love: {new_board.in_love(chess.E7)}")
    
    print("\n✅ Demo completed successfully!")


if __name__ == "__main__":
    main()
