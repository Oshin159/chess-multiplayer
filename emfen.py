"""
emFEN (Emotional FEN) - Extended FEN format for Emotional Chess

Supports serialization and deserialization of emotional states:
- Love pairs between opposite sides
- Angry pieces with remaining turns
- Sad pieces with remaining turns
"""

import chess
from typing import Dict, List, Tuple, Optional


class EmFEN:
    """Handle emFEN serialization and deserialization."""
    
    @staticmethod
    def encode(board: 'EmotionalBoard') -> str:
        """
        Encode EmotionalBoard to emFEN string.
        
        Format: <base_fen> | L: a2-b5,c4-d7 | A: e4,f7 | S: g2
        
        Args:
            board: EmotionalBoard instance
            
        Returns:
            emFEN string
        """
        base_fen = board.fen()
        
        # Build emotional state components
        love_pairs = EmFEN._encode_love_pairs(board)
        angry_squares = EmFEN._encode_angry_squares(board)
        sad_squares = EmFEN._encode_sad_squares(board)
        
        # Combine into emFEN
        emfen_parts = [base_fen]
        
        if love_pairs:
            emfen_parts.append(f"L: {love_pairs}")
        if angry_squares:
            emfen_parts.append(f"A: {angry_squares}")
        if sad_squares:
            emfen_parts.append(f"S: {sad_squares}")
        
        return " | ".join(emfen_parts)
    
    @staticmethod
    def decode(emfen_str: str, board: 'EmotionalBoard'):
        """
        Decode emFEN string and apply to EmotionalBoard.
        
        Args:
            emfen_str: emFEN string to decode
            board: EmotionalBoard instance to modify
        """
        parts = emfen_str.split(" | ")
        base_fen = parts[0]
        
        # Set base board state
        board.set_fen(base_fen)
        
        # Clear emotional states
        board.love_partner = [None] * 64
        board.angry_turns = [0] * 64
        board.sad_turns = [0] * 64
        
        # Parse emotional components
        for part in parts[1:]:
            if part.startswith("L: "):
                EmFEN._decode_love_pairs(part[3:], board)
            elif part.startswith("A: "):
                EmFEN._decode_angry_squares(part[3:], board)
            elif part.startswith("S: "):
                EmFEN._decode_sad_squares(part[3:], board)
    
    @staticmethod
    def _encode_love_pairs(board: 'EmotionalBoard') -> str:
        """Encode love pairs to string format."""
        love_pairs = []
        processed = set()
        
        for i in range(64):
            if board.in_love(i) and i not in processed:
                partner = board.love_partner[i]
                square_a = chess.square_name(i)
                square_b = chess.square_name(partner)
                love_pairs.append(f"{square_a}-{square_b}")
                processed.add(i)
                processed.add(partner)
        
        return ",".join(love_pairs)
    
    @staticmethod
    def _encode_angry_squares(board: 'EmotionalBoard') -> str:
        """Encode angry squares to string format."""
        angry_squares = []
        for i in range(64):
            if board.is_angry(i):
                angry_squares.append(chess.square_name(i))
        return ",".join(angry_squares)
    
    @staticmethod
    def _encode_sad_squares(board: 'EmotionalBoard') -> str:
        """Encode sad squares to string format."""
        sad_squares = []
        for i in range(64):
            if board.is_sad(i):
                sad_squares.append(chess.square_name(i))
        return ",".join(sad_squares)
    
    @staticmethod
    def _decode_love_pairs(love_str: str, board: 'EmotionalBoard'):
        """Decode love pairs from string."""
        if not love_str.strip():
            return
        
        pairs = love_str.split(",")
        for pair in pairs:
            if "-" in pair:
                try:
                    square_a, square_b = pair.strip().split("-")
                    idx_a = chess.parse_square(square_a)
                    idx_b = chess.parse_square(square_b)
                    board.love_partner[idx_a] = idx_b
                    board.love_partner[idx_b] = idx_a
                except ValueError:
                    continue
    
    @staticmethod
    def _decode_angry_squares(angry_str: str, board: 'EmotionalBoard'):
        """Decode angry squares from string."""
        if not angry_str.strip():
            return
        
        squares = angry_str.split(",")
        for square in squares:
            try:
                idx = chess.parse_square(square.strip())
                board.angry_turns[idx] = 1  # Default to 1 turn
            except ValueError:
                continue
    
    @staticmethod
    def _decode_sad_squares(sad_str: str, board: 'EmotionalBoard'):
        """Decode sad squares from string."""
        if not sad_str.strip():
            return
        
        squares = sad_str.split(",")
        for square in squares:
            try:
                idx = chess.parse_square(square.strip())
                board.sad_turns[idx] = 1  # Default to 1 turn
            except ValueError:
                continue
    
    @staticmethod
    def validate(emfen_str: str) -> bool:
        """
        Validate emFEN string format.
        
        Args:
            emfen_str: emFEN string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            parts = emfen_str.split(" | ")
            if len(parts) < 1:
                return False
            
            # Validate base FEN
            base_fen = parts[0]
            test_board = chess.Board()
            test_board.set_fen(base_fen)
            
            # Validate emotional components
            for part in parts[1:]:
                if not (part.startswith("L: ") or part.startswith("A: ") or part.startswith("S: ")):
                    return False
            
            return True
        except:
            return False
    
    @staticmethod
    def get_emotion_summary(emfen_str: str) -> Dict[str, int]:
        """
        Get emotion summary from emFEN string without creating board.
        
        Args:
            emfen_str: emFEN string
            
        Returns:
            Dictionary with emotion counts
        """
        parts = emfen_str.split(" | ")
        
        love_pairs = 0
        angry_count = 0
        sad_count = 0
        
        for part in parts[1:]:
            if part.startswith("L: "):
                love_str = part[3:]
                if love_str.strip():
                    love_pairs = len(love_str.split(","))
            elif part.startswith("A: "):
                angry_str = part[3:]
                if angry_str.strip():
                    angry_count = len(angry_str.split(","))
            elif part.startswith("S: "):
                sad_str = part[3:]
                if sad_str.strip():
                    sad_count = len(sad_str.split(","))
        
        return {
            "love_pairs": love_pairs,
            "angry": angry_count,
            "sad": sad_count
        }
