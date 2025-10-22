"""
Evaluation functions for Emotional Chess

Provides position evaluation considering emotional mechanics.
"""

import chess
from typing import Dict, Optional
from emotional_board import EmotionalBoard


class EmotionalEvaluator:
    """Evaluate positions considering emotional mechanics."""
    
    # Piece values (standard)
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }
    
    # Emotional bonuses/penalties
    LOVE_BONUS = 30
    ANGER_BONUS = 10
    SAD_PENALTY = 25
    
    def __init__(self, board: EmotionalBoard):
        """Initialize evaluator with board."""
        self.board = board
    
    def evaluate_position(self) -> int:
        """
        Evaluate current position considering emotional mechanics.
        
        Returns:
            Evaluation score (positive favors white, negative favors black)
        """
        material_score = self._evaluate_material()
        love_bonus = self._evaluate_love()
        anger_bonus = self._evaluate_anger()
        sad_penalty = self._evaluate_sadness()
        
        return material_score + love_bonus + anger_bonus - sad_penalty
    
    def _evaluate_material(self) -> int:
        """Evaluate material balance."""
        score = 0
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                value = self.PIECE_VALUES[piece.piece_type]
                if piece.color == chess.WHITE:
                    score += value
                else:
                    score -= value
        
        return score
    
    def _evaluate_love(self) -> int:
        """Evaluate love bonuses."""
        love_score = 0
        processed = set()
        
        for square in chess.SQUARES:
            if self.board.in_love(square) and square not in processed:
                partner = self.board.love_partner[square]
                piece = self.board.piece_at(square)
                partner_piece = self.board.piece_at(partner)
                
                if piece and partner_piece:
                    # Both pieces get love bonus
                    bonus = self.LOVE_BONUS
                    if piece.color == chess.WHITE:
                        love_score += bonus
                    else:
                        love_score -= bonus
                    
                    if partner_piece.color == chess.WHITE:
                        love_score += bonus
                    else:
                        love_score -= bonus
                
                processed.add(square)
                processed.add(partner)
        
        return love_score
    
    def _evaluate_anger(self) -> int:
        """Evaluate anger bonuses."""
        anger_score = 0
        
        for square in chess.SQUARES:
            if self.board.is_angry(square):
                piece = self.board.piece_at(square)
                if piece:
                    bonus = self.ANGER_BONUS
                    if piece.color == chess.WHITE:
                        anger_score += bonus
                    else:
                        anger_score -= bonus
        
        return anger_score
    
    def _evaluate_sadness(self) -> int:
        """Evaluate sadness penalties."""
        sad_score = 0
        
        for square in chess.SQUARES:
            if self.board.is_sad(square):
                piece = self.board.piece_at(square)
                if piece:
                    penalty = self.SAD_PENALTY
                    if piece.color == chess.WHITE:
                        sad_score += penalty
                    else:
                        sad_score -= penalty
        
        return sad_score
    
    def get_detailed_evaluation(self) -> Dict[str, int]:
        """
        Get detailed breakdown of evaluation components.
        
        Returns:
            Dictionary with evaluation components
        """
        return {
            "material": self._evaluate_material(),
            "love_bonus": self._evaluate_love(),
            "anger_bonus": self._evaluate_anger(),
            "sad_penalty": self._evaluate_sadness(),
            "total": self.evaluate_position()
        }
    
    def get_emotion_impact(self) -> Dict[str, Dict[str, int]]:
        """
        Get impact of emotions on each side.
        
        Returns:
            Dictionary with emotional impact per side
        """
        white_love = 0
        black_love = 0
        white_anger = 0
        black_anger = 0
        white_sad = 0
        black_sad = 0
        
        processed = set()
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if not piece:
                continue
            
            if self.board.in_love(square) and square not in processed:
                partner = self.board.love_partner[square]
                if piece.color == chess.WHITE:
                    white_love += 1
                else:
                    black_love += 1
                processed.add(square)
                processed.add(partner)
            
            if self.board.is_angry(square):
                if piece.color == chess.WHITE:
                    white_anger += 1
                else:
                    black_anger += 1
            
            if self.board.is_sad(square):
                if piece.color == chess.WHITE:
                    white_sad += 1
                else:
                    black_sad += 1
        
        return {
            "white": {
                "love": white_love,
                "anger": white_anger,
                "sad": white_sad
            },
            "black": {
                "love": black_love,
                "anger": black_anger,
                "sad": black_sad
            }
        }
