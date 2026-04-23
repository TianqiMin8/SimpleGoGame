# TODO: Why I use

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