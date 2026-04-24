# TODO: Why I use

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
    


class SmartAI:
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