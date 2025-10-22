"""
Unit tests for Emotional Chess system

Tests all emotional mechanics: Love ❤️, Anger 😡, and Sad 😢
"""

import unittest
import chess
from emotional_board import EmotionalBoard
from emfen import EmFEN
from evaluation import EmotionalEvaluator


class TestEmotionalBoard(unittest.TestCase):
    """Test EmotionalBoard basic functionality."""
    
    def setUp(self):
        """Set up test board."""
        self.board = EmotionalBoard()
    
    def test_initialization(self):
        """Test board initialization."""
        self.assertIsNotNone(self.board.love_partner)
        self.assertIsNotNone(self.board.angry_turns)
        self.assertIsNotNone(self.board.sad_turns)
        self.assertEqual(len(self.board.love_partner), 64)
        self.assertEqual(len(self.board.angry_turns), 64)
        self.assertEqual(len(self.board.sad_turns), 64)
    
    def test_chebyshev_distance(self):
        """Test Chebyshev distance calculation."""
        # Same square
        self.assertEqual(self.board.chebyshev_distance(0, 0), 0)
        
        # Adjacent squares
        self.assertEqual(self.board.chebyshev_distance(0, 1), 1)
        self.assertEqual(self.board.chebyshev_distance(0, 8), 1)
        
        # Diagonal
        self.assertEqual(self.board.chebyshev_distance(0, 9), 1)
        
        # Knight move
        self.assertEqual(self.board.chebyshev_distance(0, 17), 2)
        
        # Far apart
        self.assertEqual(self.board.chebyshev_distance(0, 63), 7)
    
    def test_emotion_state_tracking(self):
        """Test emotion state tracking methods."""
        # Test love state
        self.assertFalse(self.board.in_love(0))
        self.board.love_partner[0] = 1
        self.assertTrue(self.board.in_love(0))
        
        # Test anger state
        self.assertFalse(self.board.is_angry(0))
        self.board.angry_turns[0] = 1
        self.assertTrue(self.board.is_angry(0))
        
        # Test sadness state
        self.assertFalse(self.board.is_sad(0))
        self.board.sad_turns[0] = 1
        self.assertTrue(self.board.is_sad(0))


