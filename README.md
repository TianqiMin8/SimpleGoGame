# Simple Go Game (9x9)

A Python-based implementation of the game of Go with a heuristic-driven AI opponent.

## How to Run
1. **Ensure Python 3.13 is installed.**
2. **Install Dependencies:**
    This project uses `pygame` for the graphical interface. Run:
    ```bash
    pip install pygame

3. Start the Game:
    From the root directory, execute:
    ```bash
    python ui.py

## Game Features
Game Modes: Supports Human vs. Human (PVP) and Human vs. AI (PVE).

AI Opponent: A heuristic-based AI that prioritizes center control and tactical captures (Logic details in ai.py).

Interactive UI: - Real-time scoring display.

Transparent "Liberties" visualization for better tactical awareness.

Undo and Reset functionality.

## File Structure
ui.py: The main entry point. Handles the GUI, menu states, and user input.

ai.py: Contains the Heuristic class and move-evaluation logic.

core_game.py: The backend Go engine (rules, stone capturing, and board state).

test_game.py： Simple test that enable game can run.

scoring.py:  Calculating and updating the scores for both Sides. 

Note: Detailed analysis of AI strategy and design challenges can be found in the header comments of ai.py.