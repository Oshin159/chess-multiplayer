# Emotional Chess System ❤️😡😢

A modular chess system built on top of `python-chess` that adds three emotional mechanics to traditional chess:

- **Love ❤️**: Between opposite sides, prevents capture/check
- **Anger 😡**: Within same side, grants +1 movement range  
- **Sad 😢**: Love-side reaction, freezes movement

## Installation

```bash
pip install python-chess pytest
```

## Quick Start

```python
import chess
from emotional_board import EmotionalBoard

# Create emotional chess board
board = EmotionalBoard()

# Make moves (emotions form automatically)
board.push_san("e4")
board.push_san("e5")

# Check emotional states
print(board.emotion_summary())
# Output: {'love_pairs': 0, 'angry': 0, 'sad': 0}

# Get emFEN (extended FEN with emotions)
emfen = board.to_emfen()
print(emfen)
# Output: rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1

# Load from emFEN
board2 = EmotionalBoard(emfen)
```

## Emotional Mechanics

### ❤️ Love (Between Opposite Sides)

**Formation:**
- Pieces within Chebyshev distance ≤ 3
- Neither in check
- Neither already in love
- Queens cannot form love
- Kings can only love opposite-color pieces (not Kings)

**Effects:**
- Lovers cannot capture each other
- Lovers ignore each other's attack zones
- Love ends if distance > 3, either enters check, or one is captured

```python
# Check if piece is in love
if board.in_love(chess.E2):
    print("This piece is in love!")

# Get love partner
partner = board.love_partner[chess.E2]
if partner:
    print(f"Loving piece at {chess.square_name(partner)}")
```

### 😡 Anger (Within Same Side)

**Trigger:**
- When friendly piece is threatened or captured
- All allied pieces within distance ≤ 3 become angry

**Effects:**
- +1 movement range for 1 turn
- Knights unaffected
- Cannot stack

```python
# Check if piece is angry
if board.is_angry(chess.E4):
    print("This piece is angry and has extended movement!")

# Anger lasts 1 turn
board.angry_turns[chess.E4] = 1
```

### 😢 Sad (Love-Side Reaction)

**Trigger:**
- When a piece's lover is captured
- Surviving lover becomes sad

**Effects:**
- Cannot move for 1 turn
- Kings cannot become sad
- Can move only to resolve check

```python
# Check if piece is sad
if board.is_sad(chess.G2):
    print("This piece is sad and cannot move!")

# Sadness lasts 1 turn
board.sad_turns[chess.G2] = 1
```

## Advanced Usage

### emFEN (Emotional FEN)

Extended FEN format that includes emotional states:

```
<base_fen> | L: a2-b5,c4-d7 | A: e4,f7 | S: g2
```

```python
from emfen import EmFEN

# Encode board to emFEN
emfen = EmFEN.encode(board)

# Decode emFEN to board
EmFEN.decode(emfen, board)

# Validate emFEN
if EmFEN.validate(emfen):
    print("Valid emFEN!")
```

### Position Evaluation

```python
from evaluation import EmotionalEvaluator

# Create evaluator
evaluator = EmotionalEvaluator(board)

# Get total evaluation
score = evaluator.evaluate_position()
print(f"Position score: {score}")

# Get detailed breakdown
details = evaluator.get_detailed_evaluation()
print(f"Material: {details['material']}")
print(f"Love bonus: {details['love_bonus']}")
print(f"Anger bonus: {details['anger_bonus']}")
print(f"Sad penalty: {details['sad_penalty']}")

# Get emotion impact per side
impact = evaluator.get_emotion_impact()
print(f"White emotions: {impact['white']}")
print(f"Black emotions: {impact['black']}")
```

### Move Generation

```python
# Get legal moves considering emotions
legal_moves = board.generate_legal_moves()

# Filter moves for specific piece
e4_moves = board.generate_legal_moves(chess.BB_SQUARES[chess.E4])

# Check if move is legal (considers emotions)
move = chess.Move(chess.E2, chess.E4)
if move in legal_moves:
    print("Move is legal!")
```

## Configuration

```python
# Emotional constants
LOVE_DISTANCE = 3      # Max distance for love formation
LOVE_BONUS = 30        # Evaluation bonus for love
ANGER_BONUS = 10       # Evaluation bonus for anger
SAD_PENALTY = 25       # Evaluation penalty for sadness
```

## Testing

Run the comprehensive test suite:

```bash
pytest test_emotions.py -v
```

Tests cover:
- Love formation and dissolution
- Anger triggers and effects
- Sadness mechanics
- emFEN serialization
- Position evaluation
- Move generation with emotions

## Example Game

```python
# Start new game
board = EmotionalBoard()

# Make opening moves
board.push_san("e4")
board.push_san("e5")
board.push_san("Nf3")
board.push_san("Nc6")

# Update emotional states
board.update_love_states()

# Check emotions
summary = board.emotion_summary()
print(f"Love pairs: {summary['love_pairs']}")
print(f"Angry pieces: {summary['angry']}")
print(f"Sad pieces: {summary['sad']}")

# Get position evaluation
evaluator = EmotionalEvaluator(board)
score = evaluator.evaluate_position()
print(f"Position score: {score}")

# Save game state
emfen = board.to_emfen()
print(f"Game state: {emfen}")
```

## Architecture

- **EmotionalBoard**: Main class extending `chess.Board`
- **EmFEN**: Serialization/deserialization of emotional states
- **EmotionalEvaluator**: Position evaluation with emotional bonuses
- **Test Suite**: Comprehensive unit tests for all mechanics

## Contributing

The system is designed to be modular and extensible. New emotional mechanics can be added by:

1. Adding new state tracking arrays
2. Implementing formation/trigger logic
3. Updating move generation
4. Adding evaluation bonuses/penalties
5. Extending emFEN format

## License

This project extends the `python-chess` library and follows the same licensing terms.