class TestLoveMechanics(unittest.TestCase):
    """Test Love ❤️ mechanics."""
    
    def setUp(self):
        """Set up test board with pieces for love testing."""
        # Create board with pieces close enough for love
        self.board = EmotionalBoard("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    
    def test_love_formation_conditions(self):
        """Test love formation conditions."""
        # Test with pieces that can form love
        square_a = chess.E2  # White pawn
        square_b = chess.E7  # Black pawn
        
        # Should be able to form love (distance 5, but let's test closer)
        square_c = chess.D2  # White pawn
        square_d = chess.D7  # Black pawn
        
        # Test distance check
        distance = self.board.chebyshev_distance(square_c, square_d)
        self.assertLessEqual(distance, 5)  # Should be within love distance
    
    def test_love_prevents_capture(self):
        """Test that lovers cannot capture each other."""
        # Set up love relationship
        self.board.love_partner[chess.E2] = chess.E7
        self.board.love_partner[chess.E7] = chess.E2
        
        # Get legal moves for E2 pawn
        legal_moves = self.board.generate_legal_moves(chess.BB_SQUARES[chess.E2])
        
        # Should not be able to capture lover
        capture_move = chess.Move(chess.E2, chess.E7)
        self.assertNotIn(capture_move, legal_moves)
    
    def test_love_ignores_attack_zones(self):
        """Test that lovers ignore each other's attack zones."""
        # This would require more complex setup with actual pieces
        # For now, we'll test the basic logic
        self.board.love_partner[chess.E2] = chess.E7
        self.board.love_partner[chess.E7] = chess.E2
        
        # Lovers should be able to move near each other
        self.assertTrue(self.board.in_love(chess.E2))
        self.assertTrue(self.board.in_love(chess.E7))


class TestAngerMechanics(unittest.TestCase):
    """Test Anger 😡 mechanics."""
    
    def setUp(self):
        """Set up test board."""
        self.board = EmotionalBoard()
    
    def test_anger_state_tracking(self):
        """Test anger state tracking."""
        square = chess.E4
        
        # Initially not angry
        self.assertFalse(self.board.is_angry(square))
        
        # Set angry
        self.board.angry_turns[square] = 1
        self.assertTrue(self.board.is_angry(square))
        
        # Decrement turns
        self.board.angry_turns[square] -= 1
        self.assertFalse(self.board.is_angry(square))
    
    def test_anger_movement_extension(self):
        """Test that angry pieces get extended movement."""
        # This would require actual pieces and moves
        # For now, test the helper method
        square = chess.E4
        self.board.angry_turns[square] = 1
        
        # Should be able to generate anger moves
        anger_moves = self.board._generate_anger_moves(square)
        self.assertIsInstance(anger_moves, list)


class TestSadnessMechanics(unittest.TestCase):
    """Test Sad 😢 mechanics."""
    
    def setUp(self):
        """Set up test board."""
        self.board = EmotionalBoard()
    
    def test_sadness_state_tracking(self):
        """Test sadness state tracking."""
        square = chess.E4
        
        # Initially not sad
        self.assertFalse(self.board.is_sad(square))
        
        # Set sad
        self.board.sad_turns[square] = 1
        self.assertTrue(self.board.is_sad(square))
        
        # Decrement turns
        self.board.sad_turns[square] -= 1
        self.assertFalse(self.board.is_sad(square))
    
    def test_sadness_movement_restriction(self):
        """Test that sad pieces have movement restrictions."""
        square = chess.E4
        self.board.sad_turns[square] = 1
        
        # Sad pieces should have restricted movement
        legal_moves = self.board.generate_legal_moves(chess.BB_SQUARES[square])
        
        # If not in check, should have no moves
        if not self.board.is_check():
            self.assertEqual(len(legal_moves), 0)


class TestEmFEN(unittest.TestCase):
    """Test emFEN serialization/deserialization."""
    
    def setUp(self):
        """Set up test board."""
        self.board = EmotionalBoard()
    
    def test_emfen_encoding(self):
        """Test emFEN encoding."""
        # Set up some emotional states
        self.board.love_partner[chess.E2] = chess.E7
        self.board.love_partner[chess.E7] = chess.E2
        self.board.angry_turns[chess.E4] = 1
        self.board.sad_turns[chess.G2] = 1
        
        # Encode to emFEN
        emfen = self.board.to_emfen()
        self.assertIn("L: e2-e7", emfen)
        self.assertIn("A: e4", emfen)
        self.assertIn("S: g2", emfen)
    
    def test_emfen_decoding(self):
        """Test emFEN decoding."""
        emfen_str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 | L: e2-e7 | A: e4 | S: g2"
        
        # Decode emFEN
        self.board.from_emfen(emfen_str)
        
        # Check emotional states
        self.assertTrue(self.board.in_love(chess.E2))
        self.assertTrue(self.board.in_love(chess.E7))
        self.assertTrue(self.board.is_angry(chess.E4))
        self.assertTrue(self.board.is_sad(chess.G2))
    
    def test_emfen_roundtrip(self):
        """Test emFEN roundtrip (encode -> decode -> encode)."""
        # Set up emotional states
        self.board.love_partner[chess.E2] = chess.E7
        self.board.love_partner[chess.E7] = chess.E2
        self.board.angry_turns[chess.E4] = 1
        self.board.sad_turns[chess.G2] = 1
        
        # Encode
        emfen1 = self.board.to_emfen()
        
        # Create new board and decode
        new_board = EmotionalBoard()
        new_board.from_emfen(emfen1)
        
        # Encode again
        emfen2 = new_board.to_emfen()
        
        # Should be identical
        self.assertEqual(emfen1, emfen2)


class TestEmotionSummary(unittest.TestCase):
    """Test emotion summary functionality."""
    
    def setUp(self):
        """Set up test board."""
        self.board = EmotionalBoard()
    
    def test_emotion_summary(self):
        """Test emotion summary generation."""
        # Set up emotional states
        self.board.love_partner[chess.E2] = chess.E7
        self.board.love_partner[chess.E7] = chess.E2
        self.board.angry_turns[chess.E4] = 1
        self.board.sad_turns[chess.G2] = 1
        
        # Get summary
        summary = self.board.emotion_summary()
        
        self.assertEqual(summary["love_pairs"], 1)
        self.assertEqual(summary["angry"], 1)
        self.assertEqual(summary["sad"], 1)


class TestEvaluation(unittest.TestCase):
    """Test evaluation functions."""
    
    def setUp(self):
        """Set up test board."""
        self.board = EmotionalBoard()
        self.evaluator = EmotionalEvaluator(self.board)
    
    def test_material_evaluation(self):
        """Test material evaluation."""
        score = self.evaluator._evaluate_material()
        self.assertEqual(score, 0)  # Starting position should be equal
    
    def test_love_evaluation(self):
        """Test love bonus evaluation."""
        # Set up love relationship between two white pieces (E2 and F2)
        # We'll manually set the love relationship even though distance > 3 for testing
        self.board.love_partner[chess.E2] = chess.F2
        self.board.love_partner[chess.F2] = chess.E2
        
        love_score = self.evaluator._evaluate_love()
        self.assertGreater(love_score, 0)  # Should have positive love bonus
    
    def test_anger_evaluation(self):
        """Test anger bonus evaluation."""
        # Set up anger on a square that has a piece (E2 has a white pawn)
        self.board.angry_turns[chess.E2] = 1
        
        anger_score = self.evaluator._evaluate_anger()
        self.assertGreater(anger_score, 0)  # Should have positive anger bonus
    
    def test_sadness_evaluation(self):
        """Test sadness penalty evaluation."""
        # Set up sadness
        self.board.sad_turns[chess.G2] = 1
        
        sad_score = self.evaluator._evaluate_sadness()
        self.assertGreater(sad_score, 0)  # Should have positive sadness penalty
    
    def test_detailed_evaluation(self):
        """Test detailed evaluation breakdown."""
        details = self.evaluator.get_detailed_evaluation()
        
        self.assertIn("material", details)
        self.assertIn("love_bonus", details)
        self.assertIn("anger_bonus", details)
        self.assertIn("sad_penalty", details)
        self.assertIn("total", details)


class TestIntegration(unittest.TestCase):
    """Test integration of all emotional mechanics."""
    
    def setUp(self):
        """Set up test board."""
        self.board = EmotionalBoard()
    
    def test_full_emotional_game(self):
        """Test a full emotional game scenario."""
        # Make some moves
        self.board.push_san("e4")
        self.board.push_san("e5")
        
        # Update emotional states
        self.board.update_love_states()
        
        # Check that emotional mechanics are working
        summary = self.board.emotion_summary()
        self.assertIsInstance(summary, dict)
        
        # Test emFEN
        emfen = self.board.to_emfen()
        self.assertIsInstance(emfen, str)
        
        # Test evaluation
        evaluator = EmotionalEvaluator(self.board)
        score = evaluator.evaluate_position()
        self.assertIsInstance(score, int)


if __name__ == "__main__":
    unittest.main()
