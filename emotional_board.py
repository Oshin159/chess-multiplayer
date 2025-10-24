"""
Emotional Chess System - Core Implementation

Extends python-chess.Board to add Love ❤️, Anger 😡, and Sad 😢 mechanics.
"""

import chess
import re
from typing import Optional, List, Dict, Tuple, Set


class EmotionalBoard(chess.Board):
    """
    Emotional Chess Board extending python-chess.Board with three emotional mechanics:
    - Love ❤️: Between opposite sides, prevents capture/check
    - Anger 😡: Within same side, grants +1 movement range
    - Sad 😢: Love-side reaction, freezes movement
    """
    
    # Configuration constants
    LOVE_DISTANCE = 1  # Only adjacent squares can fall in love
    LOVE_BONUS = 30
    ANGER_BONUS = 10
    SAD_PENALTY = 25
    
    def __init__(self, fen: Optional[str] = None):
        """Initialize EmotionalBoard with optional FEN string."""
        if fen is None:
            fen = chess.STARTING_FEN
        super().__init__(fen)
        
        # Emotional state tracking (64 squares)
        self.love_partner = [None] * 64  # Square index -> partner square index
        self.angry_turns = [0] * 64      # Turns remaining angry
        self.sad_turns = [0] * 64        # Turns remaining sad
        
        # Initialize emotional states if FEN provided
        if fen and '|' in fen:
            self._parse_emfen(fen)
    
    def in_love(self, square: int) -> bool:
        """Check if piece at square is in love."""
        return self.love_partner[square] is not None
    
    def is_angry(self, square: int) -> bool:
        """Check if piece at square is angry."""
        return self.angry_turns[square] > 0
    
    def is_sad(self, square: int) -> bool:
        """Check if piece at square is sad."""
        return self.sad_turns[square] > 0
    
    def chebyshev_distance(self, square_a: int, square_b: int) -> int:
        """Calculate Chebyshev distance between two squares."""
        file_a, rank_a = chess.square_file(square_a), chess.square_rank(square_a)
        file_b, rank_b = chess.square_file(square_b), chess.square_rank(square_b)
        return max(abs(file_a - file_b), abs(rank_a - rank_b))
    
    def _get_piece_color(self, square: int) -> Optional[bool]:
        """Get piece color at square (True=white, False=black, None=empty)."""
        piece = self.piece_at(square)
        return piece.color if piece else None
    
    def _can_form_love(self, square_a: int, square_b: int) -> bool:
        """Check if two pieces can form love bond."""
        piece_a = self.piece_at(square_a)
        piece_b = self.piece_at(square_b)
        
        if not piece_a or not piece_b:
            return False
        
        # Must be opposite colors
        if piece_a.color == piece_b.color:
            return False
        
        # Queens cannot form love
        if piece_a.piece_type == chess.QUEEN or piece_b.piece_type == chess.QUEEN:
            return False
        
        # Kings can only love opposite-color pieces, not Kings
        if piece_a.piece_type == chess.KING and piece_b.piece_type == chess.KING:
            return False
        
        # Distance check
        if self.chebyshev_distance(square_a, square_b) > self.LOVE_DISTANCE:
            return False
        
        # Neither already in love
        if self.in_love(square_a) or self.in_love(square_b):
            return False
        
        # Neither in check
        if self.is_check() and (self.king(piece_a.color) == square_a or self.king(piece_b.color) == square_b):
            return False
        
        return True
    
    def _would_place_king_in_check(self, move: chess.Move) -> bool:
        """Check if move would place own king in check."""
        # Make temporary move
        temp_board = self.copy()
        temp_board.push(move)
        return temp_board.is_check()
    
    def update_love_states(self):
        """Update love formations and dissolutions."""
        # Clear existing love states
        for i in range(64):
            self.love_partner[i] = None
        
        # Check for new love formations
        for square_a in range(64):
            piece_a = self.piece_at(square_a)
            if not piece_a or self.in_love(square_a):
                continue
            
            for square_b in range(64):
                if square_a == square_b:
                    continue
                
                piece_b = self.piece_at(square_b)
                if not piece_b or self.in_love(square_b):
                    continue
                
                if self._can_form_love(square_a, square_b):
                    # Form love bond
                    self.love_partner[square_a] = square_b
                    self.love_partner[square_b] = square_a
                    self.log_emotion_event("love_formed", square_a, square_b)
                    break
    
    def trigger_anger_events(self):
        """Trigger anger when friendly pieces are threatened or captured."""
        # Decrement existing anger turns
        for i in range(64):
            if self.angry_turns[i] > 0:
                self.angry_turns[i] -= 1
        
        # Anger should only trigger when a piece of the same color is captured
        # This will be handled in _handle_capture_emotions instead
        # No random triggering here
    
    def apply_sadness(self):
        """Apply sadness effects and update sad turn counters."""
        # Decrement sad turns
        for i in range(64):
            if self.sad_turns[i] > 0:
                self.sad_turns[i] -= 1
        
        # Trigger sadness when pieces lose their love partners
        for square in range(64):
            piece = self.piece_at(square)
            if piece is None:
                continue
                
            # Check if this piece was in love but partner is gone
            if self.in_love(square):
                partner = self.love_partner[square]
                partner_piece = self.piece_at(partner)
                if partner_piece is None or partner_piece.color != piece.color:
                    # Partner is gone or different color, trigger sadness
                    self.sad_turns[square] = 2  # Sad for 2 turns
                    self.log_emotion_event("sadness_triggered", square, None)
                    # Break the love bond
                    self.love_partner[square] = None
                    if partner < 64:
                        self.love_partner[partner] = None
    
    def _handle_capture_emotions(self, captured_square: int):
        """Handle emotional effects when a piece is captured."""
        # Check if captured piece was in love
        if self.in_love(captured_square):
            lover = self.love_partner[captured_square]
            if lover is not None:
                # Lover becomes sad (unless it's a king)
                piece = self.piece_at(lover)
                if piece and piece.piece_type != chess.KING:
                    self.sad_turns[lover] = 1
                    self.log_emotion_event("sadness_triggered", lover)
                
                # Clear love relationship
                self.love_partner[captured_square] = None
                self.love_partner[lover] = None
                self.log_emotion_event("love_broken", captured_square, lover)
        
        # Trigger anger in nearby allies of the captured piece
        # Note: captured_piece is the piece that was captured, so we need to find allies of the same color
        for square in range(64):
            piece = self.piece_at(square)
            if piece and square != captured_square:
                # Check if this piece is close to the captured square
                if self.chebyshev_distance(captured_square, square) <= 2:
                    # Make nearby pieces angry when a piece is captured
                    self.angry_turns[square] = 3  # Angry for 3 turns
                    self.log_emotion_event("anger_triggered", square, None)
    
    def log_emotion_event(self, event_type: str, square_a: int, square_b: int = None):
        """Log emotional events for debugging."""
        square_name_a = chess.square_name(square_a)
        square_name_b = chess.square_name(square_b) if square_b is not None else ""
        print(f"Emotion: {event_type} at {square_name_a} {square_name_b}")
    
    def generate_legal_moves(self, from_mask: int = chess.BB_ALL, to_mask: int = chess.BB_ALL) -> List[chess.Move]:
        """Generate legal moves considering emotional mechanics."""
        # Get base legal moves
        base_moves = list(super().generate_legal_moves(from_mask, to_mask))
        legal_moves = []
        
        for move in base_moves:
            from_square = move.from_square
            to_square = move.to_square
            
            # Restrict pawn moves to 1 square only (not 2)
            piece = self.piece_at(from_square)
            if piece and piece.piece_type == chess.PAWN:
                # Calculate distance moved
                from_rank = chess.square_rank(from_square)
                to_rank = chess.square_rank(to_square)
                distance = abs(to_rank - from_rank)
                
                # Only allow 1 square forward moves for pawns
                if distance > 1:
                    continue
            
            # Check if move violates love mechanics
            if self.in_love(from_square):
                lover = self.love_partner[from_square]
                # Cannot capture lover
                if to_square == lover:
                    continue
                # Cannot check lover's king
                if self.piece_at(to_square) and self.piece_at(to_square).piece_type == chess.KING:
                    target_king_color = self.piece_at(to_square).color
                    if self.piece_at(lover) and self.piece_at(lover).color == target_king_color:
                        continue
            
            # Check sadness restrictions
            if self.is_sad(from_square):
                # Sad pieces cannot move unless in check
                # Check if the current player's king is in check
                piece = self.piece_at(from_square)
                if piece:
                    # Find the king of the same color
                    king_in_check = False
                    for square in range(64):
                        king_piece = self.piece_at(square)
                        if king_piece and king_piece.piece_type == chess.KING and king_piece.color == piece.color:
                            # Check if this king is in check
                            king_in_check = self.is_check()
                            break
                    
                    if not king_in_check:
                        continue
                
                # If in check, can only move to resolve check
                if self._would_place_king_in_check(move):
                    continue
            
            # Add anger bonus moves
            if self.is_angry(from_square):
                # Add +1 range moves for angry pieces (except knights)
                piece = self.piece_at(from_square)
                if piece and piece.piece_type != chess.KNIGHT:
                    anger_moves = self._generate_anger_moves(from_square)
                    for anger_move in anger_moves:
                        if anger_move not in legal_moves:
                            legal_moves.append(anger_move)
            
            legal_moves.append(move)
        
        return legal_moves
    
    def _generate_anger_moves(self, square: int) -> List[chess.Move]:
        """Generate additional moves for angry pieces (+1 range)."""
        anger_moves = []
        piece = self.piece_at(square)
        if not piece or piece.piece_type == chess.KNIGHT:
            return anger_moves
        
        # Get normal moves for this piece
        normal_moves = super().generate_legal_moves(chess.BB_SQUARES[square])
        
        # Extend each move by 1 square in the same direction
        for move in normal_moves:
            from_file, from_rank = chess.square_file(move.from_square), chess.square_rank(move.from_square)
            to_file, to_rank = chess.square_file(move.to_square), chess.square_rank(move.to_square)
            
            # Calculate direction
            file_delta = to_file - from_file
            rank_delta = to_rank - from_rank
            
            # Normalize direction (but keep magnitude)
            if file_delta != 0:
                file_delta = file_delta // abs(file_delta)
            if rank_delta != 0:
                rank_delta = rank_delta // abs(rank_delta)
            
            # Extend by one square
            extended_file = to_file + file_delta
            extended_rank = to_rank + rank_delta
            
            # Check if extended square is valid
            if 0 <= extended_file < 8 and 0 <= extended_rank < 8:
                extended_square = chess.square(extended_file, extended_rank)
                
                # Check if move is legal (not blocked, not capturing own piece)
                if self._is_legal_anger_move(square, extended_square):
                    anger_moves.append(chess.Move(square, extended_square))
        
        return anger_moves
    
    def _is_legal_anger_move(self, from_square: int, to_square: int) -> bool:
        """Check if anger move is legal."""
        # Cannot move to same square
        if from_square == to_square:
            return False
        
        # Cannot capture own piece
        piece_at_dest = self.piece_at(to_square)
        piece_at_src = self.piece_at(from_square)
        if piece_at_dest and piece_at_dest.color == piece_at_src.color:
            return False
        
        # Cannot capture lover
        if self.in_love(from_square):
            lover = self.love_partner[from_square]
            if to_square == lover:
                return False
        
        return True
    
    def push(self, move: chess.Move):
        """Push move and update emotional states."""
        # Check if move captures a piece
        captured_square = move.to_square
        captured_piece = self.piece_at(captured_square)
        
        # Apply the move
        super().push(move)
        
        # Handle emotional effects of capture
        if captured_piece:
            self._handle_capture_emotions(captured_square)
        
        # Update emotional states
        self.update_love_states()
        self.trigger_anger_events()
        self.apply_sadness()
    
    def emotion_summary(self) -> Dict[str, int]:
        """Get summary of current emotional states."""
        love_pairs = sum(1 for i in range(64) if self.in_love(i)) // 2
        angry_count = sum(1 for i in range(64) if self.is_angry(i))
        sad_count = sum(1 for i in range(64) if self.is_sad(i))
        
        return {
            "love_pairs": love_pairs,
            "angry": angry_count,
            "sad": sad_count
        }
    
    def to_emfen(self) -> str:
        """Convert board to emFEN (extended FEN with emotional state)."""
        base_fen = self.fen()
        
        # Build emotional state strings
        love_pairs = []
        for i in range(64):
            if self.in_love(i) and i < self.love_partner[i]:  # Avoid duplicates
                square_a = chess.square_name(i)
                square_b = chess.square_name(self.love_partner[i])
                love_pairs.append(f"{square_a}-{square_b}")
        
        angry_squares = [chess.square_name(i) for i in range(64) if self.is_angry(i)]
        sad_squares = [chess.square_name(i) for i in range(64) if self.is_sad(i)]
        
        # Build emFEN
        emfen_parts = [base_fen]
        
        if love_pairs:
            emfen_parts.append(f"L: {','.join(love_pairs)}")
        if angry_squares:
            emfen_parts.append(f"A: {','.join(angry_squares)}")
        if sad_squares:
            emfen_parts.append(f"S: {','.join(sad_squares)}")
        
        return " | ".join(emfen_parts)
    
    def from_emfen(self, emfen_str: str):
        """Parse emFEN string and set board state."""
        parts = emfen_str.split(" | ")
        base_fen = parts[0]
        
        # Set base board
        self.set_fen(base_fen)
        
        # Clear emotional states
        self.love_partner = [None] * 64
        self.angry_turns = [0] * 64
        self.sad_turns = [0] * 64
        
        # Parse emotional states
        for part in parts[1:]:
            if part.startswith("L: "):
                self._parse_love_pairs(part[3:])
            elif part.startswith("A: "):
                self._parse_angry_squares(part[3:])
            elif part.startswith("S: "):
                self._parse_sad_squares(part[3:])
    
    def _parse_emfen(self, emfen_str: str):
        """Parse emFEN during initialization."""
        self.from_emfen(emfen_str)
    
    def _parse_love_pairs(self, love_str: str):
        """Parse love pairs from emFEN."""
        if not love_str.strip():
            return
        
        pairs = love_str.split(",")
        for pair in pairs:
            if "-" in pair:
                square_a, square_b = pair.strip().split("-")
                try:
                    idx_a = chess.parse_square(square_a)
                    idx_b = chess.parse_square(square_b)
                    self.love_partner[idx_a] = idx_b
                    self.love_partner[idx_b] = idx_a
                except ValueError:
                    continue
    
    def _parse_angry_squares(self, angry_str: str):
        """Parse angry squares from emFEN."""
        if not angry_str.strip():
            return
        
        squares = angry_str.split(",")
        for square in squares:
            try:
                idx = chess.parse_square(square.strip())
                self.angry_turns[idx] = 1  # Set to 1 turn remaining
            except ValueError:
                continue
    
    def _parse_sad_squares(self, sad_str: str):
        """Parse sad squares from emFEN."""
        if not sad_str.strip():
            return
        
        squares = sad_str.split(",")
        for square in squares:
            try:
                idx = chess.parse_square(square.strip())
                self.sad_turns[idx] = 1  # Set to 1 turn remaining
            except ValueError:
                continue
