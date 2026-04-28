
"""
================================================================================
AI STRATEGY AND DESIGN ANALYSIS
================================================================================

a) AI Strategy & Rationale:
The AI implements a Heuristic-based Greedy Search. For a 9x9 board, I prioritized 
immediate tactical advantage over complex search trees to ensure high performance. 
The strategy is defined by:
1. Positional Bias: It rewards moves closer to the board center (4, 4) using 
   Manhattan Distance. This ensures the AI develops central influence early.
2. Capture Reward: Using the _simulate_move function, the AI identifies how 
   many stones a move will capture. A high weight (*10) is assigned to these 
   moves, making the AI tactically aggressive.
3. Rule Adherence: Illegal moves (e.g., suicide or Ko) are assigned a -100 
   penalty via get_capture_count, forcing the AI to strictly follow Go rules.

b) Design Decisions & Challenges:
- Tactical Weighting: A key decision was weighting capturing (10 points) higher 
  than center control (max 4 points). This ensures the AI prioritizes stone 
  survival and material gain over simple positioning.
- Efficiency: Instead of deep recursion, I used a flat loop through legal_moves. 
  This keeps the AI's response time nearly instantaneous during the UI's 
  60 FPS refresh cycle.
- Robustness: The use of random.choice() as a default best_move prevents the 
  AI from stalling if multiple moves return the same heuristic score.
================================================================================
"""


import copy
import random

class RandomAI:
    def __init__(self, color):
        self.color = color

    def select_move(self, game):
        moves = game.get_legal_moves()
        # print("legal moves:", len(moves))
        
        if not moves:
            return None  # pass

        return random.choice(moves)
    


class Heuristic:
    def __init__(self, color):
        self.color = color

    def select_move(self, game):
        legal_moves = game.get_legal_moves()
        if not legal_moves: return None

        best_score = -999
        best_move = random.choice(legal_moves)

        for move in legal_moves:
            score = self.evaluate_move(game, move)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def evaluate_move(self, game, move):
        r, c = move
        score = 0
        
        # 1. Basic: center
        dist_to_center = abs(r - 4) + abs(c - 4)
        score += (8 - dist_to_center) * 0.5 

        # 2. simulate one step to check result
        original_grid = [row[:] for row in game.board.grid]
        captured_count = self.get_capture_count(game, move)
        score += captured_count * 10  # high reward for capture

        return score

    def get_capture_count(self, game, move):
        # Check how many stones can get captured
        legal, captured, _ = game._simulate_move(move[0], move[1], self.color)
        return len(captured) if legal else -100